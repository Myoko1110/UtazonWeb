import json

from django.shortcuts import redirect, render
from django.http import Http404

import config.functions
import config.DBManager
import config.VaultManager


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
        for i in range(len(user_cart)):
            item_price = user_cart[i][2] * user_cart[i][10]
            item_total += item_price

        user_cart_number = 0
        for i in range(len(user_cart)):
            user_cart_number += user_cart[i][10]

        player_balance = config.VaultManager.get_player_balance("305d2e94-608f-4198-8381-5dc7bcf70f27")

        context = {
            "session": True,
            "info": info,
            "user_cart": user_cart,
            "user_cart_number": user_cart_number,
            "user_cart_id": user_cart_id,
            "item_total": f"{item_total:,.2f}",
            "player_balance": player_balance,
            "item_total_float": float(item_total),
            "after_balance": player_balance - float(item_total),
            "buy_now": buy_now,
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

        mc_uuid = config.functions.get_user_info.from_session(request).mc_uuid()
        order_item = request.GET.get("items")

        order = config.DBManager.add_order(order_item, mc_uuid)

        if request.GET.get("buynow"):
            config.DBManager.update_user_cart([], mc_uuid)

        order_item_obj = []
        order_item = json.loads(order_item)

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
            "order_time": {
                "year": order[1].year,
                "month": order[1].month,
                "day": order[1].day,
                "hour": order[1].hour,
                "minute": order[1].minute,
                "second": order[1].second,
            },
            "order_item_obj": order_item_obj,
        }

        return render(request, "buy-confirm.html", context=context)

    else:
        # 未ログイン処理
        return redirect('/login')
