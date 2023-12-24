from django.http import Http404
from django.shortcuts import render, redirect

import util
from util import *


def pride(request):
    s = Session.by_request(request)

    context = {
        "session": s,
    }

    return render(request, "pride.html", context=context)


def register(request):
    s = Session.by_request(request)
    if s.is_valid:
        b = s.get_user().get_balance()

        context = {
            "balance": b,
            "session": s,
        }

        return render(request, "register.html", context=context)


def register_confirm(request):
    if request.method != "POST":
        raise Http404

    s = Session.by_request(request)

    if s.is_valid:
        u = s.get_user()

        p = u.get_pride()
        if p and p.status:
            raise Exception("すでにPrideに登録されています")

        plan = PridePlan(request.POST.get("plan"))

        dps = u.deposit(plan.pricing, "ウェブショップ『Utazon』でPrideへの加入",
                            f"YEARLY({plan.pricing}/{plan.jp}額)")

        if not dps:
            raise Exception("出金に失敗しました")

        u.register_pride(plan, True)

        redirect_to = request.POST.get("redirect")
        return redirect(redirect_to)

    else:
        raise Http404
