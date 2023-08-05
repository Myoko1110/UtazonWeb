import datetime
import requests

import config.DBManager
import config.settings as settings


class is_session:
    """
    セッションが有効か確認

    引数:
        request: Djangoのrequestオブジェクト
    """
    def __init__(self, request):
        self.request = request
        self.valid = False
        self.expire = False
        self.invalid = False

        session = self.request.COOKIES

        # 一つずつ処理
        for child in session:
            if child.startswith('_Secure-'):

                result = config.DBManager.get_session(child, session[child])

                # EmptySetを判定
                if not result:
                    # 未ログイン処理
                    continue
                else:
                    # 有効期限の確認
                    now = datetime.datetime.now()
                    if now > result[5]:
                        config.DBManager.delete_session(child)
                        # 期限切れの処理
                        self.expire = True
                        return

                    # 既ログイン処理
                    self.valid = True
                    return
        else:
            if "LOGIN_STATUS" in session and session["LOGIN_STATUS"]:
                # 期限切れの処理
                self.expire = True

            # 未ログイン処理
            self.invalid = True


class get_user_info:
    """
    ユーザー情報を取得する

    引数:
        get_user_info.from_uuid:
            mc_uuid: MCのUUID

        get_user_info.from_session:
            request: DjangoのHttpRequestオブジェクト
    """
    class from_uuid:
        def __init__(self, mc_uuid):
            self.mc_uuid = mc_uuid

        def all(self):
            profile = requests.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{self.mc_uuid}').json()

            # mc_idを取得
            mc_id = profile["name"]

            # discord_idを取得
            discord_id = config.DBManager.get_discord_id(self.mc_uuid)

            return {
                "mc_id": mc_id,
                "discord_id": discord_id,
            }

        def mc_id(self):
            profile = requests.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{self.mc_uuid}').json()

            # mc_idを取得
            mc_id = profile["name"]

            return mc_id

        def discord_id(self):
            discord_id = config.DBManager.get_discord_id(self.mc_uuid)
            return discord_id

    class from_session:
        def __init__(self, request):
            self.request = request

        def all(self):
            try:
                session = self.request.COOKIES
            except AttributeError as exc:
                raise TypeError("Pass a Request object on request argument.") from exc

            for child in session:
                if child.startswith('_Secure-'):

                    result = config.DBManager.get_session(child, session[child])

                    if result is None:
                        continue

                    # uuidを取得
                    mc_uuid = result[2]

                    profile = get_user_info.from_uuid(mc_uuid).all()

                    cart = len(config.DBManager.get_utazon_user_cart(mc_uuid))
                    point = config.DBManager.get_utazon_user_point(mc_uuid)

                    return {
                        "discord_id": profile["discord_id"],
                        "mc_uuid": mc_uuid,
                        "mc_id": profile["mc_id"],
                        "user_cart": cart,
                        "point": point,
                    }

            else:
                return False

        def mc_id(self):
            try:
                session = self.request.COOKIES
            except AttributeError as exc:
                raise TypeError("Pass a Request object on request argument.") from exc

            for child in session:
                if child.startswith('_Secure-'):

                    result = config.DBManager.get_session(child, session[child])

                    if result is None:
                        continue

                    # uuidを取得
                    mc_uuid = result[2]

                    mc_id = get_user_info.from_uuid(mc_uuid).mc_id

                    return mc_id

            else:
                return False

        def mc_uuid(self):
            try:
                session = self.request.COOKIES
            except AttributeError as exc:
                raise TypeError("Pass a Request object on request argument.") from exc

            for child in session:
                if child.startswith('_Secure-'):

                    result = config.DBManager.get_session(child, session[child])

                    if result is None:
                        continue

                    # uuidを取得
                    mc_uuid = result[2]

                    return mc_uuid

            else:
                return False

        def discord_id(self):
            try:
                session = self.request.COOKIES
            except AttributeError as exc:
                raise TypeError("Pass a Request object on request argument.") from exc

            for child in session:
                if child.startswith('_Secure-'):

                    result = config.DBManager.get_session(child, session[child])

                    if result is None:
                        continue

                    # uuidを取得
                    mc_uuid = result[2]

                    discord_id = get_user_info.from_uuid(mc_uuid).discord_id()

                    return discord_id

            else:
                return False


class get_category:
    """
    セッションから親カテゴリを取得

    引数:
        .from_en:
            value: 英語セッション名
        .from_jp:
            value: 日本語セッション名
    """
    def __init__(self, value):
        self.value = value

    def from_en(self):
        categories = settings.CATEGORIES
        for category, value in categories.items():
            if category == self.value:
                list = {
                    "jp": value["JAPANESE"],
                    "en": self.value,
                    "parent": None,
                }
                return list
            for en, jp in value.items():
                if en == self.value:
                    parent_jp = categories[category]["JAPANESE"]
                    list = {
                        "jp": jp,
                        "en": self.value,
                        "parent": {
                            "en": category,
                            "jp": parent_jp,
                        },
                    }
                    return list
        else:
            return False

    def from_jp(self):
        categories = settings.CATEGORIES
        for category, value in categories.items():
            if value == self.value:
                list = {
                    "jp": self.value,
                    "en": category,
                    "parent": None,
                }
                return list
            for en, jp in value.items():
                if en == "JAPANESE":
                    continue
                if jp == self.value:
                    parent_jp = categories[category]["JAPANESE"]
                    list = {
                        "jp": self.value,
                        "en": en,
                        "parent": {
                            "en": category,
                            "jp": parent_jp,
                        },
                    }
                    return list
        else:
            return False
