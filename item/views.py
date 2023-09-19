import datetime
import json
import math
import random
from decimal import Decimal, getcontext

from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render

import util
from config import settings

getcontext().prec = 10
point_return = Decimal(settings.POINT_RETURN)


def index_view(request):
    # バナーを取得
    banner_obj = util.get_banners()

    # 人気アイテムなど取得
    item_index = util.ItemHelper.get_index_item()

    # セッションを取得
    is_session = util.SessionHelper.is_session(request)
    context = {
        "popular_item": item_index.popular_item,
        "latest_item": item_index.latest_item,
        "special_feature": item_index.special_feature_list,
        "categories": util.ItemHelper.get_category.all(),
        "banner_obj": banner_obj,
        "session": is_session,
    }

    if is_session.valid:
        info = util.UserHelper.get_info.from_session(request)
        context["info"] = info

        # 閲覧履歴取得
        user_view_history = util.UserHelper.get_view_history(info.mc_uuid)
        context["view_history_obj"] = user_view_history

        # 既ログイン処理
        return render(request, "index.html", context=context)

    elif is_session.expire:
        return util.SessionHelper.delete_cookie(request, "index.html", context=context)

    else:
        return render(request, "index.html", context=context)


def item(request):
    item_id = request.GET.get("id")

    # item_idのレコードを取得
    result = util.ItemHelper.get_item()

    if not result:
        raise Http404

    # レビューにデータを追加
    item_review = util.ItemHelper.add_review_data(result["review"])

    # レビューの平均を計算
    item_review_av = util.ItemHelper.calc_review_average(item_review)
    if item_review:
        item_review_av_format = f"{item_review_av:.1f}"
    else:
        item_review_av_format = None

    # カテゴリーを取得
    item_category = util.ItemHelper.get_category.info.from_id(result["category"])

    # セールを取得
    sale = util.ItemHelper.get_sale(result["sale_id"], result["price"])
    item_price = sale.item_price

    # お届け日取得
    rand_time = util.ItemHelper.calc_delivery_time()

    # ポイント計算
    point = util.ItemHelper.calc_point(item_price)

    # 在庫取得
    stock = util.DatabaseHelper.get_item_stock(item_id)

    is_session = util.SessionHelper.is_session(request)
    context = {
        "item_id": result["item_id"],
        "item_name": result["item_name"],
        "item_price": sale.item_price_format,
        "past_price": sale.past_price,
        "item_point": point,
        "item_images": json.loads(result["image"]),
        "item_stock": stock,
        "item_kind": json.loads(result["kind"]),
        "item_review": reversed(item_review),
        "item_review_number": len(item_review),
        "item_review_av": item_review_av,
        "item_review_av_format": item_review_av_format,
        "item_category": item_category,
        "rand_time": rand_time,
        "point_return": util.ItemHelper.point_return_percent,
        "categories": util.ItemHelper.get_category.all(),
        "money_unit": settings.MONEY_UNIT,
        "sale": sale,
        "session": is_session,
    }

    if is_session.valid:
        info = util.UserHelper.get_info.from_session(request)
        context["info"] = info

        # 閲覧履歴に追加
        util.DatabaseHelper.add_user_view_history(info.mc_uuid, item_id)

        # 既ログイン処理
        return render(request, "item.html", context=context)

    elif is_session.expire:
        return util.SessionHelper.delete_cookie(request, "item.html", context)

    else:
        return render(request, "item.html", context=context)


def cart(request):
    is_session = util.SessionHelper.is_session(request)
    if is_session.valid:
        info = util.UserHelper.get_info.from_session(request)

        # カート取得
        user_cart_id = util.DatabaseHelper.get_user_cart(info.mc_uuid)

        # アイテム情報取得
        items_info = util.ItemHelper.get_item.cart_list(user_cart_id)
        user_cart = items_info.item_list

        # トータル金額
        item_total = items_info.total_amount

        # アイテム数
        user_cart_number = items_info.total_qty

        # 後で買うを取得し、アイテム情報を取得
        user_later_id = util.DatabaseHelper.get_user_later(info.mc_uuid)
        user_later = util.ItemHelper.get_item.id_list(user_later_id)

        # 在庫確認し、買えるか確認
        if 0 not in [i["stock"] for i in user_cart]:
            buy_able = True
        else:
            buy_able = False

        context = {
            "session": is_session,
            "user_cart": user_cart,
            "user_cart_number": user_cart_number,
            "user_later": user_later,
            "user_later_number": len(user_later),
            "item_total": f"{item_total:,.2f}",
            "buy_able": buy_able,
            "info": info,
            "point_return": util.ItemHelper.point_return_percent,
            "categories": util.ItemHelper.get_category.all(),
            "money_unit": settings.MONEY_UNIT,
        }
        return render(request, "cart.html", context=context)

    elif is_session.expire:
        context = {
            "session": is_session,
            "categories": util.ItemHelper.get_category.all()
        }
        return util.SessionHelper.delete_cookie(request, "cart.html", context)

    else:
        return redirect("/login")


def cart_delete(request):
    is_session = util.SessionHelper.is_session(request)
    if is_session.valid:

        # アイテムIDを指定
        item_id = int(request.GET.get("id"))

        if not item_id:
            raise Http404

        # UUIDからユーザーのカートを取得
        mc_uuid = util.UserHelper.get_info.from_session(request).mc_uuid
        user_cart_id = util.DatabaseHelper.get_user_cart(mc_uuid)

        for i in range(len(user_cart_id)):
            child = user_cart_id[i]

            # 該当のものだったら
            if item_id in child and child[0] == item_id:
                # 削除してアップデート
                user_cart_id.remove(child)
                util.DatabaseHelper.update_user_cart(user_cart_id, mc_uuid)

    return redirect("/cart")


def cart_add(request):
    is_session = util.SessionHelper.is_session(request)
    if is_session.valid:

        # アイテムIDと数量を指定
        item_id = int(request.GET.get("id"))
        number = int(request.GET.get("n"))

        if not item_id or not number:
            raise Http404

        # UUIDからユーザーのカートを取得
        mc_uuid = util.UserHelper.get_info.from_session(request).mc_uuid
        user_cart_id = list(util.DatabaseHelper.get_user_cart(mc_uuid))

        # 既に該当のアイテムがあったら元の数に足す
        for i in range(len(user_cart_id)):
            if user_cart_id[i][0] == item_id:
                user_cart_id[i][1] += number
                break
        else:
            # カートに追加
            user_cart_id.append([item_id, number])

        # カートをアップデート
        util.DatabaseHelper.update_user_cart(user_cart_id, mc_uuid)

    return redirect("/cart")


def cart_update(request):
    is_session = util.SessionHelper.is_session(request)
    if is_session.valid:

        item_id = int(request.GET.get("id"))
        number = int(request.GET.get("n"))

        if not item_id or not number:
            raise Http404

        mc_uuid = util.UserHelper.get_info.from_session(request).mc_uuid

        user_cart_id = list(util.DatabaseHelper.get_user_cart(mc_uuid))

        if item_id and number:

            # すでに該当のアイテムがあったら元の数に足す
            for i in range(len(user_cart_id)):
                if user_cart_id[i][0] == item_id:
                    user_cart_id[i][1] = number

                    util.DatabaseHelper.update_user_cart(user_cart_id, mc_uuid)

    return redirect("/cart")


def later_delete(request):
    is_session = util.SessionHelper.is_session(request)
    if is_session.valid:

        item_id = int(request.GET.get("id"))

        if not item_id:
            raise Http404

        mc_uuid = util.UserHelper.get_info.from_session(request).mc_uuid
        user_later_id = util.DatabaseHelper.get_user_later(mc_uuid)

        if item_id:
            user_later_id.remove(item_id)
            util.DatabaseHelper.update_user_later(user_later_id, mc_uuid)

    return redirect("/cart")


def later_to_cart(request):
    is_session = util.SessionHelper.is_session(request)
    if is_session.valid:

        item_id = int(request.GET.get("id"))

        if not item_id:
            raise Http404

        mc_uuid = util.UserHelper.get_info.from_session(request).mc_uuid

        user_later_id = util.DatabaseHelper.get_user_later(mc_uuid)
        user_cart_id = list(util.DatabaseHelper.get_user_cart(mc_uuid))

        if item_id:
            user_later_id.remove(item_id)
            util.DatabaseHelper.update_user_later(user_later_id, mc_uuid)

            # すでに該当のアイテムがあったら元の数に足す
            for i in range(len(user_cart_id)):
                if user_cart_id[i][0] == item_id:
                    user_cart_id[i][1] += 1
                    break
            else:
                user_cart_id.append([item_id, 1])

            util.DatabaseHelper.update_user_cart(user_cart_id, mc_uuid)

    return redirect("/cart")


def cart_to_later(request):
    is_session = util.SessionHelper.is_session(request)
    if is_session.valid:

        item_id = int(request.GET.get("id"))

        if not item_id:
            raise Http404

        mc_uuid = util.UserHelper.get_info.from_session(request).mc_uuid
        user_cart_id = util.DatabaseHelper.get_user_cart(mc_uuid)

        if item_id:
            for i in range(len(user_cart_id)):
                child = user_cart_id[i]

                if item_id in child and child[0] == item_id:
                    user_cart_id.remove(child)

                    util.DatabaseHelper.update_user_cart(user_cart_id, mc_uuid)

        user_later_id = util.DatabaseHelper.get_user_later(mc_uuid)

        if item_id and item_id not in user_later_id:
            user_later_id.append(item_id)
            util.DatabaseHelper.update_user_later(user_later_id, mc_uuid)

    return redirect("/cart")


def search(request):
    query = request.GET.get("q")
    if not query:
        return redirect("/")

    # カテゴリーを指定
    category_en = request.GET.get("category")
    page = request.GET.get("page")
    if page:
        page = int(page)

    # 結果を取得し、アイテム情報を取得
    result = util.DatabaseHelper.search_item(query, category_en, page)
    result_length = util.DatabaseHelper.count_item(query, category_en, page)
    result = util.ItemHelper.get_item.obj_list(result)

    if not page:
        page = 1

    page_length = range(1, math.ceil(result_length / 25) + 1)

    is_session = util.SessionHelper.is_session(request)
    context = {
        "result": result,
        "result_length": result_length,
        "result_length_range": page_length,
        "result_length_last": page_length[-1],
        "query": query,
        "category_en": category_en,
        "page": page,
        "next_page": page + 1,
        "prev_page": page - 1,
        "category": category,
        "point_return": util.ItemHelper.point_return_percent,
        "categories": util.ItemHelper.get_category.all(),
        "money_unit": settings.MONEY_UNIT,
        "session": is_session,
    }
    if is_session.valid:
        info = util.UserHelper.get_info.from_session(request)
        context["info"] = info
        return render(request, "search.html", context=context)

    elif is_session.expire:
        return util.SessionHelper.delete_cookie(request, "search.html", context=context)

    else:
        return render(request, "search.html", context=context)


def review(request):
    item_id = request.GET.get("id")
    if not item_id:
        raise Http404

    is_session = util.SessionHelper.is_session(request)
    if is_session.valid:
        info = util.UserHelper.get_info.from_session(request)

        # アイテム情報を取得
        result = util.DatabaseHelper.get_item(item_id)
        item_name = result["item_name"]
        item_image = json.loads(result["image"])[0]

        context = {
            "item_name": item_name,
            "item_image": item_image,
            "session": is_session,
            "info": info,
            "categories": util.ItemHelper.get_category.all(),
        }

        return render(request, "review.html", context=context)
    else:
        return redirect(f"item?id={item_id}")


def review_post(request):
    item_id = request.GET.get("id")
    if not item_id:
        raise Http404

    is_session = util.SessionHelper.is_session(request)
    if is_session.valid:

        # UUIDを取得
        mc_uuid = util.UserHelper.get_info.from_session(request).mc_uuid

        review_star = request.GET.get("star")
        review_title = request.GET.get("title")
        review_text = request.GET.get("text")

        # reviewを取得
        result = util.DatabaseHelper.get_item(item_id)
        item_review = json.loads(result["review"])

        # 現在時刻を取得
        now = datetime.datetime.now().replace(microsecond=0)

        new_review = {
            "id": str(random.randint(0, 99999)).zfill(5),
            "date": str(now),
            "star": int(review_star),
            "title": review_title,
            "value": review_text,
            "useful": 0,
            "mc_uuid": mc_uuid,
            "categories": util.ItemHelper.get_category.all(),
        }

        # 新規レビューを追加
        item_review.append(new_review)
        item_review = json.dumps(item_review)

        # 追加したものにアップデート
        util.DatabaseHelper.update_item_review(item_id, item_review)

        return redirect(f"/item?id={item_id}")
    else:
        return redirect(f"/item?id={item_id}")


def review_userful(request):
    item_id = request.GET.get("id")
    review_id = request.GET.get("review_id")

    if not item_id or not review_id:
        raise Http404

    # レビューを取得
    result = util.DatabaseHelper.get_item(item_id)
    item_review = json.loads(result["review"])

    for i in range(len(item_review)):
        # 該当のものがあったら
        if item_review[i]["id"] == review_id:
            item_review[i]["useful"] += 1

    item_output = json.dumps(item_review)
    util.DatabaseHelper.update_item_review(item_id, item_output)

    return redirect(f"/item?id={item_id}")


def category(request):
    cat_id = request.GET.get("name")

    # カテゴリーのアイテムを取得
    result = util.DatabaseHelper.get_item_from_category(cat_id)
    if not result:
        # 親カテゴリを参照
        if cat_id in settings.CATEGORIES.keys():

            try:
                result = []
                for i in settings.CATEGORIES[cat_id]["category"].keys():

                    # カテゴリずつ追加
                    child_category = util.DatabaseHelper.get_item_from_category(i)

                    # カテゴリにアイテムがなかったらスキップ
                    if not child_category:
                        continue

                    # resultに追加
                    else:
                        for child in child_category:
                            result.append(child)
            except AttributeError:
                result = util.DatabaseHelper.get_item_from_category(cat_id)

        else:
            raise Http404

    if result:
        # 結果に情報を追加
        result = util.ItemHelper.get_item.obj_list(result)

    # カテゴリーを取得
    category_obj = util.ItemHelper.get_category.info.from_id(cat_id)

    is_session = util.SessionHelper.is_session(request)
    context = {
        "result": result,
        "category": category_obj,
        "categories": util.ItemHelper.get_category.all(),
        "money_unit": settings.MONEY_UNIT,
        "point_return": util.ItemHelper.point_return_percent,
        "session": is_session,
    }

    if is_session.valid:
        info = util.UserHelper.get_info.from_session(request)
        context["info"] = info

        return render(request, "category.html", context=context)

    elif is_session.expire:
        return util.SessionHelper.delete_cookie(request, "category.html", context)

    else:
        return render(request, "category.html", context=context)


def history(request):
    is_session = util.SessionHelper.is_session(request)
    if is_session.valid:
        info = util.UserHelper.get_info.from_session(request)

        # 注文履歴を取得
        order_history = util.UserHelper.get_history(info.mc_uuid)

        context = {
            "order_history": order_history,
            "session": is_session,
            "info": info,
            "categories": util.ItemHelper.get_category.all(),
            "money_unit": settings.MONEY_UNIT,
            "cancellation_fee": settings.CANCELLATION_FEE,
            "error": request.GET.get("error"),
        }
        return render(request, "history.html", context=context)

    elif is_session.expire:
        context = {
            "session": is_session,
            "categories": util.ItemHelper.get_category.all()
        }
        return util.SessionHelper.delete_cookie(request, "history.html", context=context)

    else:
        return redirect("/login")


def browsing_history(request):
    is_session = util.SessionHelper.is_session(request)
    if is_session.valid:
        info = util.UserHelper.get_info.from_session(request)

        # 閲覧履歴を取得し、アイテム情報を取得
        browsing_history_obj = util.DatabaseHelper.get_user_view_history(info.mc_uuid)
        history_item = [i["item_id"] for i in browsing_history_obj]
        result = util.ItemHelper.get_item.id_list(history_item)

        context = {
            "result": result,
            "info": info,
            "session": is_session,
            "categories": util.ItemHelper.get_category.all(),
            "point_return": util.ItemHelper.point_return_percent,
            "money_unit": settings.MONEY_UNIT,
        }
        return render(request, "browsing-history.html", context=context)

    else:
        return redirect("/login")


def status(request):
    is_session = util.SessionHelper.is_session(request)
    if is_session.valid:
        info = util.UserHelper.get_info.from_session(request)

        # orderを取得
        order_id = request.GET.get("id")
        order_obj = util.DatabaseHelper.get_order(order_id)

        # 時関系
        order_time = order_obj["order_time"]
        order_delivery = order_obj["delivery_time"]

        # 進捗%を取得
        status_per = util.calc_time_percentage(order_time, order_delivery)
        status_per = round(status_per)

        # 今日届くか
        arrive_today = order_delivery.date() == datetime.datetime.now().date()

        order_status = util.DatabaseHelper.get_order(order_id)["status"]

        context = {
            "order_obj": order_obj,
            "status_per": status_per,
            "arrive_today": arrive_today,
            "order_status": order_status,
            "info": info,
            "session": is_session,
            "categories": util.ItemHelper.get_category.all(),
        }
        return render(request, "order-status.html", context=context)

    else:
        return redirect("/login")


def suggest(request):
    return HttpResponse(settings.SUGGEST, content_type="application/json")
