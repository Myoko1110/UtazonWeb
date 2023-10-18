import asyncio
import base64
import json
import os
import re
import secrets

from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

import bot
from util import *


async def mypage(request):
    s = Session.by_request(request)
    if s.is_valid:
        u = s.get_user()

        context = {
            "user": u,
            "categories": Category.all(),
            "session": s,
        }

        return render(request, "mypage.html", context=context)

    else:
        return redirect("/login/")


def list_item(request):
    s = Session.by_request(request)
    if s.is_valid:
        waiting_stock = s.get_user().get_waiting_stock()
        error = request.GET.get("error")

        context = {
            "waiting_stock": waiting_stock,
            "error": error,
            "category": settings.CATEGORIES,
            "ALLOCATION_PER": settings.ALLOCATION_PER,
            "session": s,
        }

        return render(request, "list-item.html", context=context)

    else:
        return redirect("/login/")


@csrf_exempt
def list_item_post(request):
    if request.method != "POST":
        raise Http404

    s = Session.by_request(request)
    if s.is_valid:
        item_name = request.POST.get("title")
        if not item_name:
            raise ValueError("item_name is empty")

        item_price = request.POST.get("text")
        if not item_price:
            raise ValueError("item_price is empty")
        try:
            item_price_float = float(item_price)
            if item_price_float == 0.0:
                raise ValueError("item_price is 0")
        except ValueError:
            raise ValueError("item_price is not float")

        about = request.POST.get("about")
        if not about:
            raise ValueError("about is empty")
        try:
            about_decode = json.loads(about)
            if type(about_decode) != list:
                raise ValueError("about is not list of json")
        except json.JSONDecodeError:
            raise ValueError("about is not json")

        new_image = request.POST.getlist("new_image")
        if not new_image:
            raise ValueError("new_image is empty")

        category = request.POST.get('category')
        if not category:
            raise ValueError("category is empty")

        c = Category.by_english(category)
        if not c:
            raise ValueError("category is invalid")

        items_json = request.POST.get("items")
        if not items_json:
            raise ValueError("items is empty")
        try:
            items: list[int] = json.loads(items_json)
            if type(items) != list:
                raise ValueError("item is not list of json")
        except json.JSONDecodeError:
            raise ValueError("items is not json")

        keyword = request.POST.get("keyword")
        if keyword:
            if len(keyword) > 150:
                raise ValueError("keyword is over 150 characters")
            keyword = keyword.split(" ")
            keyword = json.dumps(keyword)
        else:
            keyword = "[]"

        detail = request.POST.get("detail")

        waiting_stock = s.get_user().get_waiting_stock()

        first_item = waiting_stock[items[0]]

        item_amount = first_item.stack_size
        item_material = first_item.material
        item_display_name = first_item.display_name
        item_enchantment = first_item.enchantments
        item_damage = first_item.damage

        error = False
        for i in items:
            item_stack = waiting_stock[i]
            if item_amount != item_stack.stack_size:
                error = True
            elif item_material != item_stack.material:
                error = True
            elif item_display_name != item_stack.display_name:
                error = True
            elif item_enchantment != item_stack.enchantments:
                error = True
            elif item_damage != item_stack.damage:
                error = True
        stock = len(items)

        if error:
            return redirect(f"/mypage/list_item/?error=1#item")

        for i in items:
            waiting_stock[i] = None

        item_id = Item.create_id()

        image_path = []
        fs = settings.MEDIA_ROOT / 'item' / str(item_id)
        for i in new_image:
            db = ""
            while True:
                try:
                    file_ext = re.match(r"data:image/(.*);base64,", i).groups()[0]
                    i = re.sub(r"data:image/.*;base64,", "", i)

                    file_name = f"{secrets.token_urlsafe(4)}.{file_ext}"

                    db = f'/media/item/{item_id}/{file_name}'
                    binary_data = base64.b64decode(i)

                    if len(binary_data) > 1024 * 1024 * 2:
                        raise ValueError("size of new_image is over 2MB")

                    os.makedirs(fs, exist_ok=False)

                    # ファイルを保存
                    with open(fs / file_name, 'wb') as f:
                        f.write(binary_data)

                except FileExistsError:
                    continue
                finally:
                    image_path.append(db)
                    break

        Item.create(item_id, item_name, item_price, image_path, about, detail, c, keyword, s.mc_uuid)
        Item.create_stack(item_id, first_item, stock)

        s.get_user().update_waiting_stock(waiting_stock)
        return redirect(f"/item/?id={item_id}")


def available(request):
    s = Session.by_request(request)
    if s.is_valid:
        available_items = s.get_user().get_available_items()

        error = request.GET.get("error")

        context = {
            "item": available_items,
            "error": error,
            "categories": Category.all(),
            "session": s,
        }

        return render(request, "available_items.html", context=context)

    else:
        return redirect("/login/")


def unavailable(request):
    s = Session.by_request(request)
    if s.is_valid:
        available_items = s.get_user().get_unavailable_items()

        context = {
            "item": available_items,
            "categories": Category.all(),
            "session": s,
        }

        return render(request, "unavailable_items.html", context=context)

    else:
        return redirect("/login/")


def item_edit(request):
    s = Session.by_request(request)
    if s.is_valid:
        item_id = request.GET.get("id")
        if not item_id:
            raise Http404
        item_id = int(item_id)
        item = Item.by_id(item_id)

        if not item or item.mc_uuid != s.mc_uuid or not item.status:
            raise Http404

        context = {
            "item": item,
            "category": settings.CATEGORIES,
            "categories": Category.all(),
            "session": s,
        }
        return render(request, "edit-item.html", context=context)

    else:
        return redirect("/login/")


@csrf_exempt
def item_edit_post(request):
    if request.method != "POST":
        raise Http404

    s = Session.by_request(request)
    if s.is_valid:
        item_id = request.POST.get("item_id")
        if not item_id:
            raise Http404

        item = Item.by_id(item_id)
        if item.mc_uuid != s.mc_uuid or not item.status:
            raise Http404

        item_name = request.POST.get("title")
        if not item_name:
            raise ValueError("item_name is empty")

        item_price = request.POST.get("text")
        if not item_price:
            raise ValueError("item_price is empty")
        try:
            item_price_float = float(item_price)
            if item_price_float == 0.0:
                raise ValueError("item_price is 0")
        except ValueError:
            raise ValueError("item_price is not float")

        about = request.POST.get("about")
        if not about:
            raise ValueError("about is empty")
        try:
            about = json.loads(about)
            if not isinstance(about, list):
                raise ValueError("about is not list of json")
        except json.JSONDecodeError:
            raise ValueError("about is not json")

        category = request.POST.get('category')
        if not category:
            raise ValueError("category is empty")

        c = Category.by_english(category)
        if not c:
            raise ValueError("category is invalid")

        image = request.POST.get("update_image")
        if not image:
            raise ValueError("image is empty")
        try:
            image = json.loads(image)
            if not isinstance(image, list):
                raise ValueError("image is not list of json")
        except json.JSONDecodeError:
            raise ValueError("image is not json")

        detail = request.POST.get("detail")

        new_image = request.POST.getlist('new_image')
        fs = settings.MEDIA_ROOT / 'item' / str(item_id)
        for i in new_image:
            db = ""
            while True:
                try:
                    file_ext = re.match(r"data:image/(.*);base64,", i).groups()[0]
                    i = re.sub(r"data:image/.*;base64,", "", i)
                    file_name = f"{secrets.token_urlsafe(4)}.{file_ext}"

                    db = f'/media/item/{item_id}/{file_name}'
                    binary_data = base64.b64decode(i)

                    if len(binary_data) > 1024 * 1024 * 2:
                        raise ValueError("size of new_image is over 2MB")

                    os.makedirs(fs, exist_ok=True)

                    # ファイルを保存
                    with open(fs / file_name, 'wb') as f:
                        f.write(binary_data)

                except FileExistsError:
                    continue
                finally:
                    image.append(db)
                    break

        item.update(item_name, item_price, image, about, detail, c)
        return redirect(f"/item/?id={item_id}")


def item_stock(request):
    s = Session.by_request(request)
    if s.is_valid:
        waiting_stock = s.get_user().get_waiting_stock()

        item_id = request.GET.get("id")
        if not item_id:
            raise Http404

        item = Item.by_id(item_id)
        if item.mc_uuid != s.mc_uuid or not item.status:
            raise Http404

        stack = item.get_item_stack()

        if not item or item.mc_uuid != s.mc_uuid:
            raise Http404

        error = request.GET.get("error")

        context = {
            "item": item,
            "stack": stack,
            "error": error,
            "waiting_stock": waiting_stock,
            "session": s,
        }

        return render(request, "add-stock.html", context=context)

    else:
        return redirect("/login/")


@csrf_exempt
def item_stock_post(request):
    if request.method != "POST":
        raise Http404

    s = Session.by_request(request)
    if s.is_valid:
        item_id = request.POST.get("item_id")
        if not item_id:
            raise Http404
        item = Item.by_id(item_id)
        if item.mc_uuid != s.mc_uuid or not item.status:
            raise Http404

        index = request.POST.get("items")
        if not index:
            raise ValueError("items is empty")

        index = json.loads(index)
        u = s.get_user()

        waiting_stock = u.get_waiting_stock()
        item_stack = item.get_item_stack()

        item_amount = item_stack.stack_size
        item_material = item_stack.material
        item_name = item_stack.display_name
        item_enchantment = item_stack.enchantments

        error1 = False
        for i in index:
            j = waiting_stock[i]
            if item_amount != j.stack_size:
                error1 = True
            elif item_material != j.material:
                error1 = True
            elif item_name != j.display_name:
                error1 = True
            elif item_enchantment != j.enchantments:
                error1 = True

        if error1:
            return redirect(f"/mypage/available/stock/?id={item_id}&error=1")

        stock = len(index)

        if item_stack.stock + stock > 5000:
            return redirect(f"/mypage/available/stock/?id={item_id}&error=2")

        for i in index:
            waiting_stock[i] = None

        item.increase_stock(stock)
        u.update_waiting_stock(waiting_stock)

        return redirect(f"/item/?id={item_id}")


def item_delete(request):
    s = Session.by_request(request)
    if s.is_valid:
        item_id = request.GET.get("id")
        if not item_id:
            raise Http404

        i = Item.by_id(item_id)
        if s.mc_uuid != i.mc_uuid or not i.status:
            raise Http404

        i.delete()
        return redirect("/mypage/available/")


def item_return(request):
    s = Session.by_request(request)
    if s.is_valid:
        item_id = request.GET.get("id")
        i = Item.by_id(item_id)
        error = request.GET.get("error")

        context = {
            "item": i,
            "error": error,
            "category": settings.CATEGORIES,
            "session": s,
        }

        return render(request, "return-stock.html", context=context)

    else:
        return redirect("/login/")


def item_return_post(request):
    s = Session.by_request(request)
    if s.is_valid:
        item_id = request.GET.get("id")
        if not item_id:
            raise Http404
        amount = int(request.GET.get("amount"))

        i = Item.by_id(int(item_id))
        if i.mc_uuid != s.mc_uuid or not i.status:
            raise Http404

        if i.get_stock() < amount:
            raise ValueError("返却するには在庫が不足しています")

        i.return_stock(amount)
        asyncio.run_coroutine_threadsafe(
            bot.send_returnstock_confirm(s.get_user().get_discord_id()),
            bot.client.loop)
        return redirect("/mypage/available/")
