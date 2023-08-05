import datetime
import json

from django.shortcuts import redirect, render
from django.http import Http404
from decimal import Decimal, getcontext, ROUND_UP

import config.functions
import config.DBManager
import config.VaultManager

getcontext().prec = 10


def buy(request):
    is_session = config.functions.is_session(request)
    if is_session.valid:
        info = config.functions.get_user_info.from_session(request).all()

        item_id = request.GET.get("item")
        if item_id:
            user_cart_id = json.loads(item_id)
            buy_now = True
        else:
            user_cart_id = config.DBManager.get_utazon_user_cart(info["mc_uuid"])
            buy_now = False

        # アイテム情報を取得
        user_cart = []
        for i in user_cart_id:
            result = config.DBManager.get_item(i[0])

            # item_idのレコードを取得
            item_info = list(result)

            item_info[3] = json.loads(item_info[3])

            item_price = item_info[2]

            item_info.append(int(item_price / 10))
            item_info.append(f"{item_price:,.2f}")
            item_info.append(i[1])

            user_cart.append(item_info)

        # 請求額算出
        item_total = 0
        user_cart_number = 0
        for i in range(len(user_cart)):
            item_price = Decimal(f"{user_cart[i][2]}") * Decimal(f"{user_cart[i][10]}")
            item_total += item_price
            user_cart_number += user_cart[i][10]

        player_balance = config.VaultManager.get_balance(info["mc_uuid"])

        # 小数第2位まで切り上げ
        if player_balance:
            player_balance = Decimal(f"{player_balance}").quantize(Decimal(".01"), rounding=ROUND_UP)
            after_balance = Decimal(f"{player_balance}") - Decimal(f"{item_total}")
        else:
            after_balance = None

        now = datetime.datetime.now()
        if now > datetime.datetime.strptime('13:00:00', '%H:%M:%S'):
            rand_time = now + datetime.timedelta(days=2)
        else:
            rand_time = now + datetime.timedelta(days=1)

        context = {
            "session": True,
            "info": info,
            "user_cart": user_cart,
            "user_cart_number": user_cart_number,
            "user_cart_id": user_cart_id,
            "item_total": f"{item_total:,.2f}",
            "player_balance": player_balance,
            "item_total_float": float(item_total),
            "after_balance": after_balance,
            "buy_now": buy_now,
            "rand_time": rand_time,
        }
        return render(request, "buy.html", context=context)

    else:
        # 未ログイン処理
        return redirect('/')


def buy_confirm(request):
    if not request.GET.get("items"):
        raise Http404

    is_session = config.functions.is_session(request)
    if is_session.valid:

        info = config.functions.get_user_info.from_session(request).all()
        mc_uuid = info["mc_uuid"]

        # オーダーをdbに保存
        order_item = request.GET.get("items")
        order = config.DBManager.add_order(order_item, mc_uuid)

        # ポイント減らす
        point = int(request.GET.get("point"))
        if point:
            config.DBManager.deposit_utazon_user_point(mc_uuid, point)

        # 合計金額を算出
        array = []
        amount: float = 0
        order_item = json.loads(order_item)
        for i in order_item:
            price = config.DBManager.get_item(i[0])[2]

            item_dict = f"{i[0]}({i[1]}個:{price})"
            array.append(item_dict)

            amount += price * i[1]
        amount -= point * 0.1  # <----- THIS

        # 履歴に追加
        history = config.DBManager.get_utazon_user_history(mc_uuid)
        history_obj = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": amount,
            "order_id": order[0],
            "order_item": order_item,
        }
        history.append(history_obj)
        config.DBManager.update_user_history(mc_uuid, json.dumps(history))

        # 出金
        if point:
            reason = ", ".join(array) + f", ポイント使用({point}pt:{point * 0.1})"  # <----- THIS
        else:
            reason = ", ".join(array)
        config.VaultManager.withdraw_player(mc_uuid, amount, reason)

        # カートから削除
        if request.GET.get("buynow") == "False":
            config.DBManager.update_user_cart([], mc_uuid)

        # アイテム情報取得
        order_item_obj = []
        for i in order_item:
            result = config.DBManager.get_item(i[0])

            # item_idのレコードを取得
            item_info = list(result)

            item_info[3] = json.loads(item_info[3])

            item_price = item_info[2]

            item_info.append(int(item_price / 10))
            item_info.append(f"{item_price:,.2f}")
            item_info.append(i[1])

            order_item_obj.append(item_info)

        context = {
            "session": True,
            "info": info,
            "order_id": order[0],
            "order_time": order[1],
            "order_item_obj": order_item_obj,
        }

        return render(request, "buy-confirm.html", context=context)

    else:
        # 未ログイン処理
        return redirect('/login')
