import datetime
import json
import random
from statistics import mean
from decimal import Decimal, getcontext, ROUND_UP

from django.shortcuts import redirect, render
from django.http import Http404

import config.DBManager
import config.functions
import config.settings as settings

getcontext().prec = 10
point_return = Decimal(settings.POINT_RETURN)


def index_view(request):
    banner_obj = config.functions.get_banners()

    popular_item = config.DBManager.get_popular_item()
    latest_item = config.DBManager.get_latest_item()
    special_feature = config.DBManager.get_special_feature()

    special_feature_list = {}
    for i in special_feature:
        item_list = i.value
        obj_list = []
        for j in item_list:
            item_obj = config.DBManager.get_item(j)
            item_obj[3] = json.loads(item_obj[3])
            obj_list.append(item_obj)
        special_feature_list[i.title] = obj_list

    is_session = config.functions.is_session(request)
    context = {
        "popular_item": popular_item,
        "latest_item": latest_item,
        "special_feature": special_feature_list,
        "categories": config.functions.get_categories(),
        "banner_obj": banner_obj,
        "session": is_session,
    }
    if is_session.valid:
        # ユーザー情報を取得
        info = config.functions.get_user_info.from_session(request).all()
        context["info"] = info

        view_history = config.DBManager.get_user_view_history(info["mc_uuid"])
        view_history_obj = []
        for i in range(4):
            item_id = view_history[i]
            item_obj = config.DBManager.get_item(item_id)
            item_obj[3] = json.loads(item_obj[3])
            view_history_obj.append(item_obj)

        context["view_history_obj"] = view_history_obj

        # 既ログイン処理
        return render(request, "index.html", context=context)
    elif is_session.expire:
        response = render(request, "index.html", context=context)

        for key in request.COOKIES:
            if key.startswith("_Secure-"):
                response.delete_cookie(key)
        response.delete_cookie("LOGIN_STATUS")

        # 期限切れ処理
        return response
    else:
        # 未ログイン処理
        return render(request, "index.html", context=context)


def item(request):
    # アイテムIDを指定
    item_id = request.GET.get("id")

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

    sale_id = config.DBManager.get_id_from_item(item_id)
    item_sale = config.DBManager.get_item_sale(sale_id)
    past_price = 0
    if item_sale and item_sale[2]:
        if calc_status_per(item_sale[4], item_sale[5]) != 0.0 and calc_status_per(item_sale[4], item_sale[5]) != 100.0:
            sale = {"status": True, "discount_rate": item_sale[3]}
            past_price = result[2]
            result[2] = Decimal(str(result[2])) * (Decimal(str(100 - item_sale[3])) / Decimal("100"))
            result[2] = result[2].quantize(Decimal(".01"), rounding=ROUND_UP)
        else:
            sale = {"status": False}
    else:
        sale = {"status": False}
    now = datetime.datetime.now()
    if now > datetime.datetime.strptime("13:00:00", "%H:%M:%S"):
        rand_time = now + datetime.timedelta(days=2)
    else:
        rand_time = now + datetime.timedelta(days=1)

    is_session = config.functions.is_session(request)
    context = {
        "item_id": result[0],
        "item_name": result[1],
        "item_price": f"{result[2]:,.2f}",
        "past_price": f"{past_price:,.2f}",
        "item_point": int(Decimal(str(result[2])) * point_return),
        "item_images": json.loads(result[3]),
        "item_stock": result[5],
        "item_kind": json.loads(result[6]),
        "item_review": reversed(item_review),
        "item_review_number": len(item_review),
        "item_review_av": item_review_av,
        "item_category": item_category,
        "rand_time": rand_time,
        "point_return": int(point_return * 100),
        "categories": config.functions.get_categories(),
        "money_unit": settings.MONEY_UNIT,
        "sale": sale,
        "session": is_session,
    }
    if is_session.valid:
        info = config.functions.get_user_info.from_session(request).all()

        # 閲覧履歴に追加
        config.DBManager.add_user_view_history(info["mc_uuid"], item_id)

        context["info"] = info

        # 既ログイン処理
        return render(request, "item.html", context=context)

    elif is_session.expire:
        response = render(request, "item.html", context=context)

        for key in request.COOKIES:
            if key.startswith("_Secure-"):
                response.delete_cookie(key)
        response.delete_cookie("LOGIN_STATUS")

        # 期限切れ処理
        return response

    else:
        # 未ログイン処理
        return render(request, "item.html", context=context)


def cart(request):
    is_session = config.functions.is_session(request)
    if is_session.valid:
        info = config.functions.get_user_info.from_session(request).all()

        # dbに接続
        user_cart_id = config.DBManager.get_user_cart(info["mc_uuid"])

        user_cart = []
        item_total = 0.0
        for i in user_cart_id:
            result = config.DBManager.get_item(i[0])

            # item_idのレコードを取得
            item_info = list(result)

            item_info[3] = json.loads(item_info[3])

            item_price = item_info[2]

            sale_id = config.DBManager.get_id_from_item(i[0])
            item_sale = config.DBManager.get_item_sale(sale_id)
            if item_sale and item_sale[2]:
                if calc_status_per(item_sale[4], item_sale[5]) != 0.0 and calc_status_per(item_sale[4], item_sale[5]) != 100.0:
                    item_price = Decimal(str(item_price)) * (Decimal(str(100 - item_sale[3])) / Decimal("100"))
                    item_price = item_price.quantize(Decimal(".01"), rounding=ROUND_UP)

            item_info.append(int(Decimal(str(item_price)) * point_return))
            item_info.append(f"{item_price:,.2f}")
            item_info.append(i[1])

            item_total += float(Decimal(str(item_price)) * Decimal(str(i[1])))

            user_cart.append(item_info)

        user_later_id = config.DBManager.get_user_later(info["mc_uuid"])

        user_later = []
        for i in user_later_id:
            result = config.DBManager.get_item(i)

            # item_idのレコードを取得
            item_info = list(result)

            item_info[3] = json.loads(item_info[3])

            item_price = item_info[2]

            sale_id = config.DBManager.get_id_from_item(i)
            item_sale = config.DBManager.get_item_sale(sale_id)
            if item_sale and item_sale[2]:
                if calc_status_per(item_sale[4], item_sale[5]) != 0.0 and calc_status_per(item_sale[4], item_sale[5]) != 100.0:
                    sale = {"status": True, "discount_rate": item_sale[3]}
                    item_price = Decimal(str(item_price)) * (Decimal(str(100 - item_sale[3])) / Decimal("100"))
                    item_price = item_price.quantize(Decimal(".01"), rounding=ROUND_UP)
                else:
                    sale = {"status": False}
            else:
                sale = {"status": False}

            item_info.append(int(Decimal(str(item_price)) * point_return))
            item_info.append(f"{item_price:,.2f}")
            item_info.append(i)
            item_info.append(sale)

            user_later.append(item_info)

        if 0 not in [i[5] for i in user_cart]:
            buy_able = True
        else:
            buy_able = False

        user_cart_number = 0
        for i in range(len(user_cart)):

            user_cart_number += int(user_cart[i][11])

        context = {
            "session": is_session,
            "user_cart": user_cart,
            "user_cart_number": user_cart_number,
            "user_later": user_later,
            "user_later_number": len(user_later),
            "item_total": f"{item_total:,.2f}",
            "buy_able": buy_able,
            "info": info,
            "point_return": int(point_return * 100),
            "categories": config.functions.get_categories(),
            "money_unit": settings.MONEY_UNIT,
        }
        # 既ログイン処理
        return render(request, "cart.html", context=context)

    elif is_session.expire:
        context = {
            "session": is_session,
            "categories": config.functions.get_categories()
        }
        response = render(request, "cart.html", context=context)

        for key in request.COOKIES:
            if key.startswith("_Secure-"):
                response.delete_cookie(key)
        response.delete_cookie("LOGIN_STATUS")

        # 期限切れ処理
        return response

    else:
        # 未ログイン処理
        return redirect("/login")


def cart_delete(request):
    is_session = config.functions.is_session(request)
    if is_session.valid:

        item_id = int(request.GET.get("id"))

        if not item_id:
            raise Http404

        mc_uuid = config.functions.get_user_info.from_session(request).mc_uuid()
        user_cart_id = config.DBManager.get_user_cart(mc_uuid)

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

        item_id = int(request.GET.get("id"))
        number = int(request.GET.get("n"))

        if not item_id or not number:
            raise Http404

        mc_uuid = config.functions.get_user_info.from_session(request).mc_uuid()

        user_cart_id = list(config.DBManager.get_user_cart(mc_uuid))

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

        item_id = int(request.GET.get("id"))
        number = int(request.GET.get("n"))

        if not item_id or not number:
            raise Http404

        mc_uuid = config.functions.get_user_info.from_session(request).mc_uuid()

        user_cart_id = list(config.DBManager.get_user_cart(mc_uuid))

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

        item_id = int(request.GET.get("id"))

        if not item_id:
            raise Http404

        mc_uuid = config.functions.get_user_info.from_session(request).mc_uuid()
        user_later_id = config.DBManager.get_user_later(mc_uuid)

        if item_id:
            user_later_id.remove(item_id)
            config.DBManager.update_user_later(user_later_id, mc_uuid)

    return redirect("/cart")


def later_to_cart(request):
    is_session = config.functions.is_session(request)
    if is_session.valid:

        item_id = int(request.GET.get("id"))

        if not item_id:
            raise Http404

        mc_uuid = config.functions.get_user_info.from_session(request).mc_uuid()

        user_later_id = config.DBManager.get_user_later(mc_uuid)
        user_cart_id = list(config.DBManager.get_user_cart(mc_uuid))

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

        item_id = int(request.GET.get("id"))

        if not item_id:
            raise Http404

        mc_uuid = config.functions.get_user_info.from_session(request).mc_uuid()
        user_cart_id = config.DBManager.get_user_cart(mc_uuid)

        if item_id:
            for i in range(len(user_cart_id)):
                child = user_cart_id[i]

                if item_id in child and child[0] == item_id:
                    user_cart_id.remove(child)

                    config.DBManager.update_user_cart(user_cart_id, mc_uuid)

        user_later_id = config.DBManager.get_user_later(mc_uuid)

        if item_id and item_id not in user_later_id:
            user_later_id.append(item_id)
            config.DBManager.update_user_later(user_later_id, mc_uuid)

    return redirect("/cart")


def search(request):
    query = request.GET.get("q")
    if not query:
        return redirect("/")

    category_en = request.GET.get("category")

    result = config.DBManager.search_item(query, category_en)

    search_results = len(result)

    for i in range(search_results):

        result[i] = list(result[i])

        # レビューの平均を算出
        item_review = json.loads(result[i][4].replace("\n", "<br>"))
        if item_review:
            item_review_av = float("{:.1f}".format(round(mean([i["star"] for i in item_review]), 1)))
        else:
            item_review_av = None
        result[i].append(item_review_av)

        # ポイントを計算
        result[i].append(int(Decimal(str(result[i][2])) * point_return))

        sale_id = config.DBManager.get_id_from_item(result[i][0])
        item_sale = config.DBManager.get_item_sale(sale_id)
        if item_sale and item_sale[2]:
            if calc_status_per(item_sale[4], item_sale[5]) != 0.0 and calc_status_per(item_sale[4], item_sale[5]) != 100.0:
                past_price = f"{result[i][2]:,.2f}"
                sale = {"status": True, "discount_rate": item_sale[3], "past_price": past_price}
                result[i][2] = Decimal(str(result[i][2])) * (Decimal(str(100 - item_sale[3])) / Decimal("100"))
                result[i][2] = result[i][2].quantize(Decimal(".01"), rounding=ROUND_UP)
            else:
                sale = {"status": False}
        else:
            sale = {"status": False}

        result[i].append(sale)

        result[i][3] = json.loads(result[i][3])
        result[i][2] = f"{result[i][2]:,.2f}"

    is_session = config.functions.is_session(request)
    context = {
        "result": result,
        "query": query,
        "category": category,
        "search_results": search_results,
        "point_return": int(point_return * 100),
        "categories": config.functions.get_categories(),
        "money_unit": settings.MONEY_UNIT,
        "session": is_session,
    }
    if is_session.valid:
        info = config.functions.get_user_info.from_session(request).all()
        context["info"] = info

        return render(request, "search.html", context=context)

    elif is_session.expire:
        response = render(request, "search.html", context=context)

        for key in request.COOKIES:
            if key.startswith("_Secure-"):
                response.delete_cookie(key)
        response.delete_cookie("LOGIN_STATUS")

        # 期限切れ処理
        return response

    else:
        # 未ログイン処理
        return render(request, "search.html", context=context)


def review(request):
    item_id = request.GET.get("id")
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
            "session": is_session,
            "info": info,
            "categories": config.functions.get_categories(),
        }

        return render(request, "review.html", context=context)
    else:
        return redirect(f"item?id={item_id}")


def review_post(request):
    item_id = request.GET.get("id")
    if not item_id:
        raise Http404

    is_session = config.functions.is_session(request)
    if is_session.valid:

        mc_uuid = config.functions.get_user_info.from_session(request).mc_uuid()

        review_star = request.GET.get("star")
        review_title = request.GET.get("title")
        review_text = request.GET.get("text")

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
            "mc_uuid": mc_uuid,
            "categories": config.functions.get_categories(),
        }

        item_review.append(new_review)
        item_review = json.dumps(item_review)

        config.DBManager.update_item_review(item_id, item_review)

        return redirect(f"/item?id={item_id}")
    else:
        return redirect(f"/item?id={item_id}")


def review_userful(request):
    item_id = request.GET.get("id")
    review_id = request.GET.get("review_id")

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
    cat_id = request.GET.get("name")
    result = config.DBManager.get_item_from_category(cat_id)

    if not result:

        # 親カテゴリを参照
        if cat_id in settings.CATEGORIES.keys():

            try:
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
            except AttributeError:
                result = config.DBManager.get_item_from_category(cat_id)

        else:
            raise Http404

    if result:
        for i in range(len(result)):

            result[i] = list(result[i])

            # レビューの平均を算出
            item_review = json.loads(result[i][4].replace("\n", "<br>"))
            if item_review:
                item_review_av = float("{:.1f}".format(round(mean([i["star"] for i in item_review]), 1)))
            else:
                item_review_av = None
            result[i].append(item_review_av)

            # ポイントを計算
            result[i].append(int(Decimal(str(result[i][2])) * point_return))

            sale_id = config.DBManager.get_id_from_item(result[i][0])
            item_sale = config.DBManager.get_item_sale(sale_id)
            if item_sale and item_sale[2]:
                if calc_status_per(item_sale[4], item_sale[5]) != 0.0 and calc_status_per(item_sale[4], item_sale[5]) != 100.0:
                    past_price = f"{result[i][2]:,.2f}"
                    sale = {"status": True, "discount_rate": item_sale[3], "past_price": past_price}
                    result[i][2] = Decimal(str(result[i][2])) * (Decimal(str(100 - item_sale[3])) / Decimal("100"))
                    result[i][2] = result[i][2].quantize(Decimal(".01"), rounding=ROUND_UP)
                else:
                    sale = {"status": False}
            else:
                sale = {"status": False}

            result[i].append(sale)

            result[i][3] = json.loads(result[i][3])
            result[i][2] = f"{result[i][2]:,.2f}"

    category_obj = config.functions.get_category(cat_id).from_en()

    is_session = config.functions.is_session(request)
    context = {
        "result": result,
        "category": category_obj,
        "categories": config.functions.get_categories(),
        "money_unit": settings.MONEY_UNIT,
        "point_return": int(point_return * 100),
        "session": is_session,
    }
    if is_session.valid:
        info = config.functions.get_user_info.from_session(request).all()
        context["info"] = info

        return render(request, "category.html", context=context)

    elif is_session.expire:
        response = render(request, "category.html", context=context)

        for key in request.COOKIES:
            if key.startswith("_Secure-"):
                response.delete_cookie(key)
        response.delete_cookie("LOGIN_STATUS")

        # 期限切れ処理
        return response

    else:
        # 未ログイン処理
        return render(request, "category.html", context=context)


def history(request):
    is_session = config.functions.is_session(request)
    if is_session.valid:
        info = config.functions.get_user_info.from_session(request).all()

        order_history = config.DBManager.get_user_history(info["mc_uuid"])

        for i in range(len(order_history)):
            order_history[i]["date"] = datetime.datetime.strptime(order_history[i]["date"], "%Y-%m-%d %H:%M:%S")
            order_history[i]["delivery_time"] = datetime.datetime.strptime(order_history[i]["delivery_time"], "%Y-%m-%d %H:%M:%S")
            order_history[i]["amount"] = f"{order_history[i]['amount']:,.2f}"

            if datetime.datetime.now() >= order_history[i]["delivery_time"]:
                order_history[i]["status"] = True

            order_history_child = []

            for child in order_history[i]["order_item"]:
                result = config.DBManager.get_item(child[0])

                # item_idのレコードを取得
                item_info = list(result)
                item_info[3] = json.loads(item_info[3])
                item_info.append(child[1])
                order_history_child.append(item_info)

            order_history[i]["order_item"] = order_history_child

        if not order_history:
            order_history = False
        else:
            order_history = reversed(order_history)

        context = {
            "order_history": order_history,
            "session": is_session,
            "info": info,
            "categories": config.functions.get_categories(),
            "money_unit": settings.MONEY_UNIT,
        }
        return render(request, "history.html", context=context)

    elif is_session.expire:
        context = {
            "session": is_session,
            "categories": config.functions.get_categories()
        }
        response = render(request, "history.html", context=context)

        for key in request.COOKIES:
            if key.startswith("_Secure-"):
                response.delete_cookie(key)
        response.delete_cookie("LOGIN_STATUS")

        # 期限切れ処理
        return response
    else:
        # 未ログイン処理
        return redirect("/login")


def view_history(request):
    is_session = config.functions.is_session(request)
    if is_session.valid:
        info = config.functions.get_user_info.from_session(request).all()
        view_history_obj = config.DBManager.get_user_view_history(info["mc_uuid"])

        result = []
        for i in view_history_obj:
            item_result = config.DBManager.get_item(i)
            result.append(item_result)

        for i in range(len(result)):

            result[i] = list(result[i])

            # レビューの平均を算出
            item_review = json.loads(result[i][4].replace("\n", "<br>"))
            if item_review:
                item_review_av = float("{:.1f}".format(round(mean([i["star"] for i in item_review]), 1)))
            else:
                item_review_av = None
            result[i].append(item_review_av)

            # ポイントを計算
            result[i].append(int(Decimal(str(result[i][2])) * point_return))

            sale_id = config.DBManager.get_id_from_item(result[i][0])
            item_sale = config.DBManager.get_item_sale(sale_id)
            if item_sale and item_sale[2]:
                if calc_status_per(item_sale[4], item_sale[5]) != 0.0 and calc_status_per(item_sale[4], item_sale[5]) != 100.0:
                    past_price = f"{result[i][2]:,.2f}"
                    sale = {"status": True, "discount_rate": item_sale[3], "past_price": past_price}
                    result[i][2] = Decimal(str(result[i][2])) * (Decimal(str(100 - item_sale[3])) / Decimal("100"))
                    result[i][2] = result[i][2].quantize(Decimal(".01"), rounding=ROUND_UP)
                else:
                    sale = {"status": False}
            else:
                sale = {"status": False}

            result[i].append(sale)
            result[i][3] = json.loads(result[i][3])
            result[i][2] = f"{result[i][2]:,.2f}"

        context = {
            "result": result,
            "info": info,
            "session": is_session,
            "categories": config.functions.get_categories(),
            "point_return": int(point_return * 100),
            "money_unit": settings.MONEY_UNIT,
        }
        return render(request, "view-history.html", context=context)

    else:
        return redirect("/login")


def status(request):
    is_session = config.functions.is_session(request)
    if is_session.valid:
        info = config.functions.get_user_info.from_session(request).all()

        order_id = request.GET.get("id")
        order_obj = config.DBManager.get_order(order_id)

        order_time = order_obj[3]
        order_delivery = order_obj[2]

        status_per = calc_status_per(order_time, order_delivery)

        arrive_today = order_delivery.date() == datetime.datetime.now().date()

        context = {
            "order_obj": order_obj,
            "status_per": status_per,
            "arrive_today": arrive_today,
            "info": info,
            "session": is_session,
            "categories": config.functions.get_categories(),
        }
        return render(request, "order-status.html", context=context)

    return redirect("/login")


def calc_status_per(past_time: datetime.datetime, future_time: datetime.datetime):
    current_time = datetime.datetime.now()

    if past_time > future_time:
        past_time, future_time = future_time, past_time

    total_duration = future_time - past_time
    elapsed_duration = current_time - past_time

    if elapsed_duration.total_seconds() < 0:
        percentage = 0.0
    elif elapsed_duration.total_seconds() > total_duration.total_seconds():
        percentage = 100.0
    else:
        percentage = (elapsed_duration.total_seconds() / total_duration.total_seconds()) * 100

    return round(percentage)
