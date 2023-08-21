import asyncio
import datetime
import json
from decimal import Decimal, getcontext, ROUND_UP, ROUND_DOWN

from django.shortcuts import redirect, render
from django.http import Http404

import bot
from item import views
import config.functions
import config.DBManager
import config.VaultManager
import config.settings as settings

getcontext().prec = 10
per_point = Decimal(settings.PER_POINT)
point_return = Decimal(settings.POINT_RETURN)


def buy(request):
    is_session = config.functions.is_session(request)
    if is_session.valid:
        info = config.functions.get_user_info.from_session(request).all()

        item_id = request.GET.get("item")
        if item_id:
            user_cart_id = json.loads(item_id)
            buy_now = True
        else:
            user_cart_id = config.DBManager.get_user_cart(info["mc_uuid"])
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

            item_price = item_info[2]

            point = int(Decimal(str(item_price)) * point_return)
            item_info.append(point)

            total_point += int(Decimal(str(point)) * Decimal(str(i[1])))

            sale_id = config.DBManager.get_id_from_item(i[0])
            item_sale = config.DBManager.get_item_sale(sale_id)
            if item_sale and item_sale[2]:
                if views.calc_status_per(item_sale[4], item_sale[5]) != 0.0 or views.calc_status_per(item_sale[4],
                                                                                         item_sale[5]) != 100.0:
                    sale = {"status": True, "discount_rate": item_sale[3]}
                    item_price = Decimal(str(item_price)) * (Decimal(str(100 - item_sale[3])) / Decimal("100"))
                    item_price = item_price.quantize(Decimal(".01"), rounding=ROUND_UP)
                else:
                    sale = {"status": False}
            else:
                sale = {"status": False}

            item_info.append(f"{item_price:,.2f}")
            item_info.append(i[1])
            item_info.append(sale)

            item_price = Decimal(f"{item_price}") * Decimal(f"{i[1]}")
            item_total += item_price
            user_cart_number += i[1]

            user_cart.append(item_info)

        player_balance = config.VaultManager.get_balance(info["mc_uuid"])

        # 小数第2位まで切り上げ
        if player_balance:
            player_balance = Decimal(f"{player_balance}").quantize(Decimal(".01"), rounding=ROUND_UP)
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
            "categories": config.functions.get_categories(),
            "money_unit": settings.MONEY_UNIT,
        }
        return render(request, "buy.html", context=context)

    else:
        # 未ログイン処理
        return redirect("/")


def buy_confirm(request):
    if not request.GET.get("items"):
        raise Http404

    is_session = config.functions.is_session(request)
    if is_session.valid:

        info = config.functions.get_user_info.from_session(request).all()
        mc_uuid = info["mc_uuid"]

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
            reason = ", ".join(array) + f", ポイント使用({point}pt:{Decimal(str(point)) * per_point})(OrderID: {order[0]})"
        else:
            reason = ", ".join(array) + f"(OrderID: {order[0]})"
        config.VaultManager.withdraw_player(mc_uuid, amount_float, reason)

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

            point = int(Decimal(str(item_price)) * point_return)
            item_info.append(point)

            total_point += int(Decimal(str(point)) * Decimal(str(i[1])))

            sale_id = config.DBManager.get_id_from_item(i[0])
            item_sale = config.DBManager.get_item_sale(sale_id)
            if item_sale and item_sale[2]:
                if views.calc_status_per(item_sale[4], item_sale[5]) != 0.0 or views.calc_status_per(item_sale[4],
                                                                                         item_sale[5]) != 100.0:
                    item_price = Decimal(str(item_price)) * (Decimal(str(100 - item_sale[3])) / Decimal("100"))
                    item_price = item_price.quantize(Decimal(".01"), rounding=ROUND_UP)

            item_info.append(f"{item_price:,.2f}")
            item_info.append(i[1])

            order_item_obj.append(item_info)

        # ポイント付与
        config.DBManager.deposit_user_point(mc_uuid, total_point)

        # DM送信
        asyncio.run_coroutine_threadsafe(bot.send_order_confirm(info["discord_id"], order[0], order_item_obj, order[1]),
                                         bot.client.loop)

        context = {
            "session": is_session,
            "info": info,
            "order_id": order[0],
            "order_time": order[1],
            "order_item_obj": order_item_obj,
            "categories": config.functions.get_categories(),
            "money_unit": settings.MONEY_UNIT,
        }

        return render(request, "buy-confirm.html", context=context)

    else:
        # 未ログイン処理
        return redirect("/login")


def buy_cancel(request):
    is_session = config.functions.is_session(request)
    if is_session.valid:
        info = config.functions.get_user_info.from_session(request).all()
        mc_uuid = info["mc_uuid"]
        order_id = request.GET.get("id")

        order_item = json.loads(config.DBManager.get_order(order_id)[1])

        item_list = []
        for i in order_item:
            item_id = i[0]
            item_obj = config.DBManager.get_item(item_id)
            item_list.append(item_obj)

        config.DBManager.delete_order(order_id)
        user_history = config.DBManager.get_user_history(mc_uuid)

        for i in user_history:
            if i["order_id"] == order_id:
                i["cancel"] = True
                amount = i["amount"]
                amount_twenty_per = Decimal("0.8") * Decimal(str(amount))
                amount_twenty_per = float(amount_twenty_per.quantize(Decimal(".01"), rounding=ROUND_DOWN))

                reason = f"注文のキャンセル(OrderID: {order_id})(入金額: {amount}の80%(キャンセル料20%))"
                config.VaultManager.deposit_player(mc_uuid, amount_twenty_per, reason)

        config.DBManager.update_user_history(mc_uuid, json.dumps(user_history))
        asyncio.run_coroutine_threadsafe(bot.send_order_cancel(info["discord_id"], order_id, item_list),
                                         bot.client.loop)

    return redirect("/history")
