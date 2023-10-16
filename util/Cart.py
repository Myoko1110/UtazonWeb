import json
import urllib.parse
from decimal import Decimal
from typing import Union

import util
from config import settings

per_point = Decimal(settings.POINT_PER)


class Cart:
    cart: Union[dict['util.Item', int], None]

    __cached_total: Union[float, None] = None
    __cached_amount: Union[int, None] = None
    __cached_point: Union[int, None] = None
    __index: int = 0
    __keys: list = None

    def __init__(self, cart: dict['util.Item', int] = None):
        self.cart = cart

        if self.cart is not None:
            self.__keys = list(self.cart.keys())

    def __getitem__(self, item: 'util.Item'):
        return self.cart[item]

    def __iter__(self):
        return self

    def __next__(self):
        if self.__index < len(self.__keys):
            key = self.__keys[self.__index]
            value = self.cart[key]
            self.__index += 1
            return key, value
        else:
            raise StopIteration

    def __len__(self):
        return len(self.cart)

    def __bool__(self):
        return bool(self.cart)

    def __str__(self):
        return "Cart" + str(self.cart)

    def items(self):
        if not self.cart:
            return None
        return self.cart.items()

    def keys(self):
        if not self.cart:
            return None
        return self.cart.keys()

    def values(self):
        if not self.cart:
            return None
        return self.cart.values()

    def get_total(self) -> float:
        """
        合計金額を取得します

        :return: 合計金額
        """

        if not self.__cached_total:
            if not self.cart:
                self.__cached_total = 0.0
            else:
                self.__cached_total = float(sum(
                    Decimal(str(item.get_discounted_price())) * Decimal(str(quantity))
                    for item, quantity in self.cart.items()))
        return self.__cached_total

    def get_amount(self) -> int:
        """
        合計の商品数を計算します

        :return: 合計商品数
        """

        if not self.__cached_amount:
            if not self.cart:
                self.__cached_amount = 0
            else:
                self.__cached_amount = sum([i for i in self.cart.values()])
        return self.__cached_amount

    def get_point(self) -> int:
        """
        割引した値段のポイントを取得します

        :return: 割引した値段のポイント
        """

        if not self.__cached_point:
            if not self.cart:
                self.__cached_point = 0
            else:
                self.__cached_point = sum(
                    Decimal(str(item.get_discounted_point())) * Decimal(str(quantity))
                    for item, quantity in self.cart.items())
        return self.__cached_point

    def is_in_stock(self) -> bool:
        """
        在庫を確認し、購入できるかを返します

        :return: 購入可か(在庫0があったらFalse, それ以外はTrueを返却)
        """

        return all(i.get_stock() >= q for i, q in self.cart.items())

    def is_valid_items(self) -> bool:
        """
        すべて有効なアイテムか確認します

        :return: すべて有効か
        """

        if False in [i.status for i in self.cart]:
            return False
        else:
            return True

    def get_qty(self, item: Union[int, 'util.Item']) -> Union[int, None]:
        """
        アイテムIDからその数量を取得します

        :param item: アイテムIDまたはItem型
        :return: 数量(見つからなかった場合はNoneを返却)
        """

        if isinstance(item, int):
            for i in self.cart:
                if i.id == item:
                    return self.cart[i]
        elif isinstance(item, util.Item):
            for i in self.cart:
                if i.id == item.id:
                    return self.cart[i]
        else:
            TypeError(f"'{type(item)}'は使用できません")

    def encode_to_dict(self) -> dict[int, int]:
        """
        辞書にエンコードします

        :return: JSON
        """

        return {str(i.id): q for i, q in self.cart.items()}

    def encode_to_percent_encoding(self) -> str:
        """
        URLに使用するカート情報をエンコードします

        :return: URLエンコード
        """

        return urllib.parse.quote(json.dumps(self.encode_to_dict()))

    def create_reason(self, order_id, used_point=None):
        """
        出勤する際の理由を作成します

        :param order_id: オーダーID
        :param used_point: 使用したポイント
        :return: 理由
        """

        reason = ", ".join([f"{i.id}({i.price}×{q}個)" for i, q in self.cart.items()])
        if used_point:
            reason += f"(ポイント使用 {used_point}pt: {Decimal(str(used_point)) * per_point}分)"
        reason += f"(注文番号: {order_id})"
        return reason

    def delete_invalid_items(self):
        """
        無効な商品(削除されたまたは在庫不足)のものを削除します
        """

        if self.cart:
            for i in list(self.cart.keys()):
                if not i.status or i.get_stock() < self.cart[i]:
                    del self.cart[i]

    @staticmethod
    def delete(mc_uuid: str, item: Union[int, 'util.Item']) -> bool:
        """
        カートからアイテムを削除します

        :param mc_uuid: MinecraftのUUID
        :param item: アイテムIDまたはItem型
        :return: 成功したか
        """

        if isinstance(item, int):
            return util.DatabaseHelper.delete_cart(mc_uuid, item)
        elif isinstance(item, util.Item):
            return util.DatabaseHelper.delete_cart(mc_uuid, item.id)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @staticmethod
    def add(mc_uuid: str, item: Union[int, 'util.Item'], qty: int) -> bool:
        """
        カートにアイテムを追加します

        :param mc_uuid: MinecraftのUUID
        :param item: アイテムIDまたはItem型
        :param qty: 数量
        :return: 成功したか
        """

        if isinstance(item, int):
            return util.DatabaseHelper.add_cart(mc_uuid, item, qty)
        elif isinstance(item, util.Item):
            return util.DatabaseHelper.add_cart(mc_uuid, item.id, qty)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @staticmethod
    def update_qty(mc_uuid: str, item: Union[int, 'util.Item'], qty: int) -> bool:
        """
        カート内のアイテムの数量を指定された数量に更新します

        :param mc_uuid: MinecraftのUUId
        :param item: アイテムIDまたはItem型
        :param qty: 数量
        :return: 成功したか
        """

        if isinstance(item, int):
            return util.DatabaseHelper.update_cart(mc_uuid, item, qty)
        elif isinstance(item, util.Item):
            return util.DatabaseHelper.update_cart(mc_uuid, item.id, qty)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @staticmethod
    def by_mc_uuid(mc_uuid: str) -> 'Cart':
        """
        UUIDからCart型を取得します

        :param mc_uuid: MinecraftのUUID
        :return: Cart型(アイテムが見つからなかった場合はNoneを挿入)
        """

        r = util.DatabaseHelper.get_cart(mc_uuid)

        if not r:
            return Cart()

        return Cart({util.Item.by_id(i["item_id"]): i["quantity"] for i in r})

    @staticmethod
    def by_id_dict(id_dict: dict[Union[int, str], int]):
        """
        {<アイテムID>: <数量>, ...}形式のアイテム辞書をCart型に変換します

        :param id_dict: アイテム辞書
        :return: Cart型
        """

        return Cart({util.Item.by_id(int(i)): j for i, j in id_dict.items()})
