from django.shortcuts import redirect, render
import mysql.connector
import datetime


def IndexView(request):

    # cookieを取得
    session = request.COOKIES

    # 1つずつ処理
    for i in session:

        # l__から始まるものを指定
        if i.startswith('l__'):
            config = {
                'user': 'root',
                'password': 'myon1614',
                'host': 'localhost',
                'database': 'sessions',
            }

            connection = mysql.connector.connect(**config)

            # dbに接続
            with connection:
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM session WHERE session_id=%s"
                    cursor.execute(sql,(i,))

                    # session_idのレコードを取得
                    result = cursor.fetchone()

                    # 切断
                    cursor.close()

                    # EmptySetを判定
            if len(result) == 0 or session[i] != result[1]:
                # 未ログイン処理
                return redirect('/login')
            else:

                # 有効期限の確認
                now = datetime.datetime.now()
                if now > result[5]:
                    # 期限切れの処理
                    return redirect('/login')

                # 既ログイン処理
                return render(request, 'index.html')
    else:
        # 未ログイン処理
        return redirect('/login')
