from decimal import getcontext

from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render

import account.deposit_scheduler
from util import *

getcontext().prec = 10
point_return = Decimal(settings.RETURN_RATE)


def index_view(request):
    # バナーを取得
    banner = get_banners()

    # 人気アイテムなど取得
    pi = Item.get_popular()
    li = Item.get_latest()
    fi = Item.get_featured()

    # セッションを取得
    account.deposit_scheduler.deposit_revenues()
    s = Session.by_request(request)
    context = {
        "popular_item": pi,
        "latest_item": li,
        "featured_item": fi,
        "banner": banner,
        "session": s,
    }

    if s.is_valid:
        # 閲覧履歴取得
        browsing_history = s.get_user().get_browsing_history_recently()
        context["browsing_history"] = browsing_history[:4]

        # 既ログイン処理
        return render(request, "index.html", context=context)

    elif s.is_expire:
        return Session.delete_cookie(request, "index.html", context=context)

    else:
        return render(request, "index.html", context=context)


def item(request):
    item_id = int(request.GET.get("id"))

    i = Item.by_id(item_id)

    if not i:
        raise Http404

    # お届け日取得
    rand_time = Order.calc_expected_delivery_time

    s = Session.by_request(request)
    context = {
        "item": i,
        "has_review": s.get_user().has_review(item_id),
        "status": i.status,
        "rand_time": rand_time,
        "session": s,
    }

    if s.is_valid:
        s.get_user().initialize_browsing_history(item_id)
        return render(request, "item.html", context=context)

    elif s.is_expire:
        return Session.delete_cookie(request, "item.html", context)

    else:
        return render(request, "item.html", context=context)


def initialize_browsing_history(request):
    item_id = request.GET.get("item_id")
    if not item_id:
        raise Http404

    s = Session.by_request(request)
    if s.is_valid:
        s.get_user().initialize_browsing_history(item_id)
        return HttpResponse("Success")


def update_browsing_history(request):
    item_id = int(request.GET.get("item_id"))
    duration = int(request.GET.get("duration"))
    if not item_id or not duration:
        raise Http404

    s = Session.by_request(request)
    if s.is_valid:
        s.get_user().update_browsing_history(item_id, duration)
        return HttpResponse("Success")


def cart(request):
    s = Session.by_request(request)
    if s.is_valid:

        c = s.get_user().get_cart()
        l = s.get_user().get_later()

        context = {
            "session": s,
            "cart": c,
            "later": l,
        }
        return render(request, "cart.html", context=context)

    elif s.is_expire:
        context = {
            "session": s,
        }
        return Session.delete_cookie(request, "cart.html", context)

    else:
        return redirect("/login/")


def cart_delete(request):
    s = Session.by_request(request)
    if s.is_valid:

        # アイテムIDを指定
        item_id = int(request.GET.get("id"))
        if not item_id:
            raise Http404

        Cart.delete(s.mc_uuid, item_id)

    return redirect("/cart/")


def cart_add(request):
    s = Session.by_request(request)
    if s.is_valid:

        # アイテムIDと数量を指定
        item_id = int(request.GET.get("id"))
        qty = int(request.GET.get("qty"))
        if not item_id or not qty:
            raise Http404

        Cart.add(s.mc_uuid, item_id, qty)

    return redirect("/cart/")


def cart_update(request):
    s = Session.by_request(request)
    if s.is_valid:

        item_id = int(request.GET.get("id"))
        qty = int(request.GET.get("qty"))
        if not item_id or not qty:
            raise Http404

        Cart.update_qty(s.mc_uuid, item_id, qty)

    return redirect("/cart/")


def later_delete(request):
    s = Session.by_request(request)
    if s.is_valid:

        item_id = int(request.GET.get("id"))
        if not item_id:
            raise Http404

        Later.delete(s.mc_uuid, item_id)

    return redirect("/cart/")


def later_to_cart(request):
    s = Session.by_request(request)
    if s.is_valid:

        item_id = int(request.GET.get("id"))
        if not item_id:
            raise Http404

        qty = s.get_user().get_later().get_qty(item_id)

        Later.delete(s.mc_uuid, item_id)
        Cart.add(s.mc_uuid, item_id, qty)

    return redirect("/cart/")


def cart_to_later(request):
    s = Session.by_request(request)
    if s.is_valid:

        item_id = int(request.GET.get("id"))
        if not item_id:
            raise Http404

        qty = s.get_user().get_cart().get_qty(item_id)

        Cart.delete(s.mc_uuid, item_id)
        Later.add(s.mc_uuid, item_id, qty)

    return redirect("/cart/")


def search(request):
    query = request.GET.get("q")
    if not query:
        return redirect("/")

    # カテゴリーを指定
    category_en = request.GET.get("category")
    page = request.GET.get("page", 1)

    # 結果を取得し、アイテム情報を取得
    r = Item.search(query, Category.by_english(category_en))
    p = Paging(r, page, 10)

    s = Session.by_request(request)
    context = {
        "result": r,
        "paging": p,
        "query": query,
        "category_en": category_en,
        "session": s,
    }
    if s.is_valid:
        return render(request, "search.html", context=context)

    elif s.is_expire:
        return Session.delete_cookie(request, "search.html", context=context)

    else:
        return render(request, "search.html", context=context)


def review(request):
    s = Session.by_request(request)
    item_id = request.GET.get("id")
    if not item_id:
        raise Http404
    item_id = int(item_id)

    if s.is_valid:
        i = Item.by_id(item_id)
        r = Review.by_mc_uuid(s.mc_uuid, item_id)

        context = {
            "item": i,
            "review": r,
            "session": s,
        }

        return render(request, "review.html", context=context)
    else:
        return redirect(f"/item/?id={item_id}")


def review_post(request):
    item_id = request.GET.get("id")
    if not item_id:
        raise Http404

    s = Session.by_request(request)
    if s.is_valid:

        star = request.GET.get("star")
        title = request.GET.get("title")
        text = request.GET.get("text")

        Review.add_review(s.mc_uuid, item_id, int(star), title, text)

        return redirect(f"/item/?id={item_id}")
    else:
        return redirect(f"/item/?id={item_id}")


def review_star(request):
    item_id = int(request.GET.get("id"))
    if not item_id:
        raise Http404

    s = Session.by_request(request)
    if s.is_valid:

        star = request.GET.get("star")
        Review.add_rating(s.mc_uuid, item_id, int(star))

        return HttpResponse("Success")
    else:
        return HttpResponse("User Invalid")


def review_edit(request):
    item_id = int(request.GET.get("id"))
    if not item_id:
        raise Http404

    s = Session.by_request(request)
    if s.is_valid:
        i = Item.by_id(item_id)
        r = Review.by_mc_uuid(s.mc_uuid, item_id)

        context = {
            "item": i,
            "review": r,
            "session": s,
        }

        return render(request, "review-edit.html", context=context)
    else:
        return redirect(f"/item/?id={item_id}")


def review_edit_post(request):
    item_id = int(request.GET.get("id"))
    if not item_id:
        raise Http404

    s = Session.by_request(request)
    if s.is_valid:
        star = int(request.GET.get("star"))
        title = request.GET.get("title")
        text = request.GET.get("text")

        Review.update(s.mc_uuid, item_id, star, title, text)

        return redirect(f"/item/?id={item_id}")
    else:
        return redirect(f"/item/?id={item_id}")


def helpful(request):
    item_id = int(request.GET.get("id"))
    review_id = int(request.GET.get("review_id"))

    if not item_id or not review_id:
        raise Http404

    Review.helpful(item_id, review_id)

    return HttpResponse("Success")


def category(request):
    cat_id = request.GET.get("name")

    c = Category.by_english(cat_id)
    r = c.get_item()

    page = request.GET.get("page", 1)
    p = Paging(r, page, 10)

    s = Session.by_request(request)
    context = {
        "paging": p,
        "category": c,
        "session": s,
    }

    if s.is_valid:
        return render(request, "category.html", context=context)

    elif s.is_expire:
        return Session.delete_cookie(request, "category.html", context)

    else:
        return render(request, "category.html", context=context)


def history(request):
    s = Session.by_request(request)
    if s.is_valid:
        page = int(request.GET.get("page", 1))

        p = Paging(s.get_user().get_order(), page, 10)

        context = {
            "paging": p,
            "session": s,
            "error": request.GET.get("error"),
        }
        return render(request, "history.html", context=context)

    elif s.is_expire:
        context = {
            "session": s,
        }
        return Session.delete_cookie(request, "history.html", context=context)

    else:
        return redirect("/login/")


def browsing_history(request):
    s = Session.by_request(request)
    if s.is_valid:
        page = int(request.GET.get("page", 1))

        # 閲覧履歴を取得し、アイテム情報を取得
        r = s.get_user().get_browsing_history()
        p = Paging(r, page, 10)

        p.result = Item.by_id_list(p.result)

        context = {
            "paging": p,
            "session": s,
        }
        return render(request, "browsing-history.html", context=context)

    else:
        return redirect("/login/")


def status(request):
    s = Session.by_request(request)
    if s.is_valid:
        # orderを取得
        order_id = request.GET.get("id")
        o = Order.by_id(order_id)

        context = {
            "order": o,
            "session": s,
        }
        return render(request, "order-status.html", context=context)

    else:
        return redirect("/login/")


def suggest(request):
    return HttpResponse(settings.SUGGEST, content_type="application/json")
