import asyncio
import json
import logging
import os
import secrets

from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt

import bot
from config import settings
from utils import User


@csrf_exempt
def mailbox_full(request):
    if not auth_password(request):
        raise Http404

    uuid = request.POST.get("uuid")
    order_id = request.POST.get("orderid")

    discord_id = User.by_mc_uuid(uuid).discord_id

    asyncio.run_coroutine_threadsafe(
        bot.send_mailbox_full(discord_id, order_id),
        bot.client.loop
    )

    return HttpResponse("success")


@csrf_exempt
def mailbox_notfound(request):
    if not auth_password(request):
        raise Http404

    uuid = request.POST.get("uuid")
    order_id = request.POST.get("orderid")

    discord_id = User.by_mc_uuid(uuid).discord_id

    asyncio.run_coroutine_threadsafe(
        bot.send_mailbox_notfound(discord_id, order_id),
        bot.client.loop
    )

    return HttpResponse("success")


@csrf_exempt
def order_complete(request):
    if not auth_password(request):
        raise Http404

    uuid = request.POST.get("uuid")
    order_id = request.POST.get("orderid")

    discord_id = User.by_mc_uuid(uuid).discord_id

    asyncio.run_coroutine_threadsafe(
        bot.send_complete_order(discord_id, order_id),
        bot.client.loop
    )

    return HttpResponse("success")


@csrf_exempt
def returnstock_mailbox_full(request):
    if not auth_password(request):
        raise Http404

    uuid = request.POST.get("uuid")
    discord_id = User.by_mc_uuid(uuid).discord_id

    asyncio.run_coroutine_threadsafe(
        bot.send_returnstock_mailbox_full(discord_id),
        bot.client.loop
    )

    return HttpResponse("success")


@csrf_exempt
def returnstock_item_notfound(request):
    if not auth_password(request):
        raise Http404

    uuid = request.POST.get("uuid")
    discord_id = User.by_mc_uuid(uuid).discord_id

    asyncio.run_coroutine_threadsafe(
        bot.send_returnstock_item_notfound(discord_id),
        bot.client.loop
    )

    return HttpResponse("success")


@csrf_exempt
def returnstock_mailbox_notfound(request):
    if not auth_password(request):
        raise Http404

    uuid = request.POST.get("uuid")
    discord_id = User.by_mc_uuid(uuid).discord_id

    asyncio.run_coroutine_threadsafe(
        bot.send_returnstock_mailbox_notfound(discord_id),
        bot.client.loop
    )

    return HttpResponse("success")


@csrf_exempt
def returnstock_complete(request):
    if not auth_password(request):
        raise Http404

    uuid = request.POST.get("uuid")
    discord_id = User.by_mc_uuid(uuid).discord_id

    asyncio.run_coroutine_threadsafe(
        bot.send_complete_returnstock(discord_id),
        bot.client.loop
    )

    return HttpResponse("success")


def auth_password(request):
    # クライアントのIPを取得
    forwarded_addresses = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_addresses:
        client_addr = forwarded_addresses.split(",")[0]
    else:
        client_addr = request.META.get("REMOTE_ADDR")

    if request.method != "POST":
        logging.warning(
            f"order_listにGETメゾットでアクセスされましたが失敗しました(IP:{client_addr})")
        return False

    password = request.META.get("HTTP_PASS")

    if not password:
        logging.warning(
            f"order_listにPOSTメゾットでアクセスされましたがパスワードが入力されていませんでした(IP:{client_addr})")
        return False

    if password != settings.POST_PASS:
        logging.warning(
            f"order_listにPOSTメゾットでアクセスされましたがパスワードが違いました(IP:{client_addr})")
        return False
    return True


@csrf_exempt
def ship_complete(request):
    if not auth_password(request):
        raise Http404

    uuid = request.POST.get("uuid")
    order_id = request.POST.get("orderid")

    discord_id = User.by_mc_uuid(uuid).discord_id

    asyncio.run_coroutine_threadsafe(
        bot.send_complete_ship(discord_id, order_id),
        bot.client.loop
    )

    return HttpResponse("success")


@csrf_exempt
def upload_detail_img(request):
    file: InMemoryUploadedFile = request.FILES.get("image")

    os.makedirs(settings.MEDIA_ROOT / "details", exist_ok=True)

    file_ext = file.name.split(".")[-1]
    file_path = settings.MEDIA_ROOT / "details" / f"{secrets.token_urlsafe(16)}.{file_ext}"
    fs = FileSystemStorage().save(file_path, file)

    content = {
        "success": True,
        "file": f"/media/{fs}"
    }

    return HttpResponse(json.dumps(content), content_type="application/json")
