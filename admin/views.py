import json

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from utils import *


def admin_index(request):
    if request.user.is_authenticated:
        o = Order.get_active()

        context = {
            "order": o,
        }

        return render(request, "admin-index.html", context=context)

    else:
        return redirect("/admin/login/")


def admin_items(request):
    if request.user.is_authenticated:
        context = {
            "item": Item.get_active(),
        }
        return render(request, "admin-items.html", context=context)
    else:
        return redirect("/admin/login/")


@csrf_exempt
def admin_items_get(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            query = request.POST.get("q")
            sort_by = request.POST.get("s")
            if query:
                item_json = [i.to_dict() for i in Item.search(query)]
            else:
                item_json = [i.to_dict() for i in Item.get_active()]

            return HttpResponse(json.dumps(item_json))

        else:
            return redirect("/admin/items/")

    else:
        return redirect("/admin/login/")


def admin_items_stop(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            item_id = int(request.POST.get("item"))
            i = Item.by_id(item_id)
            i.delete()
        return redirect("/admin/items/")
    else:
        return redirect("/admin/login/")


def admin_items_end_sale(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            items_list = json.loads(request.POST.get("item"))
            items = Item.by_id_list(items_list)

            for i in items:
                i.end_sale()
        return redirect("/admin/items/")

    else:
        return redirect("/admin/login/")


def admin_items_set_sale(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            items_list = json.loads(request.POST.get("items"))
            discount_rate = int(request.POST.get("discountRate"))
            start_date = datetime.datetime.strptime(request.POST.get("startDate"), "%Y-%m-%dT%H:%M")
            end_date = datetime.datetime.strptime(request.POST.get("endDate"), "%Y-%m-%dT%H:%M")
            pride_only = bool(int(request.POST.get("prideOnly")))

            items = Item.by_id_list(items_list)
            for i in items:
                i.set_sale(discount_rate, start_date, end_date, pride_only)
        return redirect("/admin/items/")

    else:
        return redirect("/admin/login/")


def admin_login(request):
    if request.user.is_authenticated:
        return redirect("/admin/")

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/admin/")
        else:
            return render(request, "admin-login.html", context={"error": "ユーザー名またはパスワードが間違っています"})
    else:
        return render(request, "admin-login.html")


def admin_logout(request):
    logout(request)
    return redirect("/admin/login/")
