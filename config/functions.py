import datetime
import requests
import config.DBManager


def is_session_valid(request):
    """
    セッションが有効か確認
    """

    # Cookie取得
    session = request.COOKIES

    # 一つずつ処理
    for child in session:
        if child.startswith('_Secure-'):

            result = config.DBManager.get_session(child, session[child])

            # EmptySetを判定
            if result is None or len(result) == 0:
                # 未ログイン処理
                continue
            else:
                # 有効期限の確認
                now = datetime.datetime.now()
                if now > result[5]:
                    config.DBManager.delete_session(child)
                    # 期限切れの処理
                    return [False, True, False]

                # 既ログイン処理
                return [True, False, False]
    else:
        if "LOGIN_STATUS" in session and session["LOGIN_STATUS"]:
            # 期限切れの処理
            return [False, True, False]

        # 未ログイン処理
        return [False, False, True]


def get_userinfo_from_uuid(uuid):
    """
    uuidからのユーザー情報の取得
    """

    # discord_idのレコードを取得
    discord_id = config.DBManager.get_discord_id(uuid)

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

    # 一つずつ処理
    for child in session:
        if child.startswith('_Secure-'):

            result = config.DBManager.get_session(child, session[child])

            if result is None:
                continue

            # uuidを取得
            mc_uuid = result[2]

            profile = get_userinfo_from_uuid(mc_uuid)

            cart = len(config.DBManager.get_utazon_user_cart(mc_uuid))

            return {"discord_id": profile["discord_id"], "mc_uuid": mc_uuid, "mc_id": profile["mc_id"],
                    "user_cart": cart}

    else:
        return False
