import datetime
import json
import random
import secrets
from decimal import Decimal
from typing import Union
from uuid import UUID

import utils


class Order:
    order_id: str
    mc_uuid: UUID
    order_item: 'utils.Cart'
    ordered_at: datetime.datetime
    ships_at: datetime.datetime
    delivers_at: datetime.datetime
    amount: float
    used_point: int
    status: bool
    canceled: bool
    error: str

    __cached_progress: float = None

    def __init__(
            self,
            order_id: str,
            mc_uuid: UUID,
            order_item: 'utils.Cart',
            ordered_at: datetime.datetime,
            ships_at: datetime.datetime,
            delivers_at: datetime.datetime,
            amount: float,
            used_point: int,
            status: bool,
            canceled: bool,
            error: str,
            dm_sent: bool
    ):
        self.order_id = order_id
        self.mc_uuid = mc_uuid
        self.order_item = order_item
        self.ordered_at = ordered_at
        self.ships_at = ships_at
        self.delivers_at = delivers_at
        self.amount = amount
        self.used_point = used_point
        self.status = status
        self.canceled = canceled
        self.error = error
        self.dm_sent = dm_sent

    def __dict__(self):
        return {
            "order_id": self.order_id,
            "mc_uuid": self.mc_uuid,
            "order_item": self.order_item,
            "ordered_at": self.ordered_at,
            "ships_at": self.ships_at,
            "delivers_at": self.delivers_at,
            "amount": self.amount,
            "used_point": self.used_point,
            "status": self.status,
            "canceled": self.canceled,
            "error": self.error,
            "dm_sent": self.dm_sent,
        }

    def __str__(self):
        return "Order" + str(self.__dict__())

    def __repr__(self):
        return (f"Order({self.order_id.__repr__()}, {self.mc_uuid.__repr__()}, {self.order_item.__repr__()}, {self.ordered_at.__repr__()}, "
                f"{self.ships_at.__repr__()}, {self.delivers_at.__repr__()}, {self.amount.__repr__()}, {self.used_point.__repr__()}, "
                f"{self.status.__repr__()}, {self.canceled.__repr__()}, {self.error.__repr__()}, {self.dm_sent.__repr__()})")

    @property
    def buyer(self) -> Union['utils.User', None]:
        """
        購入者のUser型を取得します

        :return: User型
        """

        return utils.User.by_mc_uuid(self.mc_uuid)

    @property
    def delivery_progress(self) -> float:
        """
        注文の配達の進捗具合を取得します

        :return: 進捗具合(%)
        """

        if not self.__cached_progress:
            ship = round(utils.calc_time_percentage(self.ordered_at, self.ships_at))
            deliver = round(utils.calc_time_percentage(self.ships_at, self.delivers_at))

            self.__cached_progress = (ship * 3.3 / 10) + (deliver * 6.7 / 10)
        return round(self.__cached_progress)

    def will_arrive_today(self) -> bool:
        """
        注文が今日届くかを確認します

        :return: 今日届くか
        """

        now = datetime.datetime.now()
        return self.delivers_at.date() == now.date()

    def is_shipped(self) -> bool:
        """
        すでに発送されたかを取得します

        :return: 発送されたか
        """

        now = datetime.datetime.now()
        return self.ships_at <= now

    def cancel(self) -> bool:
        """
        注文をキャンセルします

        :return: 成功したか
        """

        return utils.DatabaseHelper.cancel_order(self.order_id)

    def redelivery(self) -> bool:
        """
        再配達をします

        :return:　成功したか
        """
        if self.error:
            now = datetime.datetime.now()
            time = now + datetime.timedelta(hours=random.randint(1, 4),
                                            minutes=random.randint(0, 59),
                                            seconds=0,
                                            microseconds=0)
            return utils.DatabaseHelper.redelivery_order(self.order_id, time)
        return False

    @staticmethod
    def create(mc_uuid: UUID, items: 'utils.Cart', ships_at: datetime.datetime,
               delivers_at: datetime.datetime, order_id: str, total: Union[float, Decimal],
               point: int) -> bool:
        """
        注文を作成します

        :param mc_uuid: MinecraftUUID
        :param items: Cart型
        :param ships_at: 発送時間
        :param delivers_at: 配達時間
        :param order_id: オーダーID
        :param total: トータルの値段(ポイントの使用を含む)
        :param point: 使用したポイント
        :return: 成功したか
        """

        return utils.DatabaseHelper.add_order(str(mc_uuid), json.dumps(items.to_dict()),
                                              order_id, ships_at, delivers_at, float(total), point)

    @staticmethod
    def decode(db_list: str) -> 'utils.Cart':
        """
        注文の商品情報JSONからカート型を取得します

        :param db_list: DBのOrderのアイテムデータ
        :return: カート型
        """

        db_list = json.loads(db_list)
        return utils.Cart({utils.Item.by_id(int(i)): q for i, q in db_list.items()})

    @staticmethod
    def by_mc_uuid(mc_uuid: UUID) -> Union[list['Order'], None]:
        """
        注文を取得します

        :param mc_uuid: MinecraftUUID
        :return: オーダー型のリスト
        """

        r = utils.DatabaseHelper.get_orders(str(mc_uuid))

        if not r:
            return None

        return [
            Order(i["order_id"], UUID(i["mc_uuid"]), Order.decode(i["order_item"]),
                  i["ordered_at"], i["ships_at"], i["delivers_at"], i["amount"],
                  i["used_point"], bool(i["status"]), bool(i["canceled"]), i["error"],
                  bool(i["dm_sent"]))
            for i in r
        ]

    @staticmethod
    def by_id(id: str) -> Union['Order', None]:
        """
        オーダーIDからOrder型を取得します

        :param id: オーダーID
        :return: Order型
        """

        r = utils.DatabaseHelper.get_order(id)

        if not r:
            return None
        return Order(r["order_id"], UUID(r["mc_uuid"]), Order.decode(r["order_item"]),
                     r["ordered_at"], r["ships_at"], r["delivers_at"], r["amount"],
                     r["used_point"], bool(r["status"]), bool(r["canceled"]), r["error"],
                     bool(r["dm_sent"]))

    @staticmethod
    def create_order_id():
        """
        オーダーIDを作成します

        :return: オーダーID
        """
        return (f"U{str(secrets.randbelow(999)).zfill(3)}-" +
                f"{str(secrets.randbelow(999999)).zfill(6)}-" +
                f"{str(secrets.randbelow(999999)).zfill(6)}")

    @staticmethod
    def calc_delivery_time():
        """
        正確なお届け時間を計算します

        :return: お届け時間(datetime型)
        """

        now = datetime.datetime.now().replace(microsecond=0)
        if now.time() > datetime.time(13, 0, 0):
            delivery_time = (now.replace(hour=random.randint(8, 18), minute=random.randint(0, 59),
                                         second=0, microsecond=0)
                             + datetime.timedelta(days=2))
        else:
            delivery_time = (now.replace(hour=random.randint(8, 18), minute=random.randint(0, 59),
                                         second=0, microsecond=0)
                             + datetime.timedelta(days=1))

        return delivery_time

    @staticmethod
    def calc_fastest_delivery_time():
        """
        正確な最も早いお届け時間を計算します

        :return: お届け時間(datetime型)
        """

        now = datetime.datetime.now().replace(microsecond=0)
        if now.time() > datetime.time(15, 0, 0):
            delivery_time = (now.replace(hour=random.randint(7, 10),
                                         minute=random.randint(0, 59),
                                         second=0, microsecond=0)
                             + datetime.timedelta(days=1))
        else:
            delivery_time = (now.replace(hour=random.randint(now.hour+3, 20),
                                         minute=random.randint(0, 59),
                                         second=0, microsecond=0))

        return delivery_time

    @staticmethod
    def calc_ship_time(delivery_time: datetime.datetime):
        """
        お届け時間から発送時間を計算します

        :return: 発送時間(datetime型)
        """

        rand_hour = random.randint(1, 3)
        rand_minute = random.randint(0, 59)

        ship_time = delivery_time - datetime.timedelta(hours=rand_hour, minutes=rand_minute,
                                                       seconds=0, microseconds=0)

        return ship_time

    @staticmethod
    def calc_expected_delivery_time():
        """
        おおよそのお届け時間を計算します

        :return: お届け時間(datetime型)
        """

        now = datetime.datetime.now()
        if now.time() > datetime.time(13, 0, 0):
            rand_time = now + datetime.timedelta(days=2)
        else:
            rand_time = now + datetime.timedelta(days=1)

        return rand_time

    @staticmethod
    def calc_expected_fastest_delivery_time():
        """
        おおよその最も早いお届け時間を計算します

        :return: お届け時間(datetime型)
        """
        now = datetime.datetime.now()
        if now.time() > datetime.time(15, 0, 0):
            rand_time = now + datetime.timedelta(hours=random.randint(1, 4))
        else:
            rand_time = now + datetime.timedelta(days=1)

        return rand_time

    @staticmethod
    def get_active() -> Union[list['Order'], None]:
        """
        有効な注文を取得します

        :return: Order型のリスト
        """

        r = utils.DatabaseHelper.get_all_orders()

        if not r:
            return None

        return [
            Order(i["order_id"], UUID(i["mc_uuid"]), Order.decode(i["order_item"]),
                  i["ordered_at"], i["ships_at"], i["delivers_at"], i["amount"],
                  i["used_point"], bool(i["status"]), bool(i["canceled"]), i["error"],
                  bool(i["dm_sent"]))
            for i in r
        ]
