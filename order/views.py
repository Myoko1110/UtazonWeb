import json
from datetime import datetime, date

from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt

import config.settings
import config.DBManager


@csrf_exempt
def order(request):
    if request.method != "POST":
        raise Http404

    password = request.META["HTTP_PASS"]

    if not password:
        raise Http404

    if password != config.settings.ORDER_LIST_PASS:
        raise Http404

    order_list = json.dumps(config.DBManager.get_order(), indent=4)

    response = HttpResponse(order_list)
    response['Content-Disposition'] = 'application/json'

    return response
