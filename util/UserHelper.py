import json

import requests

import config.DBManager


class get_info:
    """
    ユーザの情報を取得します
    """

    class from_uuid:
        """
        UUIDからユーザの情報を取得します

        :param mc_uuid: MinecraftのUUID
        """

        def __init__(self, mc_uuid):
            self.mc_uuid = mc_uuid

            profile = requests.get(
                f"https://sessionserver.mojang.com/session/minecraft/profile/{self.mc_uuid}").json()

            # mc_idを取得
            mc_id = profile["name"]

            # discord_idを取得
            discord_id = config.DBManager.get_discord_id(self.mc_uuid)

            self.mc_id = mc_id
            self.discord_id = discord_id

    class from_session:
        """
        セッションからユーザの情報を取得します

        :param request: DjangoのHttpRequestオブジェクト
        """

        def __init__(self, request):
            self.request = request

            try:
                session = self.request.COOKIES
            except AttributeError as exc:
                raise TypeError("request引数にはDjangoのHttpRequestオブジェクトを入れて下さい") from exc

            for child in session:
                if child.startswith("_Secure-"):

                    result = config.DBManager.get_session(child, session[child])

                    if result is None:
                        continue

                    # uuidを取得
                    self.mc_uuid = result[2]

                    profile = get_info.from_uuid(self.mc_uuid)

                    self.user_cart = len(config.DBManager.get_user_cart(self.mc_uuid))
                    self.point = config.DBManager.get_user_point(self.mc_uuid)

                    self.discord_id = profile.discord_id
                    self.mc_id = profile.mc_id

                    break

            else:
                self.mc_uuid = None
                self.user_cart = None
                self.point = None

                self.discord_id = None
                self.mc_id = None


def get_view_history(mc_uuid):
    """
    ユーザーの閲覧履歴を取得します

    :param mc_uuid: MinecraftのUUID
    :return: 閲覧履歴
    """

    view_history = config.DBManager.get_user_view_history(mc_uuid)
    view_history_obj = []

    if view_history:
        try:
            for i in range(4):
                item_id = view_history[i]
                item_obj = config.DBManager.get_item(item_id)
                item_obj[3] = json.loads(item_obj[3])
                view_history_obj.append(item_obj)

        except IndexError:
            pass

    return view_history_obj
