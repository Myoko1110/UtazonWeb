import mysql.connector
from config.settings import DATABASES
from django.apps import AppConfig
import logging


class LoginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'login'

    def ready(self):
        from django.core.signals import request_started
        request_started.connect(table_create, weak=False)


class RunOnce:
    def __init__(self, func):
        self.func = func
        self.has_run = False

    def __call__(self, *args, **kwargs):

        # 一回だけ実行
        if not self.has_run:
            self.has_run = True
            return self.func(*args, **kwargs)


@RunOnce
def table_create(sender, **kwargs):
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
            if result is None or 'session' not in result:
                sql = """CREATE TABLE `session` (
                                        session_id VARCHAR(256),
                                        session_val VARCHAR(256),
                                        user_id BIGINT,
                                        access_token VARCHAR(256),
                                        login_date DATETIME,
                                        expires DATETIME)"""
                cursor.execute(sql)
                logging.info(f"{config['database']}にtable「session」を作成しました")

                sql = "SHOW TABLES LIKE 'item'"
                cursor.execute(sql)

                # 結果を取得
                result = cursor.fetchone()

                # なかったら作成
                if result is None or 'item' not in result:
                    sql = """CREATE TABLE `session` (
                                                        session_id VARCHAR(256),
                                                        session_val VARCHAR(256),
                                                        user_id BIGINT,
                                                        access_token VARCHAR(256),
                                                        login_date DATETIME,
                                                        expires DATETIME)"""
                    cursor.execute(sql)
                    logging.info(f"{config['database']}にtable「item」を作成しました")

            cursor.close()
        cnx.commit()
