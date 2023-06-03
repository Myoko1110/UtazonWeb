import mysql.connector
import datetime
from config.settings import DATABASES


def session_is_valid(request):
    """
    セッションの確認
    """

    # Cookie取得
    session = request.COOKIES

    config = {
        'user': DATABASES['session']['USER'],
        'password': DATABASES['session']['PASSWORD'],
        'host': DATABASES['session']['HOST'],
        'database': DATABASES['session']['DATABASE'],
    }

    cnx = mysql.connector.connect(**config)

    # dbに接続
    with cnx:
        with cnx.cursor() as cursor:

            # dbがなかったら作成
            sql = "SHOW TABLES LIKE 'session'"
            cursor.execute(sql)
            result = cursor.fetchone()
            if result is None or 'session' not in result:
                sql = """CREATE TABLE `session` (
                            session_id VARCHAR(256),
                            session_val VARCHAR(256),
                            user_id BIGINT,
                            access_token VARCHAR(256),
                            login_date DATETIME,
                            expires DATETIME)"""
                cursor.execute(sql)
                print('aa')
                # 一つずつ処理
                for child in session:

                    # l__から始まるものを指定
                    if child.startswith('l__'):

                        sql = "SELECT * FROM session WHERE session_id=%s"
                        cursor.execute(sql, (child,))

                        # session_idのレコードを取得
                        result = cursor.fetchone()

                        cursor.close()
                        cnx.commit()

                        # EmptySetを判定
                        if result is None or len(result) == 0 or session[child] != result[1]:
                            # 未ログイン処理
                            return "Not login"
                        else:

                            # 有効期限の確認
                            now = datetime.datetime.now()
                            if now > result[5]:
                                # 期限切れの処理
                                return "Expired session"

                            # 既ログイン処理
                            return "Login"
                else:
                    cursor.close()
                    cnx.commit()

                    # 未ログイン処理
                    return "Not login"



