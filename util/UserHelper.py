import datetime
import json

import requests

import util


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
            discord_id = util.DatabaseHelper.get_discord_id(self.mc_uuid)

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

                    result = util.DatabaseHelper.get_session(child, session[child])

                    if result is None:
                        continue

                    # uuidを取得
                    self.mc_uuid = result["mc_uuid"]

                    profile = get_info.from_uuid(self.mc_uuid)

                    self.user_cart = len(util.DatabaseHelper.get_user_cart(self.mc_uuid))
                    self.point = util.DatabaseHelper.get_user_point(self.mc_uuid)

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

    view_history = util.DatabaseHelper.get_user_view_history_four(mc_uuid)
    view_history_obj = []

    if view_history:
        try:
            for i in range(4):
                item_id = view_history[i]["item_id"]
                item_obj = util.DatabaseHelper.get_item(item_id)
                if not item_obj:
                    continue
                item_obj["image"] = json.loads(item_obj["image"])
                view_history_obj.append(item_obj)

        except IndexError:
            pass

    return view_history_obj


def get_history(mc_uuid):
    order_history = util.DatabaseHelper.get_user_history(mc_uuid)

    for i in range(len(order_history)):
        # amountをフォーマット
        order_history[i]["amount"] = f"{float(order_history[i]['amount']):,.2f}"

        # アイテム情報を取得
        order_history[i]["order_item"] = json.loads(order_history[i]["order_item"])
        order_history_child = util.ItemHelper.get_item.cart_list(order_history[i]["order_item"])
        order_history[i]["order_item"] = order_history_child.item_list

    if not order_history:
        return False
    else:
        return order_history
