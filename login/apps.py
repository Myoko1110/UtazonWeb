import mysql.connector
from config.settings import DATABASES
from django.apps import AppConfig


def table_create():
    print("aa")
    config = {
        'user': DATABASES['session']['USER'],
        'password': DATABASES['session']['PASSWORD'],
        'host': DATABASES['session']['HOST'],
        'database': DATABASES['session']['DATABASE'],
    }
    cnx = mysql.connector.connect(**config)
    with cnx:
        with cnx.cursor() as cursor:
            # テーブルが存在するか確認
            sql = "SHOW TABLES LIKE 'session'"
            cursor.execute(sql)

            # 結果を取得
            result = cursor.fetchone()

            # なかったら作成
            if 'session' not in result:
                sql = """CREATE TABLE `session` (
                                        session_id VARCHAR(256),
                                        session_val VARCHAR(256),
                                        user_id BIGINT,
                                        access_token VARCHAR(256),
                                        login_date DATETIME,
                                        expires DATETIME)"""
                cursor.execute(sql)
            cursor.close()
        cnx.commit()


class LoginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'login'

    def ready(self):
        from django.core.signals import request_started
        request_started.connect(table_create, weak=False)
