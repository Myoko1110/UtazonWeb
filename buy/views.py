import asyncio
import datetime
import json
from decimal import Decimal, ROUND_DOWN, ROUND_UP, getcontext

from django.http import Http404
from django.shortcuts import redirect, render

import bot
import config.DBManager
import config.functions
import config.settings as settings
import util

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
            user_cart_id = config.DBManager.get_user_cart(info.mc_uuid)
            buy_now = False

        # アイテム情報を取得
        total_point = 0
        item_total = 0
        user_cart_number = 0
        user_cart = []
        for i in user_cart_id:
            result = config.DBManager.get_item(i[0])

            # item_idのレコードを取得
            item_info = list(result)

            item_info[3] = json.loads(item_info[3])

            sale = util.ItemHelper.get_sale(i[0], item_info[2])
            item_price = sale.item_price

            point = util.ItemHelper.calc_point(item_price)
            item_info.append(point)

            total_point += int(Decimal(str(point)) * Decimal(str(i[1])))

            item_info.append(f"{item_price:,.2f}")
            item_info.append(i[1])
            item_info.append(sale)

            total_item_price = Decimal(f"{item_price}") * Decimal(f"{i[1]}")
            item_total += total_item_price
            user_cart_number += i[1]

            user_cart.append(item_info)

        player_balance = util.VaultHelper.get_balance(info.mc_uuid)

        # 小数第2位まで切り上げ
        if player_balance:
            player_balance = Decimal(str(player_balance)).quantize(Decimal(".01"),
                                                                   rounding=ROUND_UP)
            after_balance_float = Decimal(f"{player_balance}") - Decimal(f"{item_total}")
            after_balance = f"{after_balance_float:,.2f}"
        else:
            after_balance = None

        now = datetime.datetime.now()
        if now > datetime.datetime.strptime("13:00:00", "%H:%M:%S"):
            rand_time = now + datetime.timedelta(days=2)
        else:
            rand_time = now + datetime.timedelta(days=1)

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
            "rand_time": rand_time,
            "per_point": per_point,
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
        array = []
        amount: Decimal = Decimal("0")
        order_item_list = json.loads(order_item)
        for i in order_item_list:
            price = config.DBManager.get_item(i[0])[2]

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

            config.DBManager.withdraw_user_point(mc_uuid, point)

            # 合計金額からポイント引く
            amount_float = float(amount - Decimal(str(point)) * per_point)

        else:
            amount_float = float(amount)

        # オーダーをdbに保存
        order = config.DBManager.add_order(order_item, mc_uuid)

        # 出金
        if point:
            reason = ", ".join(
                array) + f", ポイント使用({point}pt:{Decimal(str(point)) * per_point})(OrderID: {order[0]})"
        else:
            reason = ", ".join(array) + f"(OrderID: {order[0]})"
        withdraw_player = util.VaultHelper.withdraw_player(mc_uuid, amount_float, reason)
        if not withdraw_player:
            raise Exception("Socketサーバーに接続できない状態で注文が確定されようとしました")

        # 履歴に追加
        history = config.DBManager.get_user_history(mc_uuid)
        history_obj = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "delivery_time": order[1].strftime("%Y-%m-%d %H:%M:%S"),
            "amount": amount_float,
            "order_id": order[0],
            "order_item": order_item_list,
            "cancel": False,
            "point": point,
        }
        history.append(history_obj)
        config.DBManager.update_user_history(mc_uuid, json.dumps(history))

        # カートから削除
        if request.GET.get("buynow") == "False":
            config.DBManager.update_user_cart([], mc_uuid)

        # アイテム情報取得
        order_item_obj = []
        total_point = 0
        for i in order_item_list:
            result = config.DBManager.get_item(i[0])

            # item_idのレコードを取得
            item_info = list(result)

            item_info[3] = json.loads(item_info[3])

            item_price = item_info[2]

            point = util.ItemHelper.calc_point(item_price)
            item_info.append(point)

            total_point += int(Decimal(str(point)) * Decimal(str(i[1])))

            sale = util.ItemHelper.get_sale(i[0], item_price)
            item_info.append(f"{sale.item_price:,.2f}")

            item_info.append(i[1])

            order_item_obj.append(item_info)

        # ポイント付与
        config.DBManager.deposit_user_point(mc_uuid, total_point)

        # DM送信
        asyncio.run_coroutine_threadsafe(
            bot.send_order_confirm(info.discord_id, order[0], order_item_obj, order[1]),
            bot.client.loop
        )

        context = {
            "session": is_session,
            "info": info,
            "order_id": order[0],
            "order_time": order[1],
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

        user_history = config.DBManager.get_user_history(mc_uuid)

        for i in user_history:
            if i["order_id"] == order_id:
                deposit_price = Decimal("100") - Decimal(str(settings.CANCELLATION_FEE))

                i["cancel"] = True
                amount = i["amount"]
                amount_twenty_per = Decimal(deposit_price / Decimal("100")) * Decimal(str(amount))
                amount_twenty_per = float(
                    amount_twenty_per.quantize(Decimal(".01"), rounding=ROUND_DOWN))

                reason = f"注文のキャンセル(OrderID: {order_id})(入金額: {amount}の{deposit_price}%(キャンセル料{settings.CANCELLATION_FEE}%))"
                deposit_player = util.VaultHelper.deposit_player(mc_uuid, amount_twenty_per, reason)
                if not deposit_player:
                    return redirect("/history/?error=true")

        order_item = json.loads(config.DBManager.get_order(order_id)[1])

        item_list = []
        for i in order_item:
            item_id = i[0]
            item_obj = config.DBManager.get_item(item_id)
            item_list.append(item_obj)

        config.DBManager.delete_order(order_id)

        config.DBManager.update_user_history(mc_uuid, json.dumps(user_history))
        asyncio.run_coroutine_threadsafe(
            bot.send_order_cancel(info.discord_id, order_id, item_list),
            bot.client.loop)

        return redirect(f"/history/#{order_id}")
    return redirect(f"/history/")
