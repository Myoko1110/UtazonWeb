from django.shortcuts import redirect, render
from config.functions import is_session_valid, get_userinfo_from_session, get_userinfo_from_uuid
import mysql.connector
import json
import config.settings as settings
from statistics import mean


def index_view(request):
    if is_session_valid(request)[0]:

        # ユーザー情報を取得
        info = get_userinfo_from_session(request)

        context = {
            "session": False,
            "info": info,
        }
        # 既ログイン処理
        return render(request, 'index.html', context=context)
    elif is_session_valid(request)[1]:
        # 期限切れ処理
        return render(request, 'index.html', context={"session": False})
    else:
        # 未ログイン処理
        return redirect('/login')


def item(request):

    # アイテムIDを指定
    item_id = request.GET.get('id')

    if is_session_valid(request)[0]:

        cnx = mysql.connector.connect(**settings.DATABASE_CONFIG)

        # dbに接続
        with cnx:
            with cnx.cursor() as cursor:
                sql = "SELECT * FROM item WHERE item_id=%s"
                cursor.execute(sql, (item_id,))

                # item_idのレコードを取得
                result = cursor.fetchone()
                cursor.close()
                cnx.commit()

        # レビューを取得
        item_review = json.loads(result[4].replace("\n", "<br>"))

        # item_reviewにmc情報を追加
        for i in item_review:
            mc_uuid = i["mc_uuid"]
            profile = get_userinfo_from_uuid(mc_uuid)
            i["mc_id"] = profile["mc_id"]

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
    elif is_session_valid(request)[1]:
        # 期限切れ処理
        return render(request, 'item.html')
    else:
        # 未ログイン処理
        return redirect('/login')


def cart(request):
    if is_session_valid(request)[0]:
        info = get_userinfo_from_session(request)
        cnx = mysql.connector.connect(**settings.DATABASE_CONFIG)

        # dbに接続
        with cnx:
            with cnx.cursor() as cursor:
                sql = "SELECT * FROM user WHERE mc_uuid=%s"
                cursor.execute(sql, (info["mc_uuid"],))

                # mc_uuidのレコードを取得
                result = cursor.fetchone()

                cart = []
                for i in json.loads(result[1]):
                    sql = "SELECT * FROM item WHERE item_id=%s"
                    cursor.execute(sql, (i,))

                    # item_idのレコードを取得
                    item = list(cursor.fetchone())

                    item[3] = json.loads(item[3])
                    item.append(int(item[2] / 10))
                    cart.append(item)

                cursor.close()
                cnx.commit()

        total = 0
        for i in cart:
            total += item[2]

        context = {
            "session": False,
            "info": info,
            "cart": cart,
            "cart_number": len(json.loads(result[1])),
            "later": json.loads(result[2]),
            "total": total
        }
        # 既ログイン処理
        return render(request, 'cart.html', context=context)
    elif is_session_valid(request)[1]:
        # 期限切れ処理
        return render(request, 'cart.html', context={"session": False})
    else:
        # 未ログイン処理
        return redirect('/login')
