import mysql.connector
import datetime
import requests
import config.settings as settings
import logging
import json


def is_session_valid(request):
    """
    セッションが有効か確認
    """

    # Cookie取得
    session = request.COOKIES
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG)

    # dbに接続
    with cnx:
        with cnx.cursor() as cursor:

            # 一つずつ処理
            for child in session:
                if child.startswith('_Secure-'):

                    sql = "SELECT * FROM session WHERE session_id=%s"
                    cursor.execute(sql, (child,))

                    # session_idのレコードを取得
                    result = cursor.fetchone()

                    # EmptySetを判定
                    if result is None or len(result) == 0 or session[child] != result[1]:
                        # 未ログイン処理
                        continue
                    else:

                        cursor.close()
                        cnx.commit()

                        # 有効期限の確認
                        now = datetime.datetime.now()
                        if now > result[5]:

                            # 期限切れの処理
                            return [False, True, False]

                        # 既ログイン処理
                        return [True, False, False]
            else:
                cursor.close()
                cnx.commit()

                if "LOGIN_STATUS" in session and session["LOGIN_STATUS"]:

                    # 期限切れの処理
                    return [False, True, False]

                # 未ログイン処理
                return [False, False, True]


def get_userinfo_from_uuid(uuid):
    """
    uuidからのユーザー情報の取得
    """
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG)

    with cnx:
        with cnx.cursor() as cursor:

            sql = "SELECT * FROM linked WHERE mc_uuid=%s"
            cursor.execute(sql, (uuid,))

            # discord_idのレコードを取得
            discord_id = cursor.fetchone()[1]

            # mc関係のprofileを取得
            profile = requests.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}').json()

            # mc_idを取得
            mc_id = profile["name"]

            return {"discord_id": discord_id, "mc_id": mc_id}


def get_userinfo_from_session(request):
    """
    セッションからのユーザー情報の取得
    """

    # Cookie取得
    session = request.COOKIES
    cnx = mysql.connector.connect(**settings.DATABASE_CONFIG)

    # dbに接続
    with cnx:
        with cnx.cursor() as cursor:

            # 一つずつ処理
            for child in session:
                if child.startswith('_Secure-'):

                    sql = "SELECT * FROM session WHERE session_id=%s and session_val=%s"
                    cursor.execute(sql, (child, session[child],))

                    # session_idのレコードを取得
                    result = cursor.fetchone()

                    if result is None:
                        continue

                    # uuidを取得
                    mc_uuid = result[2]

                    profile = get_userinfo_from_uuid(mc_uuid)

                    sql = "SELECT * FROM user WHERE mc_uuid=%s"
                    cursor.execute(sql, (mc_uuid,))

                    # mc_uuidのレコードを取得
                    result = cursor.fetchone()

                    cart = len(json.loads(result[1]))

    return {"discord_id": profile["discord_id"], "mc_uuid": mc_uuid, "mc_id": profile["mc_id"], "user_cart": cart}
