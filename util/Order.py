import datetime
import json
import random
import secrets
from decimal import Decimal
from typing import Union

import util


class Order:
    order_id: str
    mc_uuid: str
    order_item: 'util.Cart'
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
            mc_uuid: str,
            order_item: 'util.Cart',
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

    def get_purchaser(self) -> Union['util.User', None]:
        """
        購入者のUser型を取得します

        :return: User型
        """

        return util.User.by_mc_uuid(self.mc_uuid)

    def get_delivery_progress(self) -> float:
        """
        注文の配達の進捗具合を取得します

        :return: 進捗具合(%)
        """

        if not self.__cached_progress:
            ship = round(util.calc_time_percentage(self.ordered_at, self.ships_at))
            deliver = round(util.calc_time_percentage(self.ships_at, self.delivers_at))

            self.__cached_progress = (ship * 3.3 / 10) + (deliver * 6.7 / 10)
        return round(self.__cached_progress)

    def will_arrive_today(self) -> bool:
        """
        注文が今日届くかを確認します

        :return: 今日届くか
        """

        now = datetime.datetime.now()
        return self.delivers_at.year == now.year and self.delivers_at.month == now.month and self.delivers_at.day == now.day

    def cancel(self) -> bool:
        """
        注文をキャンセルします

        :return: 成功したか
        """

        return util.DatabaseHelper.cancel_order(self.order_id)

    def redelivery(self):
        if self.error:
            now = datetime.datetime.now()
            return now + datetime.timedelta(hours=random.randint(1, 4),
                                            minutes=random.randint(0, 59),
                                            seconds=0,
                                            microseconds=0)

    @staticmethod
    def create(mc_uuid: str, items: 'util.Cart', ships_at: datetime.datetime,
               delivers_at: datetime.datetime, order_id: str, total: Union[float, Decimal],
               point: int) -> bool:
        """
        注文を作成します

        :param mc_uuid: MinecraftのUUID
        :param items: Cart型
        :param ships_at: 発送時間
        :param delivers_at: 配達時間
        :param order_id: オーダーID
        :param total: トータルの値段(ポイントの使用を含む)
        :param point: 使用したポイント
        :return: 成功したか
        """

        return util.DatabaseHelper.add_order(mc_uuid, json.dumps(items.encode_to_dict()),
                                             order_id, ships_at, delivers_at, float(total), point)

    @staticmethod
    def decode(db_list: str) -> 'util.Cart':
        """
        注文の商品情報JSONからカート型を取得します

        :param db_list: DBのOrderのアイテムデータ
        :return: カート型
        """

        db_list = json.loads(db_list)
        return util.Cart({util.Item.by_id(int(i)): q for i, q in db_list.items()})

    @staticmethod
    def by_mc_uuid(mc_uuid: str) -> Union[list['Order'], None]:
        """
        注文を取得します

        :param mc_uuid: MinecraftのUUID
        :return: オーダー型のリスト
        """

        r = util.DatabaseHelper.get_orders(mc_uuid)

        if not r:
            return None

        return [
            Order(i["order_id"], i["mc_uuid"], Order.decode(i["order_item"]),
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

        r = util.DatabaseHelper.get_order(id)

        if not r:
            return None
        return Order(r["order_id"], r["mc_uuid"], Order.decode(r["order_item"]),
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
        if now > datetime.datetime.strptime("13:00:00", "%H:%M:%S"):
            delivery_time = (now.replace(hour=random.randint(8, 18), minute=random.randint(0, 59),
                                         second=0, microsecond=0)
                             + datetime.timedelta(days=2))
        else:
            delivery_time = (now.replace(hour=random.randint(8, 18), minute=random.randint(0, 59),
                                         second=0, microsecond=0)
                             + datetime.timedelta(days=1))

        return delivery_time

    @staticmethod
    def calc_ship_time(delivery_time: datetime.datetime):
        """
        お届け時間から発送時間を計算します

        :return: 発送時間(datetime型)
        """

        rand_hour = random.randint(1, 4)
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
        if now > datetime.datetime.strptime("13:00:00", "%H:%M:%S"):
            rand_time = now + datetime.timedelta(days=2)
        else:
            rand_time = now + datetime.timedelta(days=1)

        return rand_time
