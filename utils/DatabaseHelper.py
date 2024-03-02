import datetime
from typing import Union

import mysql.connector

from config import settings
from item.models import Featured


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
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def get_item_stack(item_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM utazon_itemstack WHERE item_id=%s"
            cursor.execute(sql, (item_id,))
            result = cursor.fetchone()
    return result


def get_cart(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = """SELECT * FROM utazon_cart WHERE mc_uuid=%s ORDER BY created_at DESC"""
            cursor.execute(sql, (mc_uuid,))
            result = cursor.fetchall()
    return result


def add_cart(mc_uuid, item_id, qty):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            now = datetime.datetime.now()

            sql = """INSERT INTO utazon_cart (mc_uuid, item_id, quantity, created_at)
                     VALUES (%s, %s, %s, %s)
                     ON DUPLICATE KEY UPDATE quantity=quantity+VALUES(quantity)"""
            cursor.execute(sql, (mc_uuid, item_id, qty, now))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def reset_cart(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = """DELETE FROM utazon_cart WHERE mc_uuid=%s"""
            cursor.execute(sql, (mc_uuid,))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def delete_cart(mc_uuid, item_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "DELETE FROM utazon_cart WHERE mc_uuid=%s AND item_id=%s"
            cursor.execute(sql, (mc_uuid, item_id))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def update_cart(mc_uuid, item_id, qty):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE utazon_cart SET quantity=%s WHERE mc_uuid=%s AND item_id=%s"
            cursor.execute(sql, (qty, mc_uuid, item_id))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def get_later(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = """SELECT * FROM utazon_later WHERE mc_uuid=%s ORDER BY created_at DESC"""
            cursor.execute(sql, (mc_uuid,))
            result = cursor.fetchall()
    return result


def add_later(mc_uuid, item_id, qty):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            now = datetime.datetime.now()

            sql = """INSERT INTO utazon_later (mc_uuid, item_id, quantity, created_at)
                     VALUES (%s, %s, %s, %s)
                     ON DUPLICATE KEY UPDATE quantity=quantity+VALUES(quantity)"""
            cursor.execute(sql, (mc_uuid, item_id, qty, now))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def delete_later(mc_uuid, item_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "DELETE FROM utazon_later WHERE mc_uuid=%s AND item_id=%s"
            cursor.execute(sql, (mc_uuid, item_id))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def update_later(mc_uuid, item_id, qty):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE utazon_later SET quantity=%s WHERE mc_uuid=%s AND item_id=%s"
            cursor.execute(sql, (qty, mc_uuid, item_id))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def get_item(item_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = """SELECT utazon_item.sale_id, utazon_item.item_id, utazon_item.item_name,
                            utazon_item.price, utazon_item.image, utazon_item.kind, utazon_item.detail, utazon_item.category,
                            utazon_item.sold_count, utazon_item.mc_uuid, utazon_item.search_keyword,
                            utazon_item.created_at, utazon_item.updated_at, utazon_item.status,
                            utazon_sale.sale_status, utazon_sale.discount_rate, utazon_sale.sale_start,
                            utazon_sale.sale_end, utazon_sale.is_pride_only FROM utazon_item
                         LEFT JOIN utazon_sale ON utazon_item.item_id = utazon_sale.item_id
                         WHERE utazon_item.item_id=%s"""
            cursor.execute(sql, (item_id,))

            # item_idのレコードを取得
            result = cursor.fetchone()
    return result


def get_item_by_list(id_list):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            l = ", ".join(str(i) for i in id_list)

            sql = f"""SELECT utazon_item.sale_id, utazon_item.item_id, utazon_item.item_name,
                            utazon_item.price, utazon_item.image, utazon_item.kind, utazon_item.detail, utazon_item.category,
                            utazon_item.sold_count, utazon_item.mc_uuid, utazon_item.search_keyword,
                            utazon_item.created_at, utazon_item.updated_at, utazon_item.status,
                            utazon_sale.sale_status, utazon_sale.discount_rate, utazon_sale.sale_start,
                            utazon_sale.sale_end, utazon_sale.is_pride_only FROM utazon_item
                         LEFT JOIN utazon_sale ON utazon_item.item_id = utazon_sale.item_id
                         WHERE utazon_item.item_id IN ({l})
                         ORDER BY FIELD(utazon_item.item_id, {l})"""
            cursor.execute(sql)

            # item_idのレコードを取得
            result = cursor.fetchall()
    return result


def get_available_item(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = """SELECT utazon_item.sale_id, utazon_item.item_id, utazon_item.item_name,
                            utazon_item.price, utazon_item.image, utazon_item.kind, utazon_item.detail, utazon_item.category,
                            utazon_item.sold_count, utazon_item.mc_uuid, utazon_item.search_keyword,
                            utazon_item.created_at, utazon_item.updated_at, utazon_item.status,
                            utazon_sale.sale_status, utazon_sale.discount_rate, utazon_sale.sale_start,
                            utazon_sale.sale_end, utazon_sale.is_pride_only FROM utazon_item
                         LEFT JOIN utazon_sale ON utazon_item.item_id = utazon_sale.item_id
                         WHERE utazon_item.mc_uuid=%s AND utazon_item.status=TRUE"""
            cursor.execute(sql, (mc_uuid,))

            result = cursor.fetchall()
    return result


def get_unavailable_item(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = """SELECT utazon_item.sale_id, utazon_item.item_id, utazon_item.item_name,
                            utazon_item.price, utazon_item.image, utazon_item.kind, utazon_item.detail, utazon_item.category,
                            utazon_item.sold_count, utazon_item.mc_uuid, utazon_item.search_keyword,
                            utazon_item.created_at, utazon_item.updated_at, utazon_item.status,
                            utazon_sale.sale_status, utazon_sale.discount_rate, utazon_sale.sale_start,
                            utazon_sale.sale_end, utazon_sale.is_pride_only FROM utazon_item
                         LEFT JOIN utazon_sale ON utazon_item.item_id = utazon_sale.item_id
                         WHERE utazon_item.mc_uuid=%s AND utazon_item.status=FALSE"""
            cursor.execute(sql, (mc_uuid,))

            result = cursor.fetchall()
    return result


def get_discounting_item():
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = """SELECT utazon_item.sale_id, utazon_item.item_id, utazon_item.item_name,
                            utazon_item.price, utazon_item.image, utazon_item.kind, utazon_item.detail, utazon_item.category,
                            utazon_item.sold_count, utazon_item.mc_uuid, utazon_item.search_keyword,
                            utazon_item.created_at, utazon_item.updated_at, utazon_item.status,
                            utazon_sale.sale_status, utazon_sale.discount_rate, utazon_sale.sale_start,
                            utazon_sale.sale_end, utazon_sale.is_pride_only FROM utazon_item
                         LEFT JOIN utazon_sale ON utazon_item.item_id = utazon_sale.item_id
                         WHERE utazon_sale.sale_status=TRUE"""
            cursor.execute(sql)

            result = cursor.fetchall()
    return result


def get_active_item():
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = """SELECT utazon_item.sale_id, utazon_item.item_id, utazon_item.item_name,
                            utazon_item.price, utazon_item.image, utazon_item.kind, utazon_item.detail, utazon_item.category,
                            utazon_item.sold_count, utazon_item.mc_uuid, utazon_item.search_keyword,
                            utazon_item.created_at, utazon_item.updated_at, utazon_item.status,
                            utazon_sale.sale_status, utazon_sale.discount_rate, utazon_sale.sale_start,
                            utazon_sale.sale_end, utazon_sale.is_pride_only FROM utazon_item
                         LEFT JOIN utazon_sale ON utazon_item.item_id = utazon_sale.item_id
                         WHERE utazon_item.status=TRUE"""
            cursor.execute(sql)

            result = cursor.fetchall()
    return result


def update_item(item_id, item_name, price, image, about, detail, category):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            now = datetime.datetime.now()

            sql = "UPDATE utazon_item SET item_name=%s, price=%s, image=%s, kind=%s, detail=%s, category=%s, updated_at=%s WHERE item_id=%s"
            cursor.execute(sql, (item_name, price, image, about, detail, category, now, item_id))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def search_item(item_query: str, category: Union['utils.Category', None]):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            result = []
            if category:
                if category.is_parent:
                    c = category.get_child()
                else:
                    c = [category]

                for i in c:

                    sql = """SELECT utazon_item.sale_id, utazon_item.item_id, utazon_item.item_name,
                            utazon_item.price, utazon_item.image, utazon_item.kind, utazon_item.detail, utazon_item.category,
                            utazon_item.sold_count, utazon_item.mc_uuid, utazon_item.search_keyword,
                            utazon_item.created_at, utazon_item.updated_at, utazon_item.status,
                            utazon_sale.sale_status, utazon_sale.discount_rate, utazon_sale.sale_start,
                            utazon_sale.sale_end, utazon_sale.is_pride_only FROM utazon_item
                                 LEFT JOIN utazon_sale ON utazon_item.item_id = utazon_sale.item_id
                                 WHERE MATCH(utazon_item.item_name) AGAINST(%s)
                                     AND utazon_item.category=%s AND utazon_item.status=TRUE"""
                    for j in item_query.split("+"):
                        sql += f" OR JSON_CONTAINS(search_keyword, '\"{j}\"', '$') AND status=TRUE"

                    sql += " ORDER BY sold_count DESC, item_name"
                    cursor.execute(sql, (item_query, i.english))

                    # mc_uuidのレコードを取得
                    fetch = cursor.fetchall()
                    for k in fetch:
                        result.append(k)

            else:
                sql = """SELECT utazon_item.sale_id, utazon_item.item_id, utazon_item.item_name,
                            utazon_item.price, utazon_item.image, utazon_item.kind, utazon_item.detail, utazon_item.category,
                            utazon_item.sold_count, utazon_item.mc_uuid, utazon_item.search_keyword,
                            utazon_item.created_at, utazon_item.updated_at, utazon_item.status,
                            utazon_sale.sale_status, utazon_sale.discount_rate, utazon_sale.sale_start,
                            utazon_sale.sale_end, utazon_sale.is_pride_only FROM utazon_item
                             LEFT JOIN utazon_sale ON utazon_item.item_id = utazon_sale.item_id
                             WHERE MATCH(utazon_item.item_name) AGAINST(%s)
                                 AND utazon_item.status=TRUE"""

                for i in item_query.split("+"):
                    sql += f" OR JSON_CONTAINS(search_keyword, '\"{i}\"', '$') AND status=TRUE"

                sql += " ORDER BY sold_count DESC, item_name"
                cursor.execute(sql, (item_query,))

                # mc_uuidのレコードを取得
                fetch = cursor.fetchall()
                for k in fetch:
                    result.append(k)

    return result


def get_item_by_category(cat_en):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = """SELECT utazon_item.sale_id, utazon_item.item_id, utazon_item.item_name,
                            utazon_item.price, utazon_item.image, utazon_item.kind, utazon_item.detail, utazon_item.category,
                            utazon_item.sold_count, utazon_item.mc_uuid, utazon_item.search_keyword,
                            utazon_item.created_at, utazon_item.updated_at, utazon_item.status,
                            utazon_sale.sale_status, utazon_sale.discount_rate, utazon_sale.sale_start,
                            utazon_sale.sale_end, utazon_sale.is_pride_only FROM utazon_item
                     LEFT JOIN utazon_sale ON utazon_item.item_id = utazon_sale.item_id
                     WHERE category=%s AND status=TRUE"""
            cursor.execute(sql, (cat_en,))

            result = cursor.fetchall()
    return result


def set_sale(item_id, discount_rate, start, end, pride_only):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = """INSERT INTO `utazon_sale`
                         (item_id, sale_status, discount_rate, sale_start, sale_end, is_pride_only)
                     VALUES (%s, TRUE, %s, %s, %s, %s)
                     ON DUPLICATE KEY UPDATE
                         discount_rate=VALUES(discount_rate), sale_status=TRUE, sale_start=VALUES(sale_start), sale_end=VALUES(sale_end), is_pride_only=VALUES(is_pride_only)"""
            cursor.execute(sql, (item_id, discount_rate, start, end, pride_only))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def end_sale(item_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE utazon_sale SET sale_status=FALSE WHERE item_id=%s"

            cursor.execute(sql, (item_id,))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def add_review(mc_uuid, item_id, star, title, value, type):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            now = datetime.datetime.now()

            sql = """INSERT INTO `utazon_review`
                         (item_id, created_at, updated_at, rating, title, value, helpful_votes, mc_uuid, type)
                     VALUES (%s, %s, %s, %s, %s, %s, 0, %s, %s)
                     ON DUPLICATE KEY UPDATE
                         rating=VALUES(rating), title=VALUES(title), value=VALUES(value), type=VALUES(type), updated_at=VALUES(updated_at)"""
            cursor.execute(sql, (item_id, now, now, star, title, value, mc_uuid, type))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def update_review(mc_uuid, item_id, star, title, value):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            now = datetime.datetime.now()

            sql = """UPDATE utazon_review SET rating=%s, title=%s, value=%s, updated_at=%s
                     WHERE mc_uuid=%s AND item_id=%s"""

            cursor.execute(sql, (star, title, value, now, mc_uuid, item_id))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def get_review(item_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = """SELECT * FROM utazon_review WHERE item_id=%s ORDER BY updated_at DESC"""
            cursor.execute(sql, (item_id,))
            result = cursor.fetchall()
    return result


def get_review_by_mc_uuid(mc_uuid, item_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = """SELECT * FROM utazon_review WHERE mc_uuid=%s AND item_id=%s"""
            cursor.execute(sql, (mc_uuid, item_id))
            result = cursor.fetchone()
    return result


def check_review_and_rating(mc_uuid, item_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = """SELECT EXISTS(SELECT NULL FROM utazon_review
                     WHERE mc_uuid=%s AND item_id=%s)"""
            cursor.execute(sql, (mc_uuid, item_id))

            result = cursor.fetchone()
    return result


def check_review(mc_uuid, item_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = """SELECT EXISTS(SELECT NULL FROM utazon_review
                     WHERE mc_uuid=%s AND item_id=%s AND type='REVIEW')"""
            cursor.execute(sql, (mc_uuid, item_id))

            result = cursor.fetchone()
    return result


def check_rating(mc_uuid, item_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = """SELECT EXISTS(SELECT NULL FROM utazon_review
                     WHERE mc_uuid=%s AND item_id=%s AND type='RATING')"""
            cursor.execute(sql, (mc_uuid, item_id))

            result = cursor.fetchone()
    return result


def helpful_review(item_id, review_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE utazon_review SET helpful_votes=helpful_votes+1 WHERE item_id=%s AND id=%s"

            cursor.execute(sql, (item_id, review_id))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def get_orders(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM utazon_order WHERE mc_uuid=%s ORDER BY ordered_at DESC"
            cursor.execute(sql, (mc_uuid,))

            result = cursor.fetchall()
    return result


def get_all_orders():
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM utazon_order WHERE status=TRUE"
            cursor.execute(sql)

            result = cursor.fetchall()
    return result


def get_point(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT point FROM utazon_point WHERE mc_uuid=%s ORDER BY created_at DESC LIMIT 1"
            cursor.execute(sql, (mc_uuid,))

            result = cursor.fetchone()
    return result


def deduct_points(mc_uuid, amount):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            now = datetime.datetime.now()

            sql = """INSERT INTO utazon_point (mc_uuid, point, created_at)
                     VALUES(%s, (SELECT point FROM utazon_point WHERE mc_uuid=VALUES(mc_uuid) ORDER BY created_at DESC LIMIT 1) - %s, %s)"""
            cursor.execute(sql, (mc_uuid, amount, now))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def add_points(mc_uuid, amount):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            now = datetime.datetime.now()

            sql = """INSERT INTO utazon_point (mc_uuid, point, created_at)
                     SELECT mc_uuid, (point + %s), %s
                     FROM(
                         SELECT mc_uuid, point
                         FROM utazon_point
                         WHERE mc_uuid = %s
                         ORDER BY created_at DESC
                         LIMIT 1
                     ) as temp
                     """
            cursor.execute(sql, (amount, now, mc_uuid))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def initialize_browsing_history(mc_uuid, item_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            now = datetime.datetime.now()

            sql = """INSERT INTO utazon_browsinghistory (mc_uuid, item_id, browsed_at, browse_count, browse_duration)
                     VALUES (%s, %s, %s, 1, 0)
                     ON DUPLICATE KEY UPDATE browse_count=browse_count+1, browsed_at=VALUES(browsed_at)"""
            cursor.execute(sql, (mc_uuid, item_id, now))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def update_browsing_history(mc_uuid, item_id, duration):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = """UPDATE utazon_browsingHistory SET browse_duration = browse_duration + %s
                     WHERE mc_uuid=%s AND item_id=%s"""
            cursor.execute(sql, (duration, mc_uuid, item_id,))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def get_browsing_history(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = """SELECT item_id FROM utazon_browsinghistory
                     WHERE mc_uuid=%s ORDER BY browsed_at DESC"""""
            cursor.execute(sql, (mc_uuid,))

            result = cursor.fetchall()
    return result


def get_browsing_history_recently(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = """SELECT item_id FROM utazon_browsinghistory
                     WHERE mc_uuid=%s ORDER BY browsed_at DESC LIMIT 4"""""
            cursor.execute(sql, (mc_uuid,))

            result = cursor.fetchall()
    return result


def get_session(session_id, session_val):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM utazon_session WHERE session_id=%s AND session_val=%s"
            cursor.execute(sql, (session_id, session_val,))

            # session_idのレコードを取得
            result = cursor.fetchone()
    return result


def get_discord_id(uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["linked"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT discord_id FROM linked WHERE mc_uuid=%s"
            cursor.execute(sql, (uuid,))

            result = cursor.fetchone()
    return result


def get_mc_uuid(discord_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["linked"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT mc_uuid FROM linked WHERE discord_id=%s"
            cursor.execute(sql, (discord_id,))

            result = cursor.fetchone()
    return result


def get_stock(item_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT stock FROM utazon_itemstack WHERE item_id=%s"
            cursor.execute(sql, (item_id,))
            result = cursor.fetchone()
    return result


def reduce_stock(item_id, qty):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE utazon_itemstack SET stock = stock - %s WHERE item_id=%s"
            cursor.execute(sql, (qty, item_id,))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def increase_stock(item_id, amount):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE utazon_itemstack SET stock = stock + %s WHERE item_id=%s"
            cursor.execute(sql, (amount, item_id,))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def add_revenues(mc_uuid, item_id, item_price, qty, total, seller):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            now = datetime.datetime.now()

            sql = """INSERT INTO utazon_revenues (mc_uuid, item_id, item_price, qty, total, bought_at, seller_uuid)
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (mc_uuid, item_id, item_price, qty, total, now, seller))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def delete_revenues(seller):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            three_days_ago = datetime.datetime.now().replace(minute=0, second=0,
                                                             microsecond=0) - datetime.timedelta(
                days=3)

            sql = "DELETE FROM utazon_revenues WHERE bought_at < %s AND seller_uuid=%s"
            cursor.execute(sql, (three_days_ago, seller))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


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


def increase_sold_count(item_id, qty):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE utazon_item SET sold_count = sold_count + %s WHERE item_id=%s"
            cursor.execute(sql, (qty, item_id))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def add_order(mc_uuid, items, order_id, ship_time, delivery_time, amount, used_point):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            now = datetime.datetime.now()
            while True:
                try:
                    sql = """INSERT IGNORE INTO `utazon_order` (  
                                         `mc_uuid`, `order_item`, `order_id`, `ordered_at`, `ships_at`, `delivers_at`,
                                         `amount`, `used_point`, `status`, `canceled`, `dm_sent`
                                         ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE, FALSE, FALSE)"""
                    cursor.execute(sql, (
                        mc_uuid, items, order_id, now, ship_time, delivery_time, amount, used_point))
                except mysql.connector.Error as err:
                    if err.errno == 1062:
                        continue
                    else:
                        raise err
                else:
                    affected_rows = cursor.rowcount
                    cnx.commit()

                    if affected_rows > 0:
                        return True
    return False


def get_order(order_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM `utazon_order` WHERE order_id=%s"
            cursor.execute(sql, (order_id,))

            result = cursor.fetchone()
            return result


def cancel_order(order_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE utazon_order SET status = FALSE, canceled = TRUE WHERE order_id=%s"
            cursor.execute(sql, (order_id,))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def redelivery_order(order_id, delivery_time):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE utazon_order SET status=TRUE, error=NULL, delivers_at=%s WHERE order_id=%s"
            cursor.execute(sql, (delivery_time, order_id,))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def get_waiting_stock(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "SELECT value FROM utazon_waitingstock WHERE mc_uuid=%s"
            cursor.execute(sql, (mc_uuid,))
            result = cursor.fetchone()
    return result


def update_waiting_stock(mc_uuid, value):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE utazon_waitingstock SET value=%s WHERE mc_uuid=%s"
            cursor.execute(sql, (value, mc_uuid))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def add_return_stock(mc_uuid, item_id, amount):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            now = datetime.datetime.now()
            hour_ago = now + datetime.timedelta(hours=1)

            sql = """INSERT INTO utazon_returnstock (mc_uuid, item_id, amount, created_at, delivers_at, status)
                     VALUES(%s, %s, %s, %s, %s, TRUE)"""
            cursor.execute(sql, (mc_uuid, item_id, amount, now, hour_ago))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def delete_item(item_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE utazon_item SET status=false WHERE item_id=%s"
            cursor.execute(sql, (item_id,))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def create_item(item_id, item_name, price, image, kind, detail, category, search_keyword, mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    now = datetime.datetime.now()
    with cnx:
        with cnx.cursor() as cursor:
            sql = """INSERT INTO utazon_item (item_id, item_name, price, image, kind, detail,
                     category, sold_count, search_keyword, mc_uuid, created_at, updated_at, status)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, 0, %s, %s, %s, %s, TRUE)"""
            cursor.execute(sql,
                           (item_id, item_name, price, image, kind, detail, category, search_keyword,
                            mc_uuid, now, now))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
    return False


def save_session(session_id, session_value, mc_uuid, access_token, now, expires, logged_IP):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            # すでにidがあるときの対策
            try:
                # sessionテーブルに保存
                sql = """INSERT INTO `utazon_session` (
                         `session_id`, `session_val`, `mc_uuid`, `access_token`,
                         `login_at`, `expires_at`, `logged_IP`
                         ) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (
                    session_id, session_value, mc_uuid, access_token, now, expires, logged_IP))

            except mysql.connector.Error as err:
                if err.errno == 1062:
                    return err
                else:
                    raise err
            else:
                affected_rows = cursor.rowcount
                cnx.commit()

                if affected_rows > 0:
                    return True
    return False


def delete_session(session_id):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:
            sql = "DELETE IGNORE FROM utazon_session WHERE session_id=%s"
            cursor.execute(sql, (session_id,))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
        return False


def get_popular_item():
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = """SELECT utazon_item.sale_id, utazon_item.item_id, utazon_item.item_name,
                            utazon_item.price, utazon_item.image, utazon_item.kind, utazon_item.detail, utazon_item.category,
                            utazon_item.sold_count, utazon_item.mc_uuid, utazon_item.search_keyword,
                            utazon_item.created_at, utazon_item.updated_at, utazon_item.status,
                            utazon_sale.sale_status, utazon_sale.discount_rate, utazon_sale.sale_start,
                            utazon_sale.sale_end, utazon_sale.is_pride_only FROM utazon_item
                     LEFT JOIN utazon_sale ON utazon_item.item_id = utazon_sale.item_id
                     WHERE status=TRUE ORDER BY sold_count DESC LIMIT 4"""
            cursor.execute(sql)
            result = cursor.fetchall()
    return result


def get_latest_item():
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = """SELECT utazon_item.sale_id, utazon_item.item_id, utazon_item.item_name,
                            utazon_item.price, utazon_item.image, utazon_item.kind, utazon_item.detail, utazon_item.category,
                            utazon_item.sold_count, utazon_item.mc_uuid, utazon_item.search_keyword,
                            utazon_item.created_at, utazon_item.updated_at, utazon_item.status,
                            utazon_sale.sale_status, utazon_sale.discount_rate, utazon_sale.sale_start,
                            utazon_sale.sale_end, utazon_sale.is_pride_only FROM utazon_item
                     LEFT JOIN utazon_sale ON utazon_item.item_id = utazon_sale.item_id
                     WHERE status=TRUE ORDER BY sale_id DESC LIMIT 4"""
            cursor.execute(sql)
            result = cursor.fetchall()
    return result


def get_pride(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM utazon_pride WHERE mc_uuid=%s"
            cursor.execute(sql, (mc_uuid,))
            result = cursor.fetchone()
    return result


def get_pride_all():
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM utazon_pride WHERE status=TRUE"
            cursor.execute(sql)
            result = cursor.fetchall()
    return result


def disable_pride(mc_uuid):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:

            sql = "UPDATE utazon_pride SET status=FALSE WHERE mc_uuid=%s"
            cursor.execute(sql, (mc_uuid,))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
        return False


def renew_pride(mc_uuid, expires_at):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor(dictionary=True) as cursor:
            now = datetime.datetime.now()

            sql = "UPDATE utazon_pride SET expires_at=%s, updated_at=%s WHERE mc_uuid=%s"
            cursor.execute(sql, (expires_at, now, mc_uuid,))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
        return False


def register_pride(mc_uuid, plan, auto, expires):
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG["utazon"])
    with cnx:
        with cnx.cursor() as cursor:

            now = datetime.datetime.now()
            sql = """INSERT INTO utazon_pride (mc_uuid, status, plan, registered_at, expires_at, automatically_renew)
                     VALUES (%s, TRUE, %s, %s, %s, %s)
                     ON DUPLICATE KEY UPDATE status=TRUE, plan=VALUES(plan), registered_at=VALUES(registered_at), expires_at=VALUES(expires_at), automatically_renew=VALUES(automatically_renew)"""
            cursor.execute(sql, (mc_uuid, plan, now, expires, auto))
            affected_rows = cursor.rowcount
            cnx.commit()

            if affected_rows > 0:
                return True
        return False

def get_featured_item():
    return Featured.objects.all()
