import mysql.connector
import config.settings as settings
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
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG)
    with cnx:
        with cnx.cursor() as cursor:

            # テーブルが存在するか確認
            sql = """CREATE TABLE IF NOT EXISTS `session` (
                                                    session_id VARCHAR(64) UNIQUE,
                                                    session_val VARCHAR(256),
                                                    discord_id BIGINT,
                                                    access_token VARCHAR(64),
                                                    login_date DATETIME,
                                                    expires DATETIME)"""
            cursor.execute(sql)

            sql = """CREATE TABLE IF NOT EXISTS `item` (
                                                    id BIGINT UNIQUE,
                                                    name VARCHAR(256),
                                                    price INT,
                                                    image JSON,
                                                    review JSON,
                                                    stock BIGINT,
                                                    about JSON,
                                                    kind JSON)"""
            cursor.execute(sql)

            sql = """CREATE TABLE IF NOT EXISTS `linked` (
                                                    mc_uuid VARCHAR(36) UNIQUE,
                                                    discord_id BIGINT,
                                                    link_time BIGINT,
                                                    cart JSON)"""
            cursor.execute(sql)
            cursor.close()
            cnx.commit()
