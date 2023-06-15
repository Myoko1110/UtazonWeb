import mysql.connector
import datetime
import config.settings as settings


def session_is_valid(request):
    """
    セッションの確認
    """

    # Cookie取得
    session = request.COOKIES

    config = {
        'user': settings.DATABASES['session']['USER'],
        'password': settings.DATABASES['session']['PASSWORD'],
        'host': settings.DATABASES['session']['HOST'],
        'database': settings.DATABASES['session']['DATABASE'],
    }

    cnx = mysql.connector.connect(**config)

    # dbに接続
    with cnx:
        with cnx.cursor() as cursor:

            # 一つずつ処理
            for child in session:

                # l__から始まるものを指定
                if child.startswith('_Secure-'):

                    sql = "SELECT * FROM session WHERE session_id=%s"
                    cursor.execute(sql, (child,))

                    # session_idのレコードを取得
                    result = cursor.fetchone()

                    # EmptySetを判定
                    if result is None or len(result) == 0 or session[child] != result[1]:
                        # 未ログイン処理
                        continue
                    else:

                        cursor.close()
                        cnx.commit()

                        # 有効期限の確認
                        now = datetime.datetime.now()
                        if now > result[5]:

                            # 期限切れの処理
                            return [False, True, False]

                        # 既ログイン処理
                        return [True, False, False]
            else:
                cursor.close()
                cnx.commit()

                if "LOGIN_STATUS" in session and session["LOGIN_STATUS"]:

                    # 期限切れの処理
                    return [False, True, False]

                # 未ログイン処理
                return [False, False, True]
