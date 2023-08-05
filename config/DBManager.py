import datetime
import json
import random

import mysql.connector

import config.settings as settings


def get_utazon_user_cart(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT * FROM utazon_user WHERE mc_uuid=%s"
            cursor.execute(sql, (mc_uuid,))

            # mc_uuidのレコードを取得
            result = cursor.fetchone()

            if not result:
                return False
    return json.loads(result[1])


def get_utazon_user_later(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT * FROM utazon_user WHERE mc_uuid=%s"
            cursor.execute(sql, (mc_uuid,))

            # mc_uuidのレコードを取得
            result = cursor.fetchone()

            if not result:
                return False
    return json.loads(result[2])


def get_item(item_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT * FROM utazon_item WHERE item_id=%s"
            cursor.execute(sql, (item_id,))

            # item_idのレコードを取得
            result = cursor.fetchone()

            if not result:
                return False
    return result


def get_utazon_user_point(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT * FROM utazon_user WHERE mc_uuid=%s"
            cursor.execute(sql, (mc_uuid,))

            # mc_uuidのレコードを取得
            result = cursor.fetchone()

            if not result:
                return False
    return result[3]


def deposit_utazon_user_point(mc_uuid, amount):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT * FROM utazon_user WHERE mc_uuid=%s"
            cursor.execute(sql, (mc_uuid,))

            # mc_uuidのレコードを取得
            result = cursor.fetchone()

            if not result:
                return False
            point = result[3] - amount
            print(point)

            sql = "UPDATE IGNORE utazon_user SET point=%s WHERE mc_uuid=%s"

            cursor.execute(sql, (point, mc_uuid))
            cnx.commit()
    return True


def get_item_from_category(cat_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT * FROM utazon_item WHERE category=%s"
            cursor.execute(sql, (cat_id,))

            # cat_idのレコードを取得
            result = cursor.fetchall()

            if not result:
                return False
    return result


def search_item(item_query):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT * FROM utazon_item WHERE item_name LIKE %s"
            cursor.execute(sql, (f"%{item_query}%",))

            # mc_uuidのレコードを取得
            result = list(cursor.fetchall())
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

            cursor.execute(sql, (value ,item_id,))
            cnx.commit()
    return True


def get_session(session_id, session_val):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])

    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT * FROM utazon_session WHERE session_id=%s and session_val=%s"
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

            sql = "SELECT * FROM linked WHERE discord_id=%s"
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


def add_order(items, mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])

    with cnx:
        with cnx.cursor() as cursor:

            while True:
                try:
                    # お届け時間を計算
                    now = datetime.datetime.now().replace(microsecond=0)
                    if now > datetime.datetime.strptime('13:00:00', '%H:%M:%S'):
                        rand_time = now.replace(hour=random.randint(8, 18), minute=random.randint(1, 59), second=0,
                                                microsecond=0) + datetime.timedelta(days=2)
                    else:
                        rand_time = now.replace(hour=random.randint(8, 18), minute=random.randint(1, 59), second=0,
                                                microsecond=0) + datetime.timedelta(days=1)
                    order_id = f"U{str(random.randint(0, 999)).zfill(3)}-{str(random.randint(0, 999999)).zfill(6)}-{str(random.randint(0, 999999)).zfill(6)}"

                    sql = """INSERT IGNORE INTO `utazon_order` (  
                                         `mc_uuid`, `order_item`, `delivery_time` ,`order_time`, `order_id`
                                         ) VALUES (%s, %s, %s, %s, %s)"""
                    cursor.execute(sql, (mc_uuid, items, rand_time, now, order_id))
                except mysql.connector.Error as err:
                    if err.errno == 1062:
                        continue
                    else:
                        raise err
                else:
                    cnx.commit()
                    return order_id, rand_time


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
            with cnx.cursor() as cursor:
                sql = "SELECT * FROM `utazon_order` WHERE order_id=%s"
                cursor.execute(sql, (order_id,))

                result = cursor.fetchone()
                return result

def get_utazon_user_history(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT * FROM utazon_user WHERE mc_uuid=%s"
            cursor.execute(sql, (mc_uuid,))

            # mc_uuidのレコードを取得
            result = cursor.fetchone()

            if not result:
                return False
    return json.loads(result[4])


def update_user_history(mc_uuid, value):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE IGNORE utazon_user SET history=%s WHERE mc_uuid=%s"
            cursor.execute(sql, (value, mc_uuid,))
            cnx.commit()

    return True
