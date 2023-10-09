import json
from decimal import Decimal
from typing import Union

import requests

import data
import util.DatabaseHelper


class User:
    mc_uuid: str
    point: int

    __cached_mc_id: Union[str, None] = None
    __cached_discord_id: Union[int, None] = None
    __cached_balance: float = 0

    def __init__(self, mc_uuid: str):
        self.mc_uuid = mc_uuid

    def get_mc_id(self) -> Union[str, None]:
        """
        MCIDを取得します

        :return: MCID
        """

        if self.__cached_mc_id:
            return self.__cached_mc_id

        profile = requests.get(
            f"https://sessionserver.mojang.com/session/minecraft/profile/{self.mc_uuid}").json()
        if "name" in profile:

            self.__cached_mc_id = profile["name"]
            return profile["name"]
        else:
            return None

    def get_discord_id(self) -> Union[int, None]:
        """
        DiscordIDを取得します

        :return: DiscordID
        """

        if not self.__cached_discord_id:
            self.__cached_discord_id = util.DatabaseHelper.get_discord_id(self.mc_uuid)[0]
        return self.__cached_discord_id

    def get_point(self) -> float:
        """
        Utazonポイントを取得します

        :return: ポイント
        """

        r = util.DatabaseHelper.get_point(self.mc_uuid)
        if not r:
            return 0

        return r

    def deduct_points(self, amount: int) -> bool:
        """
        ポイントを減らします

        :return: 成功したか
        """

        return util.DatabaseHelper.deduct_points(self.mc_uuid, amount)

    def add_points(self, amount: int) -> bool:
        """
        ポイントを増やします

        :return: 成功したか
        """

        return util.DatabaseHelper.add_points(self.mc_uuid, amount)

    def get_cart(self) -> 'util.Cart':
        """
        Cart型を取得します

        :return: Cart型(アイテムが見つからなかった場合はNoneを挿入)
        """

        return util.Cart.by_mc_uuid(self.mc_uuid)

    def get_cart_length(self):
        """
        カートにある商品数を取得します

        :return: 商品数
        """

        return len(util.DatabaseHelper.get_cart(self.mc_uuid))

    def reset_cart(self) -> bool:
        """
        カートをリセットします

        :return: 成功したか
        """

        return util.DatabaseHelper.reset_cart(self.mc_uuid)

    def get_later(self) -> 'util.Later':
        """
        Later型を取得します

        :return: Later型(アイテムが見つからなければNoneを挿入)
        """

        return util.Later.by_mc_uuid(self.mc_uuid)

    def get_order(self) -> Union['util.Cart', None]:
        """
        Order型を取得します

        :return: Order型
        """

        return util.Order.by_mc_uuid(self.mc_uuid)

    def get_review(self, item: Union[int, 'util.Item']) -> Union['util.Review', None]:
        """
        ユーザーの指定されたアイテムのレビューを取得します

        :param item: アイテムID
        :return: Review型
        """

        if isinstance(item, int):
            return util.Review.by_mc_uuid(self.mc_uuid, item)
        elif isinstance(item, util.Item):
            return util.Review.by_mc_uuid(self.mc_uuid, item.id)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    def has_review(self, item: Union[int, 'util.Item']) -> bool:
        """
        指定されたアイテムのユーザーが作成したレビューが存在するか確認します

        :param item: アイテムIDまたはItem型
        :return: 存在するか
        """

        if isinstance(item, int):
            return util.Review.has_review(self.mc_uuid, item)
        elif isinstance(item, util.Item):
            return util.Review.has_review(self.mc_uuid, item.id)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    def has_rating(self, item: Union[int, 'util.Item']) -> bool:
        """
        指定されたアイテムのユーザーが作成した評価が存在するか確認します

        :param item: アイテムIDまたはItem型
        :return: 存在するか
        """

        if isinstance(item, int):
            return util.Review.has_rating(self.mc_uuid, item)
        elif isinstance(item, util.Item):
            return util.Review.has_rating(self.mc_uuid, item.id)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    def update_browsing_history(self, item: Union[int, 'util.Item'], duration: int) -> bool:
        """
        閲覧履歴を更新します

        :param item: アイテムIDまたはItem型
        :param duration: 閲覧時間
        :return: 成功したか
        """

        if isinstance(item, int):
            return util.DatabaseHelper.update_browsing_history(self.mc_uuid, item, duration)
        elif isinstance(item, util.Item):
            return util.DatabaseHelper.update_browsing_history(self.mc_uuid, item.id, duration)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    def initialize_browsing_history(self, item: Union[int, 'util.Item']) -> bool:
        """
        閲覧履歴を初期化します
        :param item: アイテムIDまたはItem型
        :return: 成功したか
        """

        if isinstance(item, int):
            return util.DatabaseHelper.initialize_browsing_history(self.mc_uuid, item)
        elif isinstance(item, util.Item):
            return util.DatabaseHelper.initialize_browsing_history(self.mc_uuid, item.id)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    def get_browsing_history(self) -> Union[list[int], None]:
        """
        閲覧履歴を取得します

        :return: アイテムIDのリスト
        """
        r = util.DatabaseHelper.get_browsing_history(self.mc_uuid)
        if not r:
            return None

        return [i[0] for i in r]

    def get_browsing_history_recently(self) -> Union[list['util.Item'], None]:
        """
        最新4つの閲覧履歴を取得します

        :return: Item型のリスト
        """

        return [util.Item.by_id(i[0]) for i in util.DatabaseHelper.get_browsing_history(self.mc_uuid)]

    def get_available_items(self) -> Union[list[Union['util.Item', None]], None]:
        """
        販売中のアイテムを取得します

        :return: Item型のリスト
        """

        r = util.DatabaseHelper.get_available_item(self.mc_uuid)
        if not r:
            return None

        return [util.Item.by_db(i) for i in r]

    def get_available_items_length(self) -> int:
        """
        販売中のアイテムの数を取得します

        :return: 販売中の数
        """
        r = util.DatabaseHelper.get_available_item(self.mc_uuid)
        if not r:
            return 0

        return len(r)

    def get_waiting_stock(self) -> list['util.ItemStack']:
        """
        待機ストックを取得します

        :return: ItemStack型
        """

        return util.ItemStack.by_mc_uuid(self.mc_uuid)

    def update_waiting_stock(self, w: list['util.ItemStack']):
        """
        待機ストックを更新します

        :return: 成功したか
        """

        item_list = [None if not i else i.encode() for i in w]
        return util.DatabaseHelper.update_waiting_stock(self.mc_uuid, json.dumps(item_list))

    def get_balance(self) -> float:
        """
        残高を取得します(取得に少し時間がかかります)

        :return: プレイヤーの残高
        """
        if not self.__cached_balance:
            self.__cached_balance = util.SocketHelper.get_balance(self.mc_uuid)
        return self.__cached_balance

    def withdraw(self, amount: Union[float, Decimal], action: str, reason: str) -> bool:
        """
        ユーザーの口座からお金を出金します

        :param amount: 出金する金額
        :param action: 簡単な理由
        :param reason: 出金する理由
        :return: お金が出金されたか(キャンセルされた場合や接続失敗した場合はFalseを返却)
        """

        return util.SocketHelper.withdraw_player(self.mc_uuid, float(amount), action, reason)

    def deposit(self, amount: Union[float, Decimal], action: str, reason: str) -> bool:
        """
        ユーザーの口座にお金を入金します

        :param amount: 出金する金額
        :param action: 簡単な理由
        :param reason: 出金する理由
        :return: お金が出金されたか(キャンセルされた場合や接続失敗した場合はFalseを返却)
        """

        return util.SocketHelper.deposit_player(self.mc_uuid, float(amount), action, reason)

    @staticmethod
    def by_mc_uuid(mc_uuid) -> Union['User', None]:
        """
        UUIDからUser型を取得します(見つからなかった場合はNoneを返却)

        :param mc_uuid: MinecraftのUUID
        :return: User型(見つからなかった場合はNoneを返却)
        """

        return User(mc_uuid)

    @staticmethod
    def by_discord_id(discord_id) -> Union['User', None]:
        """
        UUIDからUser型を取得します(見つからなかった場合はNoneを返却)

        :param discord_id: DiscordのID
        :return: User型(見つからなかった場合はNoneを返却)
        """

        r = util.DatabaseHelper.get_mc_uuid(discord_id)
        if not r:
            return None

        return User(r)
