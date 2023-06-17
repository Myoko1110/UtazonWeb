from django.shortcuts import redirect, render
from config.functions import session_is_valid, get_userinfo_from_session, get_userinfo_from_discord
import mysql.connector
import json
import config.settings as settings
from statistics import mean


def index_view(request):

    if session_is_valid(request)[0]:
        info = get_userinfo_from_session(request)

        context = {
            "session": False,
            "info": info,
        }
        # 既ログイン処理
        return render(request, 'index.html', context=context)
    elif session_is_valid(request)[1]:
        # 期限切れ処理
        return render(request, 'index.html', context={"session": False})
    else:
        # 未ログイン処理
        return redirect('/login')


def item(request):

    item_id = request.GET.get('id')

    if session_is_valid(request)[0]:

        cnx = mysql.connector.connect(**settings.DATABASE_CONFIG)

        with cnx:
            with cnx.cursor() as cursor:
                sql = "SELECT * FROM item WHERE id=%s"
                cursor.execute(sql, (item_id,))

                # session_idのレコードを取得
                result = cursor.fetchone()
                cursor.close()
                cnx.commit()

        # レビューを取得
        item_review = json.loads(result[4].replace("\n", "<br>"))

        # item_reviewにmc情報を追加
        for i in item_review:
            discord_id = i["discord_id"]
            profile = get_userinfo_from_discord(discord_id)
            i["mc_id"] = profile["mc_id"]
            i["mc_uuid"] = profile["mc_uuid"]

        # レビューの平均を計算
        if item_review:
            item_review_av = float("{:.1f}".format(round(mean([i["star"] for i in item_review]), 1)))
        else:
            item_review_av = None

        context = {
            "item_name": result[1],
            "item_price": result[2],
            "item_point": int(result[2] * 0.1),
            "item_images": json.loads(result[3]),
            "item_about": reversed(json.loads(result[6]).items()),
            "item_kind": json.loads(result[7]),
            "item_review": item_review,
            "item_review_number": len(item_review),
            "item_review_av": item_review_av
        }

        # 既ログイン処理
        return render(request, 'item.html', context=context)
    elif session_is_valid(request)[1]:
        # 期限切れ処理
        return render(request, 'item.html')
    else:
        # 未ログイン処理
        return redirect('/login')
