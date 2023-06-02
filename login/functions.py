import mysql.connector
import datetime
from config.settings import DATABASES


def check_session(request):

    # Cookie取得
    session = request.COOKIES

    # 一つずつ処理
    for child in session:

        # l__から始まるものを指定
        if child.startswith('l__'):
            config = {
                'user': DATABASES['session']['USER'],
                'password': DATABASES['session']['PASSWORD'],
                'host': DATABASES['session']['HOST'],
                'database': DATABASES['session']['DATABASE'],
            }

            connection = mysql.connector.connect(**config)

            # dbに接続
            with connection:
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM session WHERE session_id=%s"
                    cursor.execute(sql, (child,))

                    # session_idのレコードを取得
                    result = cursor.fetchone()

                    # 切断
                    cursor.close()

                    # EmptySetを判定
            if len(result) == 0 or session[child] != result[1]:
                # 未ログイン処理
                return False
            else:

                # 有効期限の確認
                now = datetime.datetime.now()
                if now > result[5]:
                    # 期限切れの処理
                    return "Expired session"

                # 既ログイン処理
                return True
    else:
        # 未ログイン処理
        return False
