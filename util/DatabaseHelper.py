import datetime
import json

import mysql.connector

import util
from config import settings
from item.models import SpecialFeature


def get_user_cart(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT cart FROM utazon_user WHERE mc_uuid=%s"
            cursor.execute(sql, (mc_uuid,))

            # mc_uuidのレコードを取得
            result = cursor.fetchone()

            if not result:
                return False

            return json.loads(result[0])


def get_user_later(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT later FROM utazon_user WHERE mc_uuid=%s"
            cursor.execute(sql, (mc_uuid,))

            # mc_uuidのレコードを取得
            result = cursor.fetchone()

            if not result:
                return False
            return json.loads(result[0])


def get_item(item_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM utazon_item WHERE item_id=%s"
            cursor.execute(sql, (item_id,))

            # item_idのレコードを取得
            result = cursor.fetchone()

            if not result:
                return False
    return result


def get_user_point(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT point FROM utazon_user WHERE mc_uuid=%s"
            cursor.execute(sql, (mc_uuid,))

            # mc_uuidのレコードを取得
            result = cursor.fetchone()

            if not result:
                return False
    return result[0]


def withdraw_user_point(mc_uuid, amount: int):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT point FROM utazon_user WHERE mc_uuid=%s"
            cursor.execute(sql, (mc_uuid,))

            # mc_uuidのレコードを取得
            result = cursor.fetchone()

            if not result:
                return False

            if result[0] < amount:
                raise Exception("使用できるポイントを超えています")

            point = result[0] - amount

            sql = "UPDATE IGNORE utazon_user SET point=%s WHERE mc_uuid=%s"

            cursor.execute(sql, (point, mc_uuid))
            cnx.commit()
    return True


def deposit_user_point(mc_uuid, amount):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE IGNORE utazon_user SET point = point + %s WHERE mc_uuid=%s"

            cursor.execute(sql, (amount, mc_uuid))
            cnx.commit()
    return True


def get_item_from_category(cat_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM utazon_item WHERE category=%s AND status=true"
            cursor.execute(sql, (cat_id,))

            # cat_idのレコードを取得
            result = cursor.fetchall()

            if not result:
                return False
    return result


def get_item_from_user(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM utazon_item WHERE mc_uuid=%s AND status=true"
            cursor.execute(sql, (mc_uuid,))

            # cat_idのレコードを取得
            result = cursor.fetchall()

            if not result:
                return False

            for i in range(len(result)):
                sql = "SELECT stock FROM utazon_itemstack WHERE item_id=%s"
                cursor.execute(sql, (result[i]["item_id"],))

                stock = cursor.fetchone()
                result[i]["stock"] = stock["stock"]
                result[i]["image"] = json.loads(result[i]["image"])
                result[i]["sale"] = util.ItemHelper.get_sale(result[i]["sale_id"],
                                                             result[i]["price"])
                result[i]["item_price_format"] = f"{result[i]['price']:,.2f}"

    return result


def search_item(item_query: list, category=None):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            result = []
            if category:
                for i in util.ItemHelper.get_category.child(category):

                    sql = "SELECT * FROM utazon_item WHERE MATCH(item_name) AGAINST(%s) AND category=%s AND status=true"
                    for j in item_query.split("+"):
                        sql += f" OR JSON_CONTAINS(search_keyword, '\"{j}\"', '$') AND status=true"

                    sql += " ORDER BY purchases_number DESC, item_name"
                    cursor.execute(sql, (item_query, i))

                    # mc_uuidのレコードを取得
                    fetch = cursor.fetchall()
                    for k in fetch:
                        result.append(k)

            else:
                sql = "SELECT * FROM utazon_item WHERE MATCH(item_name) AGAINST(%s) AND status=true"

                for i in item_query.split("+"):
                    sql += f" OR JSON_CONTAINS(search_keyword, '\"{i}\"', '$') AND status=true"

                sql += " ORDER BY purchases_number DESC, item_name"
                cursor.execute(sql, (item_query,))

                # mc_uuidのレコードを取得
                fetch = cursor.fetchall()
                for k in fetch:
                    result.append(k)

    return result


def update_user_cart(cart_value, mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    user_cart = json.dumps(cart_value)
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE IGNORE utazon_user SET cart=%s WHERE mc_uuid=%s"

            cursor.execute(sql, (user_cart, mc_uuid))
            cnx.commit()
    return True


def update_user_later(later_value, mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    user_later = json.dumps(later_value)
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE IGNORE utazon_user SET later=%s WHERE mc_uuid=%s"

            cursor.execute(sql, (user_later, mc_uuid))
            cnx.commit()
    return True


def useful_item_review(item_id, id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE utazon_review SET helpful=helpful+1 WHERE item_id=%s AND id=%s"

            cursor.execute(sql, (item_id, id))
            cnx.commit()
    return True


def add_item_review(item_id, star, title, value, mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            now = datetime.datetime.now()

            sql = """INSERT INTO `utazon_review` (item_id, created_at, star, title, value, helpful, mc_uuid)
                     VALUES (%s, %s, %s, %s, %s, 0, %s)"""

            cursor.execute(sql, (item_id, now, star, title, value, mc_uuid))
            cnx.commit()
    return True


def get_session(session_id, session_val):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM utazon_session WHERE session_id=%s AND session_val=%s"
            cursor.execute(sql, (session_id, session_val,))

            # session_idのレコードを取得
            result = cursor.fetchone()

            if not result:
                return False
    return result


def get_discord_id(uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["linked"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT discord_id FROM linked WHERE mc_uuid=%s"
            cursor.execute(sql, (uuid,))

            result = cursor.fetchone()[0]

            if not result:
                return False
    return result


def get_mc_uuid(discord_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["linked"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT mc_uuid FROM linked WHERE discord_id=%s"
            cursor.execute(sql, (discord_id,))
            result = cursor.fetchone()

            if not result:
                return False

            mc_uuid = result[0]
    return mc_uuid


def delete_session(session_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "DELETE IGNORE FROM utazon_session WHERE session_id=%s"
            cursor.execute(sql, (session_id,))
            cnx.commit()
    return True


def create_user_info(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = """INSERT IGNORE INTO `utazon_user` (  
                     `mc_uuid`, `cart`, `later`, `point` 
                     ) VALUES (%s, %s, %s, %s)"""
            cursor.execute(sql, (mc_uuid, "[]", "[]", 0))
            cnx.commit()
    return True


def save_session(session_id, session_value, mc_uuid, access_token, now, expires, logged_IP):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            # すでにidがあるときの対策
            try:
                # sessionテーブルに保存
                sql = """INSERT INTO `utazon_session` (
                         `session_id`, `session_val`, `mc_uuid`, `access_token`,
                         `login_at`, `expires`, `logged_IP`
                         ) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (
                    session_id, session_value, mc_uuid, access_token, now, expires, logged_IP))

            except mysql.connector.Error as err:
                if err.errno == 1062:
                    return err
                else:
                    raise err
            else:
                cnx.commit()
                return True


def add_order(mc_uuid, items, delivery_time, order_id, amount, used_point):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            now = datetime.datetime.now()
            items = json.dumps(items)
            while True:
                try:
                    sql = """INSERT IGNORE INTO `utazon_order` (  
                                         `mc_uuid`, `order_item`, `delivery_at` ,`order_at`,
                                         `order_id`, `amount`, `used_point`, `status`, `canceled`
                                         ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    cursor.execute(sql, (
                        mc_uuid, items, delivery_time, now, order_id, amount, used_point, True,
                        False,))
                except mysql.connector.Error as err:
                    if err.errno == 1062:
                        continue
                    else:
                        raise err
                else:
                    cnx.commit()
                    return True


def get_order(order_id=None):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        if not order_id:
            with cnx.cursor(dictionary=True) as cursor:
                sql = "SELECT * FROM `utazon_order`"
                cursor.execute(sql)

                result = cursor.fetchall()

                for i in range(len(result)):
                    result[i]["delivery_time"] = result[i]["delivery_time"].strftime(
                        "%Y-%m-%d %H:%M:%S")
                    result[i]["order_time"] = result[i]["order_time"].strftime("%Y-%m-%d %H:%M:%S")
                    order_item_load = json.loads(result[i]["order_item"])

                    order_item = []
                    for ii in range(len(order_item_load)):
                        create_list = {"id": order_item_load[ii][0], "qty": order_item_load[ii][1]}
                        order_item.append(create_list)
                    result[i]["order_item"] = order_item

                return result
        else:
            with cnx.cursor(dictionary=True) as cursor:
                sql = "SELECT * FROM `utazon_order` WHERE order_id=%s"
                cursor.execute(sql, (order_id,))

                result = cursor.fetchone()
                return result


def cancel_order(order_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE utazon_order SET status = false, canceled = true WHERE order_id=%s"
            cursor.execute(sql, (order_id,))
            cnx.commit()
    return True


def redelivery_order(order_id, delivery_time):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE utazon_order SET status=true, error=null, delivery_at=%s WHERE order_id=%s"
            cursor.execute(sql, (delivery_time, order_id,))
            cnx.commit()
    return True


def get_user_history(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM utazon_order WHERE mc_uuid=%s ORDER BY order_at DESC"
            cursor.execute(sql, (mc_uuid,))

            # mc_uuidのレコードを取得
            result = cursor.fetchall()

            if not result:
                return False
    return result


def get_user_view_history(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT item_id FROM utazon_browsinghistory WHERE mc_uuid=%s ORDER BY browsed_at DESC"
            cursor.execute(sql, (mc_uuid,))

            # mc_uuidのレコードを取得
            result = cursor.fetchall()

            if not result:
                return False
    return result


def get_user_view_history_four(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = "SELECT item_id FROM utazon_browsinghistory WHERE mc_uuid=%s ORDER BY browsed_at DESC LIMIT 4"
            cursor.execute(sql, (mc_uuid,))

            # mc_uuidのレコードを取得
            result = cursor.fetchall()

            if not result:
                return False
    return result

def add_user_view_history(mc_uuid, item_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            now = datetime.datetime.now()

            sql = """INSERT INTO utazon_browsinghistory (mc_uuid, item_id, browsed_at
                     ) VALUES (%s, %s, %s)"""
            cursor.execute(sql, (mc_uuid, item_id, now))
            cnx.commit()
    return True


def get_popular_item():
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM utazon_item ORDER BY `purchases_number` DESC LIMIT 4"
            cursor.execute(sql)
            result = cursor.fetchall()

    return result


def get_latest_item():
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM utazon_item ORDER BY `sale_id` DESC LIMIT 4"
            cursor.execute(sql)
            result = cursor.fetchall()

    return result


def get_item_sale(item_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM utazon_sale WHERE item_id=%s"
            cursor.execute(sql, (item_id,))
            result = cursor.fetchone()
    return result


def get_item_stock(item_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT stock FROM utazon_itemstack WHERE item_id=%s"
            cursor.execute(sql, (item_id,))
            result = cursor.fetchone()[0]
    return result


def reduce_stock(item_id, amount):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE utazon_itemstack SET stock = stock - %s WHERE item_id=%s"
            cursor.execute(sql, (amount, item_id,))
            cnx.commit()
    return True


def increase_stock(item_id, amount):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE utazon_itemstack SET stock = stock + %s WHERE item_id=%s"
            cursor.execute(sql, (amount, item_id,))
            cnx.commit()
    return True


def update_item(item_id, item_name, price, image, about, category):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE utazon_item SET item_name=%s, price=%s, image=%s, kind=%s, category=%s WHERE item_id=%s"
            cursor.execute(sql, (item_name, price, image, about, category, item_id))
            cnx.commit()
    return True


def increase_purchases(item_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE utazon_item SET purchases_number = purchases_number + 1 WHERE item_id=%s"
            cursor.execute(sql, (item_id,))
            cnx.commit()
    return True


def add_item(item_id, item_name, price, image, kind, category, search_keyword, mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    now = datetime.datetime.now()
    with cnx:
        with cnx.cursor() as cursor:
            sql = """INSERT INTO utazon_item (item_id, item_name, price, image, review, kind,
                     category, purchases_number, search_keyword, mc_uuid, created_at, status)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, true)"""
            cursor.execute(sql,
                           (item_id, item_name, price, image, "[]", kind, category, 0, search_keyword, mc_uuid, now))
            cnx.commit()
    return True


def delete_item(item_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE utazon_item SET status=false WHERE item_id=%s"
            cursor.execute(sql, (item_id,))
            cnx.commit()
    return True


def get_waiting_stock(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT value FROM utazon_waitingstock WHERE mc_uuid=%s"
            cursor.execute(sql, (mc_uuid,))
            result = cursor.fetchone()[0]
    return result


def add_revenues(mc_uuid, item_id, item_price, qty, amount, sale_by):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            now = datetime.datetime.now()

            sql = """INSERT INTO utazon_revenues (mc_uuid, item_id, item_price, qty, amount, bought_at, sale_by)
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (mc_uuid, item_id, item_price, qty, amount, now, sale_by))
            cnx.commit()
    return True


def get_revenues():
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            threedaysago = datetime.datetime.now().replace(minute=0, second=0,
                                                           microsecond=0) - datetime.timedelta(
                days=3)

            sql = "SELECT * FROM utazon_revenues WHERE bought_at < %s"
            cursor.execute(sql, (threedaysago,))
            result = cursor.fetchall()
    return result


def delete_revenues():
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            threedaysago = datetime.datetime.now().replace(minute=0, second=0,
                                                           microsecond=0) - datetime.timedelta(
                days=3)

            sql = "DELETE FROM utazon_revenues WHERE bought_at < %s"
            cursor.execute(sql, (threedaysago,))
            cnx.commit()
    return True


def add_item_stack(item_id, item_name, item_material, item_enchantment, item_damage, stack_size,
                   stock):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = """INSERT INTO utazon_itemstack (item_id, item_display_name, item_material, item_enchantments, item_damage, stack_size, stock)
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (
                item_id, item_name, item_material, item_enchantment, item_damage, stack_size,
                stock))
            cnx.commit()
    return True


def get_item_stack(item_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM utazon_itemstack WHERE item_id=%s"
            cursor.execute(sql, (item_id,))
            result = cursor.fetchone()
    return result


def update_waiting_stock(mc_uuid, value):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE utazon_waitingstock SET value=%s WHERE mc_uuid=%s"
            cursor.execute(sql, (value, mc_uuid))
            cnx.commit()
    return True


def add_return_stock(mc_uuid, item_id, amount):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            now = datetime.datetime.now()
            hour_ago = now + datetime.timedelta(minutes=60)

            sql = """INSERT INTO utazon_returnstock (mc_uuid, item_id, amount, created_at, delivery_at, status)
                   VALUES(%s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (mc_uuid, item_id, amount, now, hour_ago, True))
            cnx.commit()
    return True


def get_review(item_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:

            sql = """SELECT * FROM utazon_review WHERE item_id=%s"""
            cursor.execute(sql, (item_id,))
            result = cursor.fetchall()
    return result


def get_special_feature():
    return SpecialFeature.objects.all()
