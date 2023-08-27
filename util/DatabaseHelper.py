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
            sql = "SELECT * FROM utazon_user WHERE mc_uuid=%s"
            cursor.execute(sql, (mc_uuid,))

            # mc_uuidのレコードを取得
            result = cursor.fetchone()

            if not result:
                return False

            point = result[3] + amount

            sql = "UPDATE IGNORE utazon_user SET point=%s WHERE mc_uuid=%s"

            cursor.execute(sql, (point, mc_uuid))
            cnx.commit()
    return True


def get_item_from_category(cat_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM utazon_item WHERE category=%s"
            cursor.execute(sql, (cat_id,))

            # cat_idのレコードを取得
            result = cursor.fetchall()

            if not result:
                return False
    return result


def search_item(item_query, category=None):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            if category:
                for i in util.ItemHelper.get_category.child(category):
                    sql = "SELECT * FROM utazon_item WHERE item_name LIKE %s AND category=%s"
                    cursor.execute(sql, (f"%{item_query}%", i))

                    result = cursor.fetchall()

            else:
                sql = "SELECT * FROM utazon_item WHERE item_name LIKE %s"
                cursor.execute(sql, (f"%{item_query}%",))

                # mc_uuidのレコードを取得
                result = cursor.fetchall()

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


def update_item_review(item_id, value):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE utazon_item SET review=%s WHERE item_id=%s"

            cursor.execute(sql, (value, item_id,))
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

            sql = "SELECT * FROM linked WHERE mc_uuid=%s"
            cursor.execute(sql, (uuid,))

            result = cursor.fetchone()[1]

            if not result:
                return False
    return result


def get_mc_uuid(discord_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
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
                         `session_id`, `session_val`, `mc_uuid`, `access_token`, `login_date`, `expires`, `logged_IP`
                         ) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (session_id, session_value, mc_uuid, access_token, now, expires, logged_IP))

            except mysql.connector.Error as err:
                if err.errno == 1062:
                    return err
                else:
                    raise err
            else:
                cnx.commit()
                return True


def add_order(mc_uuid, items, delivery_time, order_id, amount):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            now = datetime.datetime.now()
            while True:
                try:
                    sql = """INSERT IGNORE INTO `utazon_order` (  
                                         `mc_uuid`, `order_item`, `delivery_time` ,`order_time`, `order_id`, `amount`, `status`
                                         ) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                    cursor.execute(sql, (mc_uuid, items, delivery_time, now, order_id, amount, False))
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
                    result[i]["delivery_time"] = result[i]["delivery_time"].strftime("%Y-%m-%d %H:%M:%S")
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


def delete_order(order_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE utazon_order SET status=false WHERE order_id=%s"
            cursor.execute(sql, (order_id,))
            cnx.commit()
    return True


def get_user_history(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM utazon_order WHERE mc_uuid=%s"
            cursor.execute(sql, (mc_uuid,))

            # mc_uuidのレコードを取得
            result = cursor.fetchall()

            if not result:
                return False
    return result


def update_user_history(mc_uuid, value):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE IGNORE utazon_user SET history=%s WHERE mc_uuid=%s"
            cursor.execute(sql, (value, mc_uuid,))
            cnx.commit()

    return True


def get_user_view_history(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT * FROM utazon_user WHERE mc_uuid=%s"
            cursor.execute(sql, (mc_uuid,))

            # mc_uuidのレコードを取得
            result = cursor.fetchone()

            if not result:
                return False
    return list(reversed(json.loads(result[5])))


def add_user_view_history(mc_uuid, item_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT * FROM utazon_user WHERE mc_uuid=%s"
            cursor.execute(sql, (mc_uuid,))

            # mc_uuidのレコードを取得
            result = cursor.fetchone()

            if not result:
                return False

            result = json.loads(result[5])

            item_id = int(item_id)
            try:
                if result[-1] == item_id:
                    return
            except IndexError:
                pass

            result.append(item_id)
            sql = "UPDATE IGNORE utazon_user SET view_history=%s WHERE mc_uuid=%s"
            cursor.execute(sql, (json.dumps(result), mc_uuid,))
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
            sql = "SELECT * FROM utazon_item ORDER BY `id` DESC LIMIT 4"
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


def get_special_feature():
    return SpecialFeature.objects.all()