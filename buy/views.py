import json

from django.shortcuts import redirect, render

import config.functions
import config.DBManager


def buy(request):
    is_session = config.functions.is_session(request)
    if is_session.valid:
        info = config.functions.get_user_info.from_session(request).all()

        user_cart_id = config.DBManager.get_utazon_user_cart(info["mc_uuid"])

        # アイテム情報を取得
        user_cart = []
        for i in user_cart_id:
            result = config.DBManager.get_item(i[0])

            # item_idのレコードを取得
            item_info = list(result)

            item_info[3] = json.loads(item_info[3])

            item_price = item_info[2]

            item_info.append(int(item_price / 10))
            item_info.append(f"{item_price:,}")
            item_info.append(i[1])

            user_cart.append(item_info)

        # 請求額算出
        item_total = 0
        for i in range(len(user_cart)):
            item_price = user_cart[i][2] * user_cart[i][9]
            item_total += item_price

        context = {
            "session": True,
            "info": info,
            "user_cart": user_cart,
            "user_cart_number": len(user_cart_id),
            "item_total": f"{item_total:,}",
        }
        return render(request, "buy.html", context=context)

    elif is_session.expire:
        response = render(request, 'buy.html', context={"session": "expires"})

        for key in request.COOKIES:
            if key.startswith('_Secure-'):
                response.delete_cookie(key)
        response.delete_cookie("LOGIN_STATUS")

        # 期限切れ処理
        return response

    else:
        # 未ログイン処理
        return redirect('/')
