import datetime
import json
import random
from statistics import mean

from django.shortcuts import redirect, render
from django.http import Http404

import config.DBManager
import config.functions
import config.settings as settings


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

    if not result:
        raise Http404

    # レビューを取得
    item_review = json.loads(result[4].replace("\n", "<br>"))

    for i in item_review:
        # item_reviewにmc情報を追加
        mc_uuid = i["mc_uuid"]
        mc_id = config.functions.get_user_info.from_uuid(mc_uuid).mc_id()
        i["mc_id"] = mc_id

        # item_reviewのdateをdatetimeオブジェクトに変換
        date = datetime.datetime.strptime(i["date"], "%Y-%m-%d %H:%M:%S")
        i["date"] = date

    # レビューの平均を計算
    if item_review:
        item_review_av = float("{:.1f}".format(round(mean([i["star"] for i in item_review]), 1)))
    else:
        item_review_av = None

    item_category = config.functions.get_category(result[7]).from_en()

    context = {
        "item_id": result[0],
        "item_name": result[1],
        "item_price": f"{result[2]:,}",
        "item_point": int(result[2] * 0.1),
        "item_images": json.loads(result[3]),
        "item_stock": result[5],
        "item_kind": json.loads(result[6]),
        "item_review": reversed(item_review),
        "item_review_number": len(item_review),
        "item_review_av": item_review_av,
        "item_category": item_category
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
            result = config.DBManager.get_item(i[0])

            # item_idのレコードを取得
            item_info = list(result)

            item_info[3] = json.loads(item_info[3])

            item_price = item_info[2]

            item_info.append(int(item_price / 10))
            item_info.append(f"{item_price:,}")
            item_info.append(i[1])

            user_cart.append(item_info)

        user_later_id = config.DBManager.get_utazon_user_later(info["mc_uuid"])

        user_later = []
        for i in user_later_id:
            result = config.DBManager.get_item(i)

            # item_idのレコードを取得
            item_info = list(result)

            item_info[3] = json.loads(item_info[3])

            item_price = item_info[2]

            item_info.append(int(item_price / 10))
            item_info.append(f"{item_price:,}")
            item_info.append(i)

            user_later.append(item_info)

        item_total = 0
        for i in range(len(user_cart)):
            item_price = user_cart[i][2] * user_cart[i][10]

            item_total += item_price

        if 0 not in [i[5] for i in user_cart]:
            buy_able = True
        else:
            buy_able = False

        user_cart_number = 0
        for i in range(len(user_cart)):
            user_cart_number += user_cart[i][10]

        context = {
            "session": True,
            "user_cart": user_cart,
            "user_cart_number": user_cart_number,
            "user_later": user_later,
            "user_later_number": len(user_later),
            "item_total": f"{item_total:,}",
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

        if not item_id:
            raise Http404

        mc_uuid = config.functions.get_user_info.from_session(request).mc_uuid()
        user_cart_id = config.DBManager.get_utazon_user_cart(mc_uuid)

        if item_id:
            for i in range(len(user_cart_id)):
                child = user_cart_id[i]

                if item_id in child and child[0] == item_id:
                    user_cart_id.remove(child)

                    config.DBManager.update_user_cart(user_cart_id, mc_uuid)

    return redirect("/cart")


def cart_add(request):
    is_session = config.functions.is_session(request)
    if is_session.valid:

        item_id = int(request.GET.get('id'))
        number = int(request.GET.get('n'))

        if not item_id or not number:
            raise Http404

        mc_uuid = config.functions.get_user_info.from_session(request).mc_uuid()

        user_cart_id = list(config.DBManager.get_utazon_user_cart(mc_uuid))

        if item_id and number:

            # すでに該当のアイテムがあったら元の数に足す
            for i in range(len(user_cart_id)):
                if user_cart_id[i][0] == item_id:
                    user_cart_id[i][1] += number
                    break
            else:
                user_cart_id.append([item_id, number])

            config.DBManager.update_user_cart(user_cart_id, mc_uuid)

    return redirect("/cart")


def cart_update(request):
    is_session = config.functions.is_session(request)
    if is_session.valid:

        item_id = int(request.GET.get('id'))
        number = int(request.GET.get('n'))

        if not item_id or not number:
            raise Http404

        mc_uuid = config.functions.get_user_info.from_session(request).mc_uuid()

        user_cart_id = list(config.DBManager.get_utazon_user_cart(mc_uuid))

        if item_id and number:

            # すでに該当のアイテムがあったら元の数に足す
            for i in range(len(user_cart_id)):
                if user_cart_id[i][0] == item_id:
                    user_cart_id[i][1] = number

                    config.DBManager.update_user_cart(user_cart_id, mc_uuid)

    return redirect("/cart")


def later_delete(request):
    is_session = config.functions.is_session(request)
    if is_session.valid:

        item_id = int(request.GET.get('id'))

        if not item_id:
            raise Http404

        mc_uuid = config.functions.get_user_info.from_session(request).mc_uuid()
        user_later_id = config.DBManager.get_utazon_user_later(mc_uuid)

        if item_id:
            user_later_id.remove(item_id)
            config.DBManager.update_user_later(user_later_id, mc_uuid)

    return redirect("/cart")


def later_to_cart(request):
    is_session = config.functions.is_session(request)
    if is_session.valid:

        item_id = int(request.GET.get('id'))

        if not item_id:
            raise Http404

        mc_uuid = config.functions.get_user_info.from_session(request).mc_uuid()

        user_later_id = config.DBManager.get_utazon_user_later(mc_uuid)
        user_cart_id = list(config.DBManager.get_utazon_user_cart(mc_uuid))

        if item_id:
            user_later_id.remove(item_id)
            config.DBManager.update_user_later(user_later_id, mc_uuid)

            # すでに該当のアイテムがあったら元の数に足す
            for i in range(len(user_cart_id)):
                if user_cart_id[i][0] == item_id:
                    user_cart_id[i][1] += 1
                    break
            else:
                user_cart_id.append([item_id, 1])

            config.DBManager.update_user_cart(user_cart_id, mc_uuid)

    return redirect("/cart")


def cart_to_later(request):
    is_session = config.functions.is_session(request)
    if is_session.valid:

        item_id = int(request.GET.get('id'))

        if not item_id:
            raise Http404

        mc_uuid = config.functions.get_user_info.from_session(request).mc_uuid()
        user_cart_id = config.DBManager.get_utazon_user_cart(mc_uuid)

        if item_id:
            for i in range(len(user_cart_id)):

                child = user_cart_id[i]

                if item_id in child and child[0] == item_id:
                    user_cart_id.remove(child)

                    config.DBManager.update_user_cart(user_cart_id, mc_uuid)

        user_later_id = config.DBManager.get_utazon_user_later(mc_uuid)

        if item_id and item_id not in user_later_id:
            user_later_id.append(item_id)
            config.DBManager.update_user_later(user_later_id, mc_uuid)

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


def review(request):
    item_id = request.GET.get('id')
    if not item_id:
        raise Http404

    is_session = config.functions.is_session(request)
    if is_session.valid:
        info = config.functions.get_user_info.from_session(request).all()
        result = config.DBManager.get_item(item_id)
        item_name = result[1]
        item_image = json.loads(result[3])[0]

        context = {
            "item_name": item_name,
            "item_image": item_image,
            "session": True,
            "info": info,
        }

        return render(request, 'review.html', context=context)
    else:
        return redirect(f"item?id={item_id}")


def review_post(request):
    item_id = request.GET.get('id')
    if not item_id:
        raise Http404

    is_session = config.functions.is_session(request)
    if is_session.valid:

        mc_uuid = config.functions.get_user_info.from_session(request).mc_uuid()

        review_star = request.GET.get('star')
        review_title = request.GET.get('title')
        review_text = request.GET.get('text')

        result = config.DBManager.get_item(item_id)
        item_review = json.loads(result[4])

        now = datetime.datetime.now().replace(microsecond=0)

        new_review = {
            "id": str(random.randint(0, 99999)).zfill(5),
            "date": str(now),
            "star": int(review_star),
            "title": review_title,
            "value": review_text,
            "useful": 0,
            "mc_uuid": mc_uuid
        }

        item_review.append(new_review)
        item_review = json.dumps(item_review)

        config.DBManager.update_item_review(item_id, item_review)

        return redirect(f"/item?id={item_id}")
    else:
        return redirect(f"/item?id={item_id}")


def review_userful(request):
    item_id = request.GET.get('id')
    review_id = request.GET.get('review_id')

    if not item_id or not review_id:
        raise Http404

    is_session = config.functions.is_session(request)
    if is_session.valid:
        result = config.DBManager.get_item(item_id)
        item_review = json.loads(result[4])

        for i in range(len(item_review)):

            if item_review[i]["id"] != review_id:
                continue
            item_review[i]["useful"] += 1

        item_output = json.dumps(item_review)
        config.DBManager.update_item_review(item_id, item_output)

        return redirect(f"/item?id={item_id}")
    else:
        return redirect(f"/item?id={item_id}")


def category(request):
    cat_id = request.GET.get('name')
    result = config.DBManager.get_item_from_category(cat_id)

    if not result:

        # 親カテゴリを参照
        if cat_id in settings.CATEGORIES.keys():

            # resultをリセット
            result = []
            for i in settings.CATEGORIES[cat_id].keys():

                # カテゴリずつ追加
                child_category = config.DBManager.get_item_from_category(i)

                # カテゴリにアイテムがなかったらスキップ
                if not child_category:
                    continue

                # resultに追加
                else:
                    for child in child_category:
                        result.append(child)

        else:
            raise Http404

    if result:
        for i in range(len(result)):

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

    category = config.functions.get_category(cat_id).from_en()

    context = {
        "result": result,
        "category": category,
    }

    is_session = config.functions.is_session(request)
    if is_session.valid:
        info = config.functions.get_user_info.from_session(request).all()
        context["info"] = info
        context["session"] = True

        return render(request, "category.html", context=context)

    elif is_session.expire:
        context["session"] = "expires"
        response = render(request, 'category.html', context=context)

        for key in request.COOKIES:
            if key.startswith('_Secure-'):
                response.delete_cookie(key)
        response.delete_cookie("LOGIN_STATUS")

        # 期限切れ処理
        return response

    else:
        context["session"] = False
        # 未ログイン処理
        return render(request, 'category.html', context=context)
