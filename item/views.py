import copy
import json

from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from utils import *

point_return = Decimal(settings.RETURN_RATE)


def index_view(request):
    # threading.Thread(target=pride.scheduler.expires_check).start()

    # バナーを取得
    banner = get_banners()

    # 人気アイテムなど取得
    pi = Item.get_popular()
    li = Item.get_latest()
    fi = Item.get_featured()

    # セッションを取得
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
        bh = s.get_user().browsing_history_recently
        context["browsing_history"] = bh[:4]

        # 既ログイン処理
        return render(request, "index.html", context=context)

    elif s.is_expire:
        return Session.delete_cookie(request, "index.html", context=context)

    else:
        return render(request, "index.html", context=context)


def item(request):
    item_id = request.GET.get("id")
    if not item_id:
        raise Http404

    item_id = int(item_id)
    i = Item.by_id(item_id)

    if not i:
        raise Http404

    now = datetime.datetime.now()

    rand_time = Order.calc_expected_delivery_time()
    fastest_time = Order.calc_expected_fastest_delivery_time()
    count_down = now.replace(hour=15, minute=0, second=0, microsecond=0) - now

    count_down_hours = count_down.seconds // 3600
    count_down_minutes = (count_down.seconds // 60) % 60

    s = Session.by_request(request)
    context = {
        "item": i,
        "now": now,
        "rand_time": rand_time,
        "fastest_time": fastest_time,
        "count_down_hours": count_down_hours,
        "count_down_minutes": count_down_minutes,
        "has_review": s.get_user().has_review(item_id),
        "status": i.status,
        "session": s,
    }

    if s.is_valid:
        return render(request, "item.html", context=context)

    elif s.is_expire:
        return Session.delete_cookie(request, "item.html", context)

    else:
        return render(request, "item.html", context=context)


def initialize_browsing_history(request):
    item_id = int(request.GET.get("item_id"))
    if not item_id:
        raise Http404

    s = Session.by_request(request)
    if s.is_valid:
        s.get_user().initialize_browsing_history(item_id)
        return HttpResponse("Success")
    return HttpResponse("Verify failed")


@csrf_exempt
def update_browsing_history(request):
    if request.method != "POST":
        raise Http404

    item_id = request.GET.get("item_id")
    duration = request.GET.get("duration")
    if not item_id or not duration:
        raise Http404

    item_id = int(item_id)
    duration = int(duration)

    s = Session.by_request(request)
    if s.is_valid:
        s.get_user().update_browsing_history(item_id, duration)
        return HttpResponse("Success")
    return HttpResponse("Verify failed")


def cart(request):
    s = Session.by_request(request)
    if s.is_valid:
        u = s.get_user()
        c = u.cart
        l = u.later

        deleted_cart = copy.deepcopy(c)
        deleted_cart.delete_invalid_items()

        context = {
            "session": s,
            "cart": c,
            "deleted_cart": deleted_cart,
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
        item_id = request.GET.get("id")
        if not item_id:
            raise Http404
        item_id = int(item_id)

        Cart.delete(s.mc_uuid, item_id)

    return redirect("/cart/")


def cart_add(request):
    s = Session.by_request(request)
    if s.is_valid:

        # アイテムIDと数量を指定
        item_id = request.GET.get("id")
        qty = request.GET.get("qty")
        if not item_id or not qty:
            raise Http404

        item_id = int(item_id)
        qty = int(qty)

        Cart.add(s.mc_uuid, item_id, qty)

    return redirect("/cart/")


def cart_update(request):
    s = Session.by_request(request)
    if s.is_valid:

        item_id = request.GET.get("id")
        qty = request.GET.get("qty")
        if not item_id or not qty:
            raise Http404

        item_id = int(item_id)
        qty = int(qty)

        i = Item.by_id(item_id)
        stock = i.stock
        if stock >= qty:
            Cart.update_quantity(s.mc_uuid, item_id, qty)
        else:
            Cart.update_quantity(s.mc_uuid, item_id, stock)

        c = s.get_user().cart
        c.delete_invalid_items()

        cart_list = {
            "total": f"{c.total:,.2f}",
            "amount": c.quantity,
        }
        if stock < qty:
            cart_list["error"] = {
                "msg": "Shortage",
                "stock": stock
            }

        return HttpResponse(json.dumps(cart_list), content_type="application/json")
    return HttpResponse("Fail to verify")


def later_delete(request):
    s = Session.by_request(request)
    if s.is_valid:

        item_id = request.GET.get("id")
        if not item_id:
            raise Http404

        item_id = int(item_id)

        Later.delete(s.mc_uuid, item_id)

    return redirect("/cart/")


def later_to_cart(request):
    s = Session.by_request(request)
    if s.is_valid:

        item_id = request.GET.get("id")
        if not item_id:
            raise Http404

        item_id = int(item_id)

        qty = s.get_user().later.get_quantity(item_id)

        Later.delete(s.mc_uuid, item_id)
        Cart.add(s.mc_uuid, item_id, qty)

    return redirect("/cart/")


def cart_to_later(request):
    s = Session.by_request(request)
    if s.is_valid:

        item_id = request.GET.get("id")
        if not item_id:
            raise Http404

        item_id = int(item_id)

        qty = s.get_user().cart.get_quantity(item_id)

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
    item_id = int(item_id)

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
    item_id = request.GET.get("id")
    if not item_id:
        raise Http404
    item_id = int(item_id)

    s = Session.by_request(request)
    if s.is_valid:

        star = request.GET.get("star")
        Review.add_rating(s.mc_uuid, item_id, int(star))

        return HttpResponse("Success")
    else:
        return HttpResponse("User Invalid")


def review_edit(request):
    item_id = request.GET.get("id")
    if not item_id:
        raise Http404
    item_id = int(item_id)

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
    item_id = request.GET.get("id")
    if not item_id:
        raise Http404
    item_id = int(item_id)

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
    item_id = request.GET.get("id")
    review_id = request.GET.get("review_id")

    if not item_id or not review_id:
        raise Http404

    item_id = int(item_id)
    review_id = int(review_id)

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

        p = Paging(s.get_user().order, page, 10)

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
        r = s.get_user().browsing_history
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

        now = datetime.datetime.now()

        context = {
            "order": o,
            "now": now,
            "session": s,
        }
        return render(request, "order-status.html", context=context)

    else:
        return redirect("/login/")


def suggest(request):
    return HttpResponse(settings.SUGGEST, content_type="application/json")
