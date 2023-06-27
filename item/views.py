from django.shortcuts import redirect, render
import config.DBManager
import config.functions
import json
from statistics import mean


def index_view(request):
    is_session = config.functions.is_session(request)
    if is_session.valid:

        # ユーザー情報を取得
        info = config.functions.get_user_info.from_session(request).all()

        context = {
            "session": True,
            "info": info,
        }
        # 既ログイン処理
        return render(request, 'index.html', context=context)
    elif is_session.expire:
        response = render(request, 'index.html', context={"session": "expires"})

        for key in request.COOKIES:
            if key.startswith('_Secure-'):
                response.delete_cookie(key)
        response.delete_cookie("LOGIN_STATUS")

        # 期限切れ処理
        return response
    else:
        # 未ログイン処理
        return render(request, 'index.html', context={"session": False})


def item(request):
    # アイテムIDを指定
    item_id = request.GET.get('id')

    # item_idのレコードを取得
    result = config.DBManager.get_item(item_id)

    # レビューを取得
    item_review = json.loads(result[4].replace("\n", "<br>"))

    # item_reviewにmc情報を追加
    for i in item_review:
        mc_uuid = i["mc_uuid"]
        mc_id = config.functions.get_user_info.from_uuid(mc_uuid).mc_id()
        i["mc_id"] = mc_id

    # レビューの平均を計算
    if item_review:
        item_review_av = float("{:.1f}".format(round(mean([i["star"] for i in item_review]), 1)))
    else:
        item_review_av = None

    context = {
        "item_id": result[0],
        "item_name": result[1],
        "item_price": result[2],
        "item_point": int(result[2] * 0.1),
        "item_images": json.loads(result[3]),
        "item_stock": result[5],
        "item_about": reversed(json.loads(result[6]).items()),
        "item_kind": json.loads(result[7]),
        "item_review": item_review,
        "item_review_number": len(item_review),
        "item_review_av": item_review_av,

    }

    is_session = config.functions.is_session(request)
    if is_session.valid:
        info = config.functions.get_user_info.from_session(request).all()

        context["info"] = info
        context["session"] = True

        # 既ログイン処理
        return render(request, 'item.html', context=context)

    elif is_session.expire:
        context["session"] = "expires"
        response = render(request, 'item.html', context=context)

        for key in request.COOKIES:
            if key.startswith('_Secure-'):
                response.delete_cookie(key)
        response.delete_cookie("LOGIN_STATUS")

        # 期限切れ処理
        return response

    else:
        context["session"] = False
        # 未ログイン処理
        return render(request, 'item.html', context=context)


def cart(request):
    is_session = config.functions.is_session(request)
    if is_session.valid:
        info = config.functions.get_user_info.from_session(request).all()

        # dbに接続
        user_cart_id = config.DBManager.get_utazon_user_cart(info["mc_uuid"])

        user_cart = []
        for i in user_cart_id:
            result = config.DBManager.get_item(i)

            # item_idのレコードを取得
            item_info = list(result)

            item_info[3] = json.loads(item_info[3])
            item_info.append(int(item_info[2] / 10))
            user_cart.append(item_info)

        item_total = 0
        for _ in user_cart:
            item_total += item_info[2]

        if 0 not in [i[5] for i in user_cart]:
            buy_able = True
        else:
            buy_able = False

        context = {
            "session": True,
            "user_cart": user_cart,
            "user_cart_number": len(user_cart_id),
            "user_later": config.DBManager.get_utazon_user_later(info["mc_uuid"]),
            "item_total": item_total,
            "buy_able": buy_able,
            "info": info,
        }
        # 既ログイン処理
        return render(request, 'cart.html', context=context)

    elif is_session.expire:
        response = render(request, 'cart.html', context={"session": "expires"})

        for key in request.COOKIES:
            if key.startswith('_Secure-'):
                response.delete_cookie(key)
        response.delete_cookie("LOGIN_STATUS")

        # 期限切れ処理
        return response

    else:
        # 未ログイン処理
        return redirect('/login')


def cart_delete(request):
    is_session = config.functions.is_session(request)
    if is_session.valid:

        item_id = int(request.GET.get('id'))

        info = config.functions.get_user_info.from_session(request).all()
        user_cart_id = config.DBManager.get_utazon_user_cart(info["mc_uuid"])

        # mc_uuidのレコードを取得
        if item_id and item_id in user_cart_id:
            user_cart_id.remove(item_id)
            config.DBManager.update_user_cart(user_cart_id, info["mc_uuid"])

    return redirect("/cart")


def cart_add(request):
    is_session = config.functions.is_session(request)
    if is_session.valid:

        item_id = int(request.GET.get('id'))

        info = config.functions.get_user_info.from_session(request).all()

        user_cart_id = list(config.DBManager.get_utazon_user_cart(info["mc_uuid"]))

        if item_id:
            user_cart_id.append(item_id)
            config.DBManager.update_user_cart(user_cart_id, info["mc_uuid"])

    return redirect("/cart")


def search(request):
    query = request.GET.get('q')
    if not query:
        return redirect('/')

    result = config.DBManager.search_item(query)

    search_results = len(result)

    for i in range(search_results):

        # imageのJSONをlistに変換
        result[i] = list(result[i])
        result[i][3] = json.loads(result[i][3])

        # レビューの平均を算出
        item_review = json.loads(result[i][4].replace("\n", "<br>"))
        if item_review:
            item_review_av = float("{:.1f}".format(round(mean([i["star"] for i in item_review]), 1)))
        else:
            item_review_av = None
        result[i].append(item_review_av)

        # ポイントを計算
        result[i].append(int(result[i][2] * 0.1))

    context = {
        "result": result,
        "query": query,
        "search_results": search_results,
    }

    is_session = config.functions.is_session(request)
    if is_session.valid:
        info = config.functions.get_user_info.from_session(request).all()
        context["info"] = info
        context["session"] = True

        return render(request, 'search.html', context=context)

    elif is_session.expire:
        context["session"] = "expires"
        response = render(request, 'search.html', context=context)

        for key in request.COOKIES:
            if key.startswith('_Secure-'):
                response.delete_cookie(key)
        response.delete_cookie("LOGIN_STATUS")

        # 期限切れ処理
        return response

    else:
        context["session"] = False
        # 未ログイン処理
        return render(request, 'search.html', context=context)