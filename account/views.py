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

        context = {
            "categories": settings.CATEGORIES,
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
        item_price = request.POST.get("text")
        about = request.POST.get("about")
        new_image = request.POST.getlist('new_image')
        category = request.POST.get('category')

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

                    os.makedirs(fs, exist_ok=False)

                    # ファイルを保存
                    with open(fs / file_name, 'wb') as f:
                        f.write(binary_data)

                except FileExistsError as e:
                    print(e)
                    continue
                finally:
                    image_path.append(db)
                    break

        image_path = json.dumps(image_path)

        util.DatabaseHelper.add_item(item_id, item_name, item_price, image_path, about, category, info.mc_uuid)

        return redirect(f"/item/?id={item_id}")


def on_sale(request):
    is_session = util.SessionHelper.is_session(request)
    if is_session.valid:
        info = util.UserHelper.get_info.from_session(request)

        onsale_items = util.DatabaseHelper.get_item_from_user(info.mc_uuid)

        context = {
            "onsale": onsale_items,
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
        item_price = request.POST.get("text")
        image = request.POST.get("update_image")
        image = json.loads(image)
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
