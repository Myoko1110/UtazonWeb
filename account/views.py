import base64
import json
import re
import secrets

import os
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

import util.SessionHelper
from config import settings


def mypage(request):
    is_session = util.SessionHelper.is_session(request)
    if is_session.valid:
        info = util.UserHelper.get_info.from_session(request)

        context = {
            "categories": util.ItemHelper.get_category.all(),
            "session": is_session,
            "info": info,
        }

        return render(request, "mypage.html", context=context)

    else:
        return redirect("/login")


def list_item(request):
    is_session = util.SessionHelper.is_session(request)
    if is_session.valid:
        info = util.UserHelper.get_info.from_session(request)

        waiting_stock = util.DatabaseHelper.get_waiting_stock(info.mc_uuid)
        waiting_stock = json.loads(waiting_stock)

        context = {
            "waiting_stock": waiting_stock,
            "category": settings.CATEGORIES,
            "categories": util.ItemHelper.get_category.all(),
            "money_unit": settings.MONEY_UNIT,
            "session": is_session,
            "info": info,
        }

        return render(request, "list-item.html", context=context)

    else:
        return redirect("/login")


@csrf_exempt
def list_item_post(request):
    if request.method != "POST":
        raise Http404

    is_session = util.SessionHelper.is_session(request)
    if is_session.valid:
        info = util.UserHelper.get_info.from_session(request)

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

        category_valid = False
        if not category:
            raise ValueError("category is empty")
        for i, j in settings.CATEGORIES.items():
            if i == category:
                category_valid = True
                break
            try:
                for key, value in j.items():
                    if key == "JAPANESE":
                        continue
                    if key == category:
                        category_valid = True
                        break
            except AttributeError:
                pass

        if not category_valid:
            raise ValueError("category is invalid")

        items = request.POST.get("items")
        if not items:
            raise ValueError("items is empty")
        try:
            items = json.loads(items)
            if type(items) != list:
                raise ValueError("item is not list of json")
        except json.JSONDecodeError:
            raise ValueError("items is not json")

        waiting_stock = json.loads(util.DatabaseHelper.get_waiting_stock(info.mc_uuid))

        item_amount = waiting_stock[0]["amount"]
        item_material = waiting_stock[0]["item_material"]
        item_name = waiting_stock[0]["item_display_name"]
        item_enchantment = waiting_stock[0]["item_enchantments"]

        for i in items:
            item_stack = waiting_stock[i]
            if item_amount != item_stack["amount"]:
                raise ValueError("item is not all similar")
            elif item_material != item_stack["item_material"]:
                raise ValueError("item is not all similar")
            elif item_name != item_stack["item_display_name"]:
                raise ValueError("item is not all similar")
            elif item_enchantment != item_stack["item_enchantments"]:
                raise ValueError("item is not all similar")
        stock = len(items)

        for i in items:
            waiting_stock[i] = None

        while True:
            item_id = secrets.randbelow(100000)

            item = util.DatabaseHelper.get_item(item_id)
            if not item:
                break

        image_path = []
        fs = settings.MEDIA_ROOT / 'item' / str(item_id)
        for i in new_image:
            while True:
                try:
                    file_ext = re.match(r"data:image/(.*);base64,", i).groups()[0]
                    i = re.sub(r"data:image/.*;base64,", "", i)

                    file_name = f"{secrets.token_urlsafe(4)}.{file_ext}"

                    db = f'{settings.HOST}/media/item/{item_id}/{file_name}'
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

        image_path = json.dumps(image_path)

        util.DatabaseHelper.add_item(
            item_id, item_name, item_price, image_path, about, category, info.mc_uuid)

        util.DatabaseHelper.add_item_stack(
            item_id, item_name, item_material, item_enchantment, item_amount, stock)

        util.DatabaseHelper.update_waiting_stock(
            info.mc_uuid, json.dumps(waiting_stock)
        )

        return redirect(f"/item/?id={item_id}")


def on_sale(request):
    is_session = util.SessionHelper.is_session(request)
    if is_session.valid:
        info = util.UserHelper.get_info.from_session(request)

        onsale_items = util.DatabaseHelper.get_item_from_user(info.mc_uuid)

        context = {
            "onsale": onsale_items,
            "categories": util.ItemHelper.get_category.all(),
            "money_unit": settings.MONEY_UNIT,
            "session": is_session,
            "info": info,
        }

        return render(request, "onsale.html", context=context)

    else:
        return redirect("/login")


def item_edit(request):
    is_session = util.SessionHelper.is_session(request)
    if is_session.valid:
        info = util.UserHelper.get_info.from_session(request)

        item_id = request.GET.get("id")
        item = util.DatabaseHelper.get_item(item_id)

        if not item or item["mc_uuid"] != info.mc_uuid:
            raise Http404

        item["images"] = json.loads(item["image"])

        context = {
            "item": item,
            "categories": util.ItemHelper.get_category.all(),
            "money_unit": settings.MONEY_UNIT,
            "session": is_session,
            "info": info,
        }
        return render(request, "edit-item.html", context=context)

    else:
        return redirect("/login")


@csrf_exempt
def item_edit_post(request):
    if request.method != "POST":
        raise Http404

    is_session = util.SessionHelper.is_session(request)
    if is_session.valid:
        info = util.UserHelper.get_info.from_session(request)

        item_id = request.POST.get("item_id")
        mc_uuid = request.POST.get("mc_uuid")

        db_mc_uuid = util.DatabaseHelper.get_item(item_id)["mc_uuid"]
        if db_mc_uuid != mc_uuid or db_mc_uuid != info.mc_uuid:
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

        image = request.POST.get("update_image")
        if not image:
            raise ValueError("image is empty")
        try:
            image = json.loads(image)
            if type(image) != list:
                raise ValueError("image is not list of json")
        except json.JSONDecodeError:
            raise ValueError("image is not json")

        new_image = request.POST.getlist('new_image')

        for i in new_image:
            while True:
                try:
                    file_ext = re.match(r"data:image/(.*);base64,", i).groups()[0]

                    i = re.sub(r"data:image/.*;base64,", "", i)

                    file_name = f"{secrets.token_urlsafe(4)}.{file_ext}"

                    fs = settings.MEDIA_ROOT / 'item' / item_id / file_name
                    db = f'{settings.HOST}/media/item/{item_id}/{file_name}'
                    binary_data = base64.b64decode(i)

                    if len(binary_data) > 1024 * 1024 * 2:
                        raise ValueError("size of new_image is over 2MB")

                    # ファイルを保存
                    with open(fs, 'wb') as f:
                        f.write(binary_data)

                except FileExistsError:
                    continue
                finally:
                    image.append(db)
                    break

        image = json.dumps(image)
        util.DatabaseHelper.update_item(item_id, item_name, item_price, image)

        return HttpResponse("success")