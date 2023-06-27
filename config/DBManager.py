import mysql.connector
import config.settings as settings
import json


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
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])

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


def save_session(session_id, session_value, mc_uuid, access_token, now, expires):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    
    with cnx:
        with cnx.cursor() as cursor:
            while True:
                try:
                    # sessionテーブルに保存
                    sql = """INSERT INTO `utazon_session` (
                             `session_id`, `session_val`, `mc_uuid`, `access_token`, `login_date`, `expires`
                             ) VALUES (%s, %s, %s, %s, %s, %s)"""
                    cursor.execute(sql, (session_id, session_value, mc_uuid, access_token, now, expires))

                except mysql.connector.Error as err:
                    if err.errno == 1062:
                        continue
                else:
                    break
            cnx.commit()
    return True