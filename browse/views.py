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
    if is_session_valid(request)[0]:
        info = get_userinfo_from_session(request)

        # アイテムIDを指定
        item_id = request.GET.get('id')

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
            "item_stock": result[5],
            "item_about": reversed(json.loads(result[6]).items()),
            "item_kind": json.loads(result[7]),
            "item_review": item_review,
            "item_review_number": len(item_review),
            "item_review_av": item_review_av,
            "info": info,
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

                user_cart = []
                for i in json.loads(result[1]):
                    sql = "SELECT * FROM item WHERE item_id=%s"
                    cursor.execute(sql, (i,))

                    # item_idのレコードを取得
                    item_info = list(cursor.fetchone())

                    item_info[3] = json.loads(item_info[3])
                    item_info.append(int(item_info[2] / 10))
                    user_cart.append(item_info)

                cursor.close()
                cnx.commit()

        item_total = 0
        for _ in user_cart:
            item_total += item_info[2]

        context = {
            "session": False,
            "user_cart": user_cart,
            "user_cart_number": len(json.loads(result[1])),
            "user_later": json.loads(result[2]),
            "item_total": item_total,
            "info": info,
        }
        # 既ログイン処理
        return render(request, 'cart.html', context=context)
    elif is_session_valid(request)[1]:
        # 期限切れ処理
        return render(request, 'cart.html', context={"session": False})
    else:
        # 未ログイン処理
        return redirect('/login')


def search(request):
    query = request.GET.get('q')
    if not query:
        return redirect('/')

    if is_session_valid(request)[0]:
        info = get_userinfo_from_session(request)

        cnx = mysql.connector.connect(**settings.DATABASE_CONFIG)

        with cnx:
            with cnx.cursor() as cursor:
                sql = "SELECT * FROM item WHERE name LIKE %s"
                cursor.execute(sql, (f"%{query}%",))

                # mc_uuidのレコードを取得
                result = list(cursor.fetchall())
                cursor.close()
            cnx.commit()

        search_results = len(result)

        for i in range(search_results):

            # imageのJSONをlistに変換
            result[i] = list(result[i])
            result[i][3] = json.loads(result[i][3])

            # レビューの平均を算出
            item_review = json.loads(result[i][4].replace("\n", "<br>"))
            if item_review:
                item_review_av = float("{:.1f}".format(round(mean([i["star"] for i in item_review]), 1)))
            else:
                item_review_av = None
            result[i].append(item_review_av)

            # ポイントを計算
            result[i].append(int(result[i][2] * 0.1))

        context = {
            "result": result,
            "query": query,
            "search_results": search_results,
            "info": info,
        }
        return render(request, 'search.html', context=context)
    elif is_session_valid(request)[1]:
        # 期限切れ処理
        return render(request, 'search.html', context={"session": False})
    else:
        # 未ログイン処理
        return redirect('/login')
