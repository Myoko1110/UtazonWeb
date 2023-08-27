import asyncio
import datetime
import json
import random
from decimal import Decimal, ROUND_DOWN, ROUND_UP, getcontext

from django.http import Http404
from django.shortcuts import redirect, render

import bot
import util
from config import settings

getcontext().prec = 10
per_point = Decimal(settings.PER_POINT)
point_return = Decimal(settings.POINT_RETURN)


def buy(request):
    is_session = util.SessionHelper.is_session(request)
    if is_session.valid:
        info = util.UserHelper.get_info.from_session(request)

        item_id = request.GET.get("item")
        if item_id:
            user_cart_id = json.loads(item_id)
            buy_now = True
        else:
            user_cart_id = util.DatabaseHelper.get_user_cart(info.mc_uuid)
            buy_now = False

        # アイテム情報とトータルを取得
        items_info = util.ItemHelper.get_item.cart_list(user_cart_id)
        user_cart = items_info.item_list
        total_point = items_info.total_point
        item_total = items_info.total_amount
        user_cart_number = items_info.total_qty

        player_balance = util.VaultHelper.get_balance(info.mc_uuid)

        # 小数第2位まで切り上げ
        if player_balance:
            player_balance = Decimal(str(player_balance)).quantize(Decimal(".01"),
                                                                   rounding=ROUND_UP)
            after_balance_float = Decimal(f"{player_balance}") - Decimal(f"{item_total}")
            after_balance = f"{after_balance_float:,.2f}"
        else:
            after_balance = None

        # お届け日
        delivery_time = util.ItemHelper.calc_delivery_time()

        context = {
            "session": is_session,
            "info": info,
            "user_cart": user_cart,
            "user_cart_number": user_cart_number,
            "user_cart_id": user_cart_id,
            "item_total": f"{item_total:,.2f}",
            "player_balance": f"{player_balance:,.2f}",
            "player_balance_float": player_balance,
            "item_total_float": f"{float(item_total):,.2f}",
            "after_balance": after_balance,
            "buy_able": player_balance >= float(item_total),
            "buy_now": buy_now,
            "rand_time": delivery_time,
            "per_point": per_point,
            "point_return": point_return,
            "total_point_format": f"{total_point:,}",
            "total_point": total_point,
            "categories": util.ItemHelper.get_category.all(),
            "money_unit": settings.MONEY_UNIT,
        }
        return render(request, "buy.html", context=context)

    else:
        # 未ログイン処理
        return redirect("/")


def buy_confirm(request):
    if not request.GET.get("items"):
        raise Http404

    is_session = util.SessionHelper.is_session(request)
    if is_session.valid:

        info = util.UserHelper.get_info.from_session(request)
        mc_uuid = info.mc_uuid

        # アイテム処理系
        order_item = request.GET.get("items")

        # 合計金額を算出
        array = []
        amount = Decimal("0")
        order_item_list = json.loads(order_item)
        for i in order_item_list:
            price = util.DatabaseHelper.get_item(i[0])["price"]

            item_dict = f"{i[0]}({i[1]}個:{price})"
            array.append(item_dict)

            amount = amount + Decimal(str(price)) * Decimal(str(i[1]))

        # ポイント関係
        point = request.GET.get("point")
        if point:
            if not float(point).is_integer():
                raise Exception("ポイントが整数値ではありません")

            point = int(point)
            if not amount >= Decimal(str(point)) * per_point:
                raise Exception("ポイントが請求額を超えています")

            util.DatabaseHelper.withdraw_user_point(mc_uuid, point)

            # 合計金額からポイント引く
            amount_float = float(amount - Decimal(str(point)) * per_point)

        else:
            amount_float = float(amount)

        # お届け時間を計算
        now = datetime.datetime.now().replace(microsecond=0)
        if now > datetime.datetime.strptime("13:00:00", "%H:%M:%S"):
            delivery_time = (now.replace(hour=random.randint(8, 18), minute=random.randint(1, 59),
                                         second=0, microsecond=0)
                             + datetime.timedelta(days=2))
        else:
            delivery_time = (now.replace(hour=random.randint(8, 18), minute=random.randint(1, 59),
                                         second=0, microsecond=0)
                             + datetime.timedelta(days=1))
        order_id = f"""U{str(random.randint(0, 999)).zfill(3)}-
                        {str(random.randint(0, 999999)).zfill(6)}-
                        {str(random.randint(0, 999999)).zfill(6)}"""

        # 出金
        if point:
            reason = (", ".join(array) +
                      f", ポイント使用({point}pt:{Decimal(str(point)) * per_point})(OrderID: {order_id})")
        else:
            reason = ", ".join(array) + f"(OrderID: {order_id})"
        withdraw_player = util.VaultHelper.withdraw_player(mc_uuid, amount_float, reason)

        # サーバーオフライン処理
        if not withdraw_player:
            raise Exception("Socketサーバーに接続できない状態で注文が確定されようとしました")

        # オーダーをdbに保存
        util.DatabaseHelper.add_order(mc_uuid, order_item, delivery_time, order_id, amount_float)

        # カートから削除
        if request.GET.get("buynow") == "False":
            util.DatabaseHelper.update_user_cart([], mc_uuid)

        # アイテム情報取得
        order_item_list = util.ItemHelper.get_item.cart_list(order_item_list)
        order_item_obj = order_item_list.item_list
        total_point = order_item_list.total_point

        # ポイント付与
        util.DatabaseHelper.deposit_user_point(mc_uuid, total_point)

        # DM送信
        asyncio.run_coroutine_threadsafe(
            bot.send_order_confirm(info.discord_id, order_id, order_item_obj, delivery_time),
            bot.client.loop
        )

        context = {
            "session": is_session,
            "info": info,
            "order_id": order_id,
            "order_time": delivery_time,
            "order_item_obj": order_item_obj,
            "categories": util.ItemHelper.get_category.all(),
            "money_unit": settings.MONEY_UNIT,
        }

        return render(request, "buy-confirm.html", context=context)

    else:
        # 未ログイン処理
        return redirect("/login")


def buy_cancel(request):
    is_session = util.SessionHelper.is_session(request)
    if is_session.valid:
        info = util.UserHelper.get_info.from_session(request)
        mc_uuid = info.mc_uuid
        order_id = request.GET.get("id")

        user_history = util.DatabaseHelper.get_user_history(mc_uuid)

        for i in user_history:
            if i["order_id"] == order_id:
                deposit_price = Decimal("100") - Decimal(str(settings.CANCELLATION_FEE))

                i["cancel"] = True
                amount = i["amount"]
                amount_twenty_per = Decimal(deposit_price / Decimal("100")) * Decimal(str(amount))
                amount_twenty_per = float(
                    amount_twenty_per.quantize(Decimal(".01"), rounding=ROUND_DOWN))

                reason = (f"注文のキャンセル(OrderID: {order_id})" +
                          "(入金額: {amount}の{deposit_price}%(キャンセル料{settings.CANCELLATION_FEE}%))")
                deposit_player = util.VaultHelper.deposit_player(mc_uuid, amount_twenty_per, reason)
                if not deposit_player:
                    return redirect("/history/?error=true")

        order_item = json.loads(util.DatabaseHelper.get_order(order_id)[1])

        item_list = []
        for i in order_item:
            item_id = i[0]
            item_obj = util.DatabaseHelper.get_item(item_id)
            item_list.append(item_obj)

        util.DatabaseHelper.delete_order(order_id)

        util.DatabaseHelper.update_user_history(mc_uuid, json.dumps(user_history))
        asyncio.run_coroutine_threadsafe(
            bot.send_order_cancel(info.discord_id, order_id, item_list),
            bot.client.loop)

        return redirect(f"/history/#{order_id}")
    return redirect(f"/history/")
