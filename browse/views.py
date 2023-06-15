from django.shortcuts import redirect, render
from login.functions import session_is_valid
import mysql.connector
import json
import config.settings as settings
from statistics import mean


def index_view(request):

    if session_is_valid(request)[0]:
        # 既ログイン処理
        return render(request, 'index.html', context={"session": False})
    elif session_is_valid(request)[1]:
        # 期限切れ処理
        return render(request, 'index.html', context={"session": False})
    else:
        # 未ログイン処理
        return redirect('/login')


def item(request):

    item_id = request.GET.get('id')

    config = {
        'user': settings.DATABASES['session']['USER'],
        'password': settings.DATABASES['session']['PASSWORD'],
        'host': settings.DATABASES['session']['HOST'],
        'database': settings.DATABASES['session']['DATABASE'],
    }

    if session_is_valid(request)[0]:

        cnx = mysql.connector.connect(**config)

        with cnx:
            with cnx.cursor() as cursor:
                sql = "SELECT * FROM item WHERE id=%s"
                cursor.execute(sql, (item_id,))

                # session_idのレコードを取得
                result = cursor.fetchone()
                cursor.close()
                cnx.commit()

        item_review = json.loads(result[4].replace("\n", "<br>"))

        context = {
            "item_name": result[1],
            "item_price": result[2],
            "item_point": int(result[2] * 0.1),
            "item_images": json.loads(result[3]),
            "item_review": item_review,
            "item_review_number": len(item_review),
            "item_review_av": mean([i["star"] for i in item_review])
        }

        # 既ログイン処理
        return render(request, 'item.html', context=context)
    elif session_is_valid(request)[1]:
        # 期限切れ処理
        return render(request, 'item.html')
    else:
        # 未ログイン処理
        return redirect('/login')
