import json
import logging

from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt

import config.settings
import config.DBManager


@csrf_exempt
def order(request):

    # クライアントのIPを取得
    forwarded_addresses = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_addresses:
        client_addr = forwarded_addresses.split(",")[0]
    else:
        client_addr = request.META.get("REMOTE_ADDR")

    if request.method != "POST":
        logging.warning(f"order_listにGETメゾットでアクセスされましたが失敗しました(IP:{client_addr})")
        raise Http404

    password = request.META.get("HTTP_PASS")

    if not password:
        logging.warning(f"order_listにPOSTメゾットでアクセスされましたがパスワードが入力されていませんでした(IP:{client_addr})")
        raise Http404

    if password != config.settings.ORDER_LIST_PASS:
        logging.warning(f"order_listにPOSTメゾットでアクセスされましたがパスワードが違いました(IP:{client_addr})")
        raise Http404

    order_list = json.dumps(config.DBManager.get_order(), indent=4)

    response = HttpResponse(order_list)
    response["Content-Disposition"] = "application/json"

    return response
