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
    delivers_at: datetime.datetime
    ordered_at: datetime.datetime
    amount: float
    used_point: int
    status: bool
    canceled: bool
    error: str

    __cached_progress: int = None

    def __init__(self, order_id: str, mc_uuid: str, order_item: 'util.Cart',
                 delivers_at: datetime, ordered_at: datetime, amount: float,
                 used_point: int, status: bool, canceled: bool, error: str):
        self.order_id = order_id
        self.mc_uuid = mc_uuid
        self.order_item = order_item
        self.delivers_at = delivers_at
        self.ordered_at = ordered_at
        self.amount = amount
        self.used_point = used_point
        self.status = status
        self.canceled = canceled
        self.error = error

    def get_purchaser(self) -> Union['util.User', None]:
        """
        購入者のUser型を取得します

        :return: User型
        """

        return util.User.by_mc_uuid(self.mc_uuid)

    def get_delivery_progress(self) -> int:
        """
        注文の配達の進捗具合を取得します

        :return: 進捗具合(%)
        """

        if not self.__cached_progress:
            self.__cached_progress = round(
                util.calc_time_percentage(self.ordered_at, self.delivers_at))
        return self.__cached_progress

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
    def create(mc_uuid: str, items: 'util.Cart', delivers_at: datetime.datetime, order_id: str,
               total: Union[float, Decimal], point: int) -> bool:
        """
        注文を作成します

        :param mc_uuid: MinecraftのUUID
        :param items: Cart型
        :param delivers_at: 配達時間
        :param order_id: オーダーID
        :param total: トータルの値段(ポイントの使用を含む)
        :param point: 使用したポイント
        :return: 成功したか
        """

        return util.DatabaseHelper.add_order(mc_uuid, json.dumps(items.encode_to_dict()),
                                             delivers_at, order_id, float(total), point)

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
                  i["delivers_at"], i["ordered_at"],
                  i["amount"], i["used_point"], i["status"], i["canceled"], i["error"])
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
                     r["delivers_at"], r["ordered_at"],
                     r["amount"], r["used_point"], r["status"], r["canceled"], r["error"])

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
