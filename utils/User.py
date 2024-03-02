import datetime
import json
from decimal import Decimal
from typing import Union
from uuid import UUID

import discord
import requests

import bot
import utils


class User:
    mc_uuid: UUID

    __cached_mc_id: Union[str, bool, None] = None
    __cached_discord_id: Union[int, None] = None
    __cached_balance: float = 0
    __cached_discord_user: discord.User = None
    __cached_point: int = 0

    def __init__(self, mc_uuid: UUID):
        self.mc_uuid = mc_uuid

    def __dict__(self):
        return {"mc_uuid": self.mc_uuid}

    def __str__(self):
        return "User" + str(self.__dict__())

    def __repr__(self):
        return f"User({self.mc_uuid})"

    @property
    def mc_id(self) -> Union[str, None]:
        """
        MinecraftIDを取得します

        :return: MinecraftID
        """

        if self.__cached_mc_id is False:
            return None
        if self.__cached_mc_id:
            return self.__cached_mc_id

        try:
            profile = requests.get(
                f"https://sessionserver.mojang.com/session/minecraft/profile/{self.mc_uuid}",
                timeout=0.5)
            if profile.status_code != 200:
                self.__cached_mc_id = False
                return None

        except requests.Timeout:
            self.__cached_mc_id = False
            return None
        except requests.ConnectionError:
            self.__cached_mc_id = False
            return None

        profile = profile.json()
        if "name" in profile:

            self.__cached_mc_id = profile["name"]
            return self.__cached_mc_id

        else:
            self.__cached_mc_id = False
            return None

    @property
    def discord(self) -> Union['discord.User', None]:
        """
        DiscordのUser型を取得します

        :return: DiscordのUser型
        """

        if not self.discord_id:
            return None

        if not self.__cached_discord_user:
            self.__cached_discord_user = bot.client.get_user(self.__cached_discord_id)
        return self.__cached_discord_user

    @property
    def discord_id(self) -> Union[int, None]:
        """
        DiscordIDを取得します

        :return: DiscordID
        """

        if not self.__cached_discord_id:
            r = utils.DatabaseHelper.get_discord_id(str(self.mc_uuid))
            if r:
                self.__cached_discord_id = r[0]
            else:
                self.__cached_discord_id = None

        return self.__cached_discord_id

    @property
    def point(self) -> float:
        """
        Utazonポイントを取得します

        :return: ポイント
        """
        if not self.__cached_point:
            rs = utils.DatabaseHelper.get_point(str(self.mc_uuid))

            if rs:
                self.__cached_point = rs[0]
            else:
                self.__cached_point = 0

        return self.__cached_point

    def deduct_points(self, amount: int) -> bool:
        """
        ポイントを減らします

        :return: 成功したか
        """

        return utils.DatabaseHelper.deduct_points(str(self.mc_uuid), amount)

    def add_points(self, amount: int) -> bool:
        """
        ポイントを増やします

        :return: 成功したか
        """

        return utils.DatabaseHelper.add_points(str(self.mc_uuid), amount)

    @property
    def cart(self) -> 'utils.Cart':
        """
        Cart型を取得します

        :return: Cart型(アイテムが見つからなかった場合はNoneを挿入)
        """

        return utils.Cart.by_mc_uuid(self.mc_uuid)

    def reset_cart(self) -> bool:
        """
        カートをリセットします

        :return: 成功したか
        """

        return utils.DatabaseHelper.reset_cart(str(self.mc_uuid))

    @property
    def later(self) -> 'utils.Later':
        """
        Later型を取得します

        :return: Later型(アイテムが見つからなければNoneを挿入)
        """

        return utils.Later.by_mc_uuid(self.mc_uuid)

    @property
    def order(self) -> Union['utils.Cart', None]:
        """
        Order型を取得します

        :return: Order型
        """

        return utils.Order.by_mc_uuid(self.mc_uuid)

    @property
    def pride(self) -> 'utils.Pride':
        """
        Prime型を取得します

        :return: Prime型
        """

        return utils.Pride.by_mc_uuid(self.mc_uuid)

    def get_review(self, item: Union[int, 'utils.Item']) -> Union['utils.Review', None]:
        """
        ユーザーの指定されたアイテムのレビューを取得します

        :param item: アイテムID
        :return: Review型
        """

        if isinstance(item, int):
            return utils.Review.by_mc_uuid(self.mc_uuid, item)
        elif isinstance(item, utils.Item):
            return utils.Review.by_mc_uuid(self.mc_uuid, item.id)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    def has_review(self, item: Union[int, 'utils.Item']) -> bool:
        """
        指定されたアイテムのユーザーが作成したレビューが存在するか確認します

        :param item: アイテムIDまたはItem型
        :return: 存在するか
        """

        if isinstance(item, int):
            return utils.Review.has_review(self.mc_uuid, item)
        elif isinstance(item, utils.Item):
            return utils.Review.has_review(self.mc_uuid, item.id)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    def has_rating(self, item: Union[int, 'utils.Item']) -> bool:
        """
        指定されたアイテムのユーザーが作成した評価が存在するか確認します

        :param item: アイテムIDまたはItem型
        :return: 存在するか
        """

        if isinstance(item, int):
            return utils.Review.has_rating(self.mc_uuid, item)
        elif isinstance(item, utils.Item):
            return utils.Review.has_rating(self.mc_uuid, item.id)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    def update_browsing_history(self, item: Union[int, 'utils.Item'], duration: int) -> bool:
        """
        閲覧履歴を更新します

        :param item: アイテムIDまたはItem型
        :param duration: 閲覧時間
        :return: 成功したか
        """

        if isinstance(item, int):
            return utils.DatabaseHelper.update_browsing_history(str(self.mc_uuid), item, duration)
        elif isinstance(item, utils.Item):
            return utils.DatabaseHelper.update_browsing_history(str(self.mc_uuid), item.id, duration)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    def initialize_browsing_history(self, item: Union[int, 'utils.Item']) -> bool:
        """
        閲覧履歴を初期化します
        :param item: アイテムIDまたはItem型
        :return: 成功したか
        """

        if isinstance(item, int):
            return utils.DatabaseHelper.initialize_browsing_history(str(self.mc_uuid), item)
        elif isinstance(item, utils.Item):
            return utils.DatabaseHelper.initialize_browsing_history(str(self.mc_uuid), item.id)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @property
    def browsing_history(self) -> Union[list[int], None]:
        """
        閲覧履歴を取得します

        :return: アイテムIDのリスト
        """
        r = utils.DatabaseHelper.get_browsing_history(str(self.mc_uuid))
        if not r:
            return None

        return [i[0] for i in r]

    @property
    def browsing_history_recently(self) -> Union[list['utils.Item'], None]:
        """
        最新4つの閲覧履歴を取得します

        :return: Item型のリスト
        """

        return [utils.Item.by_id(i[0]) for i in
                utils.DatabaseHelper.get_browsing_history(str(self.mc_uuid))]

    @property
    def available_items(self) -> Union[list[Union['utils.Item', None]], None]:
        """
        販売中のアイテムを取得します

        :return: Item型のリスト
        """

        r = utils.DatabaseHelper.get_available_item(str(self.mc_uuid))
        if not r:
            return None

        return [utils.Item.by_db(i) for i in r]

    @property
    def unavailable_items(self) -> Union[list[Union['utils.Item', None]], None]:
        """
        販売中のアイテムを取得します

        :return: Item型のリスト
        """

        r = utils.DatabaseHelper.get_unavailable_item(str(self.mc_uuid))
        if not r:
            return None

        return [utils.Item.by_db(i) for i in r]

    @property
    def waiting_stock(self) -> list['utils.ItemStack']:
        """
        待機ストックを取得します

        :return: ItemStack型
        """

        return utils.ItemStack.by_mc_uuid(self.mc_uuid)

    def update_waiting_stock(self, w: list['utils.ItemStack']):
        """
        待機ストックを更新します

        :return: 成功したか
        """

        item_list = [None if not i else i.encode() for i in w]
        return utils.DatabaseHelper.update_waiting_stock(str(self.mc_uuid), json.dumps(item_list))

    @property
    def balance(self) -> float:
        """
        残高を取得します(取得に少し時間がかかります)

        :return: プレイヤーの残高
        """
        if not self.__cached_balance:
            self.__cached_balance = utils.SocketHelper.get_balance(str(self.mc_uuid))
        return self.__cached_balance

    def withdraw(self, amount: Union[float, Decimal], action: str, reason: str) -> bool:
        """
        ユーザーの口座からお金を出金します

        :param amount: 出金する金額
        :param action: 簡単な理由
        :param reason: 出金する理由
        :return: お金が出金されたか(キャンセルされた場合や接続失敗した場合はFalseを返却)
        :raises ConnectionRefusedError: 接続に失敗したときに返します
        """

        return utils.SocketHelper.withdraw_player(str(self.mc_uuid), float(amount), action, reason)

    def deposit(self, amount: Union[float, Decimal], action: str, reason: str) -> bool:
        """
        ユーザーの口座にお金を入金します

        :param amount: 出金する金額
        :param action: 簡単な理由
        :param reason: 出金する理由
        :return: お金が出金されたか(キャンセルされた場合や接続失敗した場合はFalseを返却)
        :raises ConnectionRefusedError: 接続に失敗したときに返します
        """

        return utils.SocketHelper.deposit_player(str(self.mc_uuid), float(amount), action, reason)

    def register_pride(self, plan: 'utils.PridePlan', auto_update: bool) -> bool:
        """
        Prideに登録します

        :param plan: プラン
        :param auto_update: 自動更新
        :return: 成功したか
        """

        now = datetime.datetime.now()

        if plan == utils.PridePlan.MONTHLY:
            now += datetime.timedelta(days=30)
        else:
            now += datetime.timedelta(days=365)

        expires = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return utils.DatabaseHelper.register_pride(self.mc_uuid, plan.name, auto_update, expires)

    @staticmethod
    def by_mc_uuid(mc_uuid: UUID) -> Union['User', None]:
        """
        MinecraftUUIDからUser型を取得します(見つからなかった場合はNoneを返却)

        :param mc_uuid: MinecraftのUUID
        :return: User型(見つからなかった場合はNoneを返却)
        """

        return User(mc_uuid)

    @staticmethod
    def by_discord_id(discord_id) -> Union['User', None]:
        """
        DiscordIDからUser型を取得します(見つからなかった場合はNoneを返却)

        :param discord_id: DiscordID
        :return: User型(見つからなかった場合はNoneを返却)
        """

        r = utils.DatabaseHelper.get_mc_uuid(discord_id)[0]
        if not r:
            return None

        return User(UUID(r))
