import base64
import json
import re
import secrets

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
            "money_unit": settings.MONEY_UNIT,
            "session": is_session,
            "info": info,
        }

        return render(request, "list-item.html", context=context)

    else:
        return redirect("/login")


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
        if util.DatabaseHelper.get_item(item_id)["mc_uuid"] != mc_uuid:
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
