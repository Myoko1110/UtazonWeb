import asyncio
import datetime
import json
import random
from decimal import Decimal, ROUND_DOWN, getcontext

from django.http import Http404
from django.shortcuts import redirect, render

import bot
import util
from config import settings

getcontext().prec = 10
per_point = Decimal(settings.PER_POINT)
point_return = Decimal(settings.POINT_RETURN)

deposit_rate = Decimal("100") - Decimal(str(settings.CANCELLATION_FEE))


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

        # ユーザー残高取得
        player_balance = util.SocketHelper.get_balance(info.mc_uuid)

        # 小数第2位まで切り上げ
        if player_balance:

            # 購入後の残高計算
            after_balance_float = player_balance - Decimal(str(item_total))
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
            "item_total": item_total,
            "item_total_format": f"{item_total:,.2f}",
            "player_balance": f"{player_balance:,.2f}",
            "player_balance_float": player_balance,
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
        order_item = json.loads(order_item)
        order_item_obj = util.ItemHelper.get_item.cart_list(order_item)
        amount = order_item_obj.total_amount
        order_item_list = order_item_obj.item_list

        # お届け時間を計算
        delivery_time = util.ItemHelper.calc_delivery_time_perfect()

        # オーダーIDを作成
        order_id = util.ItemHelper.create_order_id()

        # 出金するときの理由用にアイテム情報をまとめる
        reason_list = []
        for i in order_item_list:
            item_dict = f"{i['item_id']}({i['qty']}個:{i['price']})"
            reason_list.append(item_dict)

        # ポイント関係
        point = request.GET.get("point")
        if float(point) != 0.0:
            if not float(point).is_integer():
                raise Exception("ポイントが整数値ではありません")

            point = int(point)
            if not Decimal(str(amount)) >= Decimal(str(point)) * per_point:
                raise Exception("ポイントが請求額を超えています")

            # ポイントを引く
            util.DatabaseHelper.withdraw_user_point(mc_uuid, point)

            # 合計金額からポイント引く
            amount_float = float(amount - Decimal(str(point)) * per_point)

            # 理由を作成
            reason = (", ".join(reason_list) +
                      f", ポイント使用({point}pt:{Decimal(str(point)) * per_point})(注文番号: {order_id})")

        else:
            amount_float = float(amount)

            # 理由を作成
            reason = ", ".join(reason_list) + f"(注文番号: {order_id})"

        # 在庫を減らす
        for i in order_item_list:
            util.DatabaseHelper.reduce_stock(i["item_id"], i["qty"])
            util.DatabaseHelper.add_revenues(mc_uuid, i["item_id"], i["price"], i["qty"],
                                             amount_float, i["mc_uuid"])
            util.DatabaseHelper.increase_purchases(i["item_id"])

            stock = util.DatabaseHelper.get_item_stock(i["item_id"])
            if 15 in range(stock, stock + i["qty"]):
                asyncio.run_coroutine_threadsafe(
                    bot.send_stock(info.discord_id, i),
                    bot.client.loop
                )

        # 出金
        withdraw_player = util.SocketHelper.withdraw_player(mc_uuid, amount_float,
                                                            "ウェブショップ『Utazon』で購入", reason)

        # サーバーオフライン処理
        if not withdraw_player:
            raise Exception("Socketサーバーに接続できない状態で注文が確定されようとしました")

        # オーダーをdbに保存
        util.DatabaseHelper.add_order(
            mc_uuid, order_item, delivery_time, order_id, amount_float, point
        )

        # カートから削除
        if request.GET.get("buynow") == "False":
            util.DatabaseHelper.update_user_cart([], mc_uuid)

        # ポイント付与
        util.DatabaseHelper.deposit_user_point(mc_uuid, order_item_obj.total_point)

        # DM送信
        asyncio.run_coroutine_threadsafe(
            bot.send_order_confirm(info.discord_id, order_id, order_item_list, delivery_time),
            bot.client.loop
        )

        context = {
            "session": is_session,
            "info": info,
            "order_id": order_id,
            "order_time": delivery_time,
            "order_item_obj": order_item_list,
            "categories": util.ItemHelper.get_category.all(),
            "money_unit": settings.MONEY_UNIT,
        }

        return render(request, "buy-confirm.html", context=context)

    else:
        # 未ログイン処理
        return redirect("/login/")


def buy_cancel(request):
    is_session = util.SessionHelper.is_session(request)
    if is_session.valid:
        info = util.UserHelper.get_info.from_session(request)
        mc_uuid = info.mc_uuid
        order_id = request.GET.get("id")

        # オーダーを取得
        order_obj = util.DatabaseHelper.get_order(order_id)
        amount = order_obj["amount"]

        # 入金する価格を計算
        deposit_price = (deposit_rate / Decimal("100")) * Decimal(str(amount))
        deposit_price = float(deposit_price.quantize(Decimal(".01"), rounding=ROUND_DOWN))

        # 理由作成し、入金
        reason = (f"注文番号: {order_id}" +
                  f"(入金額: {amount}の{deposit_rate}%(キャンセル料{settings.CANCELLATION_FEE}%)")
        deposit_player = util.SocketHelper.deposit_player(mc_uuid, deposit_price,
                                                          "ウェブショップ『Utazon』からのキャンセルに伴う返金", reason)

        # エラーが出たらリダイレクト
        if not deposit_player:
            return redirect("/history/?error=true")

        # キャンセルしたオーダーのアイテムを取得
        order_item = util.DatabaseHelper.get_order(order_id)["order_item"]
        order_item = json.loads(order_item)
        item_list = util.ItemHelper.get_item.cart_list(order_item).item_list

        # 在庫を戻す
        for i in item_list:
            util.DatabaseHelper.increase_stock(i["item_id"], i["qty"])

        # DM送信
        asyncio.run_coroutine_threadsafe(
            bot.send_order_cancel(info.discord_id, order_id, item_list),
            bot.client.loop)

        # オーダー削除
        util.DatabaseHelper.cancel_order(order_id)

        return redirect(f"/history/#{order_id}")

    else:
        return redirect(f"/history/")


def buy_redelivery(request):
    is_session = util.SessionHelper.is_session(request)
    if is_session.valid:
        info = util.UserHelper.get_info.from_session(request)
        mc_uuid = info.mc_uuid
        order_id = request.GET.get("id")

        order_obj = util.DatabaseHelper.get_order(order_id)
        if mc_uuid != order_obj["mc_uuid"]:
            raise Http404

        # DM送信
        asyncio.run_coroutine_threadsafe(
            bot.send_redelivery(info.discord_id, order_id),
            bot.client.loop)

        now = datetime.datetime.now()
        delivery_time = now + datetime.timedelta(hours=random.randint(1, 4),
                                                 minutes=random.randint(0, 59),
                                                 seconds=0,
                                                 microseconds=0)

        # 再配達を追加
        util.DatabaseHelper.redelivery_order(order_id, delivery_time)

        return redirect(f"/history/#{order_id}")

    else:
        return redirect(f"/history/")
