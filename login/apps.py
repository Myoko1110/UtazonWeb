import mysql.connector
from django.apps import AppConfig

import bot.apps
import config.settings as settings


class LoginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'login'
    path = settings.BASE_DIR / "login"

    def ready(self):
        table_create()
        start_bot()


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
def start_bot():
    bot.apps.ready()


def table_create():
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:

            sql = """CREATE TABLE IF NOT EXISTS `utazon_session` (
                                                    session_id VARCHAR(64) UNIQUE,
                                                    session_val VARCHAR(256),
                                                    mc_uuid VARCHAR(36),
                                                    access_token VARCHAR(64),
                                                    login_at DATETIME,
                                                    expires DATETIME,
                                                    logged_IP varchar(128)
                                                    )"""
            cursor.execute(sql)

            sql = """CREATE TABLE IF NOT EXISTS `utazon_item` (
                                                    sale_id INT AUTO_INCREMENT UNIQUE,
                                                    item_id BIGINT UNIQUE,
                                                    item_name VARCHAR(256),
                                                    price DOUBLE,
                                                    image JSON,
                                                    kind JSON,
                                                    category VARCHAR(64),
                                                    purchases_number BIGINT,
                                                    mc_uuid VARCHAR(36),
                                                    search_keyword JSON,
                                                    created_at DATETIME,
                                                    updated_at DATETIME,
                                                    status BOOLEAN,
                                                    FULLTEXT (item_name) WITH PARSER ngram
                                                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""
            cursor.execute(sql)

            sql = """CREATE TABLE IF NOT EXISTS `utazon_point` (
                                                    mc_uuid VARCHAR(36),
                                                    point INT,
                                                    created_at DATETIME
                                                    )"""
            cursor.execute(sql)

            sql = """CREATE TABLE IF NOT EXISTS `utazon_order` (
                                                    order_id VARCHAR(18) UNIQUE,
                                                    mc_uuid VARCHAR(36),
                                                    order_item JSON,
                                                    ordered_at DATETIME,
                                                    ships_at DATETIME,
                                                    delivers_at DATETIME,
                                                    amount DOUBLE,
                                                    used_point INT,
                                                    canceled BOOLEAN,
                                                    error VARCHAR(64),
                                                    status BOOLEAN,
                                                    dm_sent BOOLEAN
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

            sql = """CREATE TABLE IF NOT EXISTS `utazon_browsinghistory` (
                                                    mc_uuid VARCHAR(36),
                                                    item_id BIGINT,
                                                    browsed_at DATETIME,
                                                    browse_count INT,
                                                    browse_duration INT,
                                                    UNIQUE KEY uq_history (mc_uuid, item_id)
                                                    )"""
            cursor.execute(sql)

            sql = """CREATE TABLE IF NOT EXISTS `utazon_itemstack` (
                                                    item_id BIGINT UNIQUE,
                                                    item_display_name VARCHAR(64),
                                                    item_material VARCHAR(64),
                                                    item_enchantments JSON,
                                                    item_damage INT,
                                                    stack_size INT,
                                                    stock BIGINT
                                                    )"""
            cursor.execute(sql)

            sql = """CREATE TABLE IF NOT EXISTS `utazon_revenues` (
                                                    id BIGINT AUTO_INCREMENT UNIQUE,
                                                    mc_uuid VARCHAR(36),
                                                    item_id BIGINT,
                                                    item_price DOUBLE,
                                                    qty INT,
                                                    amount DOUBLE,
                                                    bought_at DATETIME,
                                                    sale_by VARCHAR(36)
                                                    )"""
            cursor.execute(sql)

            sql = """CREATE TABLE IF NOT EXISTS `utazon_waitingstock` (
                                                    mc_uuid VARCHAR(36),
                                                    value JSON,
                                                    updated_at DATETIME
                                                    )"""
            cursor.execute(sql)

            sql = """CREATE TABLE IF NOT EXISTS `utazon_returnstock` (
                                                    mc_uuid VARCHAR(36),
                                                    item_id BIGINT,
                                                    amount INT,
                                                    created_at DATETIME,
                                                    delivery_at DATETIME,
                                                    status BOOLEAN,
                                                    error VARCHAR(64)
                                                    )"""
            cursor.execute(sql)

            sql = """CREATE TABLE IF NOT EXISTS `utazon_review` (
                                                    item_id BIGINT,
                                                    id BIGINT UNIQUE AUTO_INCREMENT,
                                                    created_at DATETIME,
                                                    star TINYINT,
                                                    title VARCHAR(64),
                                                    value VARCHAR(1024),
                                                    helpful INT,
                                                    mc_uuid VARCHAR(36),
                                                    UNIQUE KEY uq_review (mc_uuid, item_id)
                                                    )"""
            cursor.execute(sql)

            sql = """CREATE TABLE IF NOT EXISTS `utazon_cart` (
                                                    mc_uuid VARCHAR(36),
                                                    item_id BIGINT,
                                                    quantity INT,
                                                    created_at DATETIME,
                                                    UNIQUE KEY uq_item (mc_uuid, item_id)
                                                    )"""
            cursor.execute(sql)

            sql = """CREATE TABLE IF NOT EXISTS `utazon_later` (
                                                    mc_uuid VARCHAR(36),
                                                    item_id BIGINT,
                                                    quantity INT,
                                                    created_at DATETIME,
                                                    UNIQUE KEY uq_item (mc_uuid, item_id)
                                                    )"""
            cursor.execute(sql)

        cursor.close()
        cnx.commit()

    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["linked"])
    with cnx:
        with cnx.cursor() as cursor:
            # DiscordConnectに従う
            sql = """CREATE TABLE IF NOT EXISTS `linked` (
                                                        mc_uuid VARCHAR(36) UNIQUE,
                                                        discord_id BIGINT,
                                                        link_time BIGINT
                                                        )"""
            cursor.execute(sql)
        cursor.close()
        cnx.commit()
