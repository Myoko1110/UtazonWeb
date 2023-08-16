from django.apps import AppConfig
import mysql.connector

import config.settings as settings


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
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:

            # テーブルが存在するか確認
            sql = """CREATE TABLE IF NOT EXISTS `utazon_session` (
                                                    session_id VARCHAR(64) UNIQUE,
                                                    session_val VARCHAR(256),
                                                    mc_uuid VARCHAR(36),
                                                    access_token VARCHAR(64),
                                                    login_date DATETIME,
                                                    expires DATETIME,
                                                    logged_IP varchar(128)
                                                    )"""
            cursor.execute(sql)

            sql = """CREATE TABLE IF NOT EXISTS `utazon_item` (
                                                    id INT AUTO_INCREMENT UNIQUE,
                                                    item_id BIGINT UNIQUE,
                                                    item_name VARCHAR(256),
                                                    price DOUBLE,
                                                    image JSON,
                                                    review JSON,
                                                    stock BIGINT,
                                                    kind JSON,
                                                    category VARCHAR(64),
                                                    purchases_number BIGINT
                                                    )"""
            cursor.execute(sql)

            sql = """CREATE TABLE IF NOT EXISTS `utazon_user` (
                                                    mc_uuid VARCHAR(36) UNIQUE,
                                                    cart JSON,
                                                    later JSON,
                                                    point INT,
                                                    history JSON,
                                                    view_history JSON
                                                    )"""
            cursor.execute(sql)

            sql = """CREATE TABLE IF NOT EXISTS `utazon_order` (
                                                    mc_uuid VARCHAR(36),
                                                    order_item JSON,
                                                    delivery_time DATETIME,
                                                    order_time DATETIME,
                                                    order_id VARCHAR(18) UNIQUE
                                                    )"""
            cursor.execute(sql)

            sql = """CREATE TABLE IF NOT EXISTS `utazon_sale` (
                                                    id INT AUTO_INCREMENT UNIQUE,
                                                    item_id BIGINT UNIQUE,
                                                    sale_status BOOLEAN,
                                                    discount_rate INT,
                                                    sale_start DATETIME,
                                                    sale_end DATETIME
                                                    )"""
            cursor.execute(sql)

            # DiscordConnectに従う
            sql = """CREATE TABLE IF NOT EXISTS `linked` (
                                                    mc_uuid VARCHAR(36) UNIQUE,
                                                    discord_id BIGINT,
                                                    link_time BIGINT
                                                    )"""
            cursor.execute(sql)
        cursor.close()
        cnx.commit()
