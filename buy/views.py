import asyncio
import json
from decimal import ROUND_DOWN, getcontext

from django.http import Http404
from django.shortcuts import redirect, render

import bot
import util
from util import *

getcontext().prec = 10
per_point = Decimal(settings.POINT_PER)

deposit_rate = Decimal("100") - Decimal(str(settings.CANCELLATION_FEE))


def buy(request):
    s = Session.by_request(request)
    if s.is_valid:
        item_id = request.GET.get("item")
        if item_id:
            c = Cart.by_id_dict(json.loads(item_id))
            buy_now = True
        else:
            c = s.get_user().get_cart()
            buy_now = False

        delivery_time = Order.calc_expected_delivery_time
        b = s.get_user().get_balance()
        after_balance = Decimal(str(b)) - Decimal(str(c.get_total()))

        context = {
            "cart": c,
            "after_balance": after_balance,
            "balance": b,
            "buy_now": buy_now,
            "rand_time": delivery_time,
            "session": s,
        }
        return render(request, "buy.html", context=context)

    else:
        return redirect("/")


def buy_confirm(request):
    if not request.GET.get("items"):
        raise Http404

    s = Session.by_request(request)
    if s.is_valid:

        items_dict = json.loads(request.GET.get("items"))
        c = Cart.by_id_dict(items_dict)

        if not c:
            raise Exception("商品が選択されていません")

        if not c.is_valid_items():
            raise Exception("無効な商品が指定されました")

        # お届け時間を計算
        delivers_at = Order.calc_delivery_time()

        # オーダーIDを作成
        order_id = Order.create_order_id()

        u = s.get_user()

        # ポイント関係
        total = Decimal(str(c.get_total()))
        point = float(request.GET.get("point"))
        if point != 0.0:
            if not point.is_integer():
                raise Exception("ポイントが整数値ではありません")

            point = int(point)
            if not Decimal(str(total)) >= Decimal(str(point)) * per_point:
                raise Exception("ポイントが請求額を超えています")

            u.deduct_points(point)

            # 合計金額からポイント引く
            total = total - Decimal(str(point)) * per_point

        # 出金
        withdraw_player = u.withdraw(total, "ウェブショップ『Utazon』で購入",
                                     c.create_reason(order_id))
        if not withdraw_player:
            raise Exception("出金に失敗しました")

        for i, q in c.items():
            i.reduce_stock(q)  # 在庫減らす
            i.add_revenues(u.mc_uuid, q)  # 売上情報追加
            i.increase_sold_count(q)  # 販売数追加

        # オーダーをdbに保存
        Order.create(u.mc_uuid, c, delivers_at, order_id, total, point)

        # カートから削除
        if request.GET.get("buynow") == "False":
            u.reset_cart()

        # ポイント付与
        u.add_points(util.calc_point(total))

        # DM送信
        asyncio.run_coroutine_threadsafe(
            bot.send_order_confirm(u.get_discord_id(), order_id, c, delivers_at),
            bot.client.loop
        )

        context = {
            "session": s,
            "order_id": order_id,
            "delivers_at": delivers_at,
            "cart": c,
        }

        return render(request, "buy-confirm.html", context=context)

    else:
        # 未ログイン処理
        return redirect("/login/")


def buy_cancel(request):
    s = Session.by_request(request)
    if s.is_valid:
        order_id = request.GET.get("id")

        # オーダーを取得
        o = Order.by_id(order_id)
        if not o:
            raise Http404
        if not o.mc_uuid == s.mc_uuid:
            raise Http404

        u = s.get_user()

        # 入金する価格を計算
        deposit_price = (deposit_rate / Decimal("100")) * Decimal(str(o.amount))
        deposit_price = float(deposit_price.quantize(Decimal(".01"), rounding=ROUND_DOWN))

        # 理由作成し、入金
        reason = (f"注文番号: {order_id}" +
                  f"(入金額: {o.amount}の{deposit_rate}%(キャンセル料{settings.CANCELLATION_FEE}%))")
        deposit_player = u.deposit(deposit_price,
                                   "ウェブショップ『Utazon』からのキャンセルに伴う返金", reason)

        # エラーが出たらリダイレクト
        if not deposit_player:
            return redirect("/history/?error=true")

        # 在庫を戻す
        [i.increase_stock(q) for i, q in o.order_item.items()]

        # DM送信
        asyncio.run_coroutine_threadsafe(
            bot.send_order_cancel(s.get_user().get_discord_id(), order_id, o.order_item),
            bot.client.loop)

        # オーダーキャンセル
        o.cancel()

        return redirect(f"/history/#{order_id}")

    else:
        return redirect(f"/history/")


def buy_redelivery(request):
    s = Session.by_request(request)
    if s.is_valid:
        order_id = request.GET.get("id")

        o = Order.by_id(order_id)
        if s.mc_uuid != o.mc_uuid:
            raise Http404

        if not o.error:
            raise Exception("再配達できません")

        # DM送信
        asyncio.run_coroutine_threadsafe(
            bot.send_redelivery(s.get_user().get_discord_id(), order_id),
            bot.client.loop)

        o.redelivery()

        return redirect(f"/history/#{order_id}")

    else:
        return redirect(f"/history/")
