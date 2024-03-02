import json
import urllib.parse
from collections import UserDict
from decimal import Decimal
from typing import Union
from uuid import UUID

import utils
from config import settings

per_point = Decimal(settings.POINT_PER)


class Cart(UserDict):
    __cached_total: Union[float, None] = None
    __cached_amount: Union[int, None] = None
    __cached_point: Union[int, None] = None

    def __init__(self, cart: dict['utils.Item', int] = None):
        super().__init__(cart)

    def __str__(self):
        return "Cart" + super().__str__()

    def __repr__(self):
        return f"Cart({self.data.__repr__()})"

    @property
    def total(self) -> float:
        """
        合計金額を取得します

        :return: 合計金額
        """

        if not self.__cached_total:
            if not self.data:
                self.__cached_total = 0.0
            else:
                self.__cached_total = float(sum(
                    Decimal(str(item.discount_price)) * Decimal(str(quantity))
                    for item, quantity in self.data.items()))
        return self.__cached_total

    @property
    def quantity(self) -> int:
        """
        合計の商品数を計算します

        :return: 合計商品数
        """

        if not self.__cached_amount:
            if not self.data:
                self.__cached_amount = 0
            else:
                self.__cached_amount = sum([i for i in self.data.values()])
        return self.__cached_amount

    @property
    def points(self) -> int:
        """
        割引した値段のポイントを取得します

        :return: 割引した値段のポイント
        """

        if not self.__cached_point:
            if not self.data:
                self.__cached_point = 0
            else:
                self.__cached_point = sum(
                    Decimal(str(item.get_discounted_point())) * Decimal(str(quantity))
                    for item, quantity in self.data.items())
        return self.__cached_point

    def is_in_stock(self) -> bool:
        """
        在庫を確認し、購入できるかを返します

        :return: 購入可か(在庫0があったらFalse, それ以外はTrueを返却)
        """

        return all(i.stock >= q for i, q in self.data.items())

    def are_valid_items(self) -> bool:
        """
        すべて有効なアイテムか確認します

        :return: すべて有効か
        """

        if False in [i.status for i in self.data]:
            return False
        else:
            return True

    def get_quantity(self, item: Union[int, 'utils.Item']) -> Union[int, None]:
        """
        アイテムIDからその数量を取得します

        :param item: アイテムIDまたはItem型
        :return: 数量(見つからなかった場合はNoneを返却)
        """

        if isinstance(item, int):
            for i in self.data:
                if i.id == item:
                    return self.data[i]
        elif isinstance(item, utils.Item):
            for i in self.data:
                if i.id == item.id:
                    return self.data[i]
        else:
            TypeError(f"'{type(item)}'は使用できません")

    def to_dict(self) -> dict[int, int]:
        """
        辞書にエンコードします

        :return: JSON
        """

        return {str(i.id): q for i, q in self.data.items()}

    def to_percent_encoding(self) -> str:
        """
        URLに使用するカート情報をエンコードします

        :return: URLエンコード
        """

        return urllib.parse.quote(json.dumps(self.to_dict()))

    def create_reason(self, order_id, used_point=None):
        """
        出金する際の理由を作成します

        :param order_id: オーダーID
        :param used_point: 使用したポイント
        :return: 理由
        """

        reason = ", ".join([f"{i.id}({i.price}×{q}個)" for i, q in self.data.items()])
        if used_point:
            reason += f"(ポイント使用 {used_point}pt: {Decimal(str(used_point)) * per_point}分)"
        reason += f"(注文番号: {order_id})"
        return reason

    def delete_invalid_items(self):
        """
        無効な商品(削除されたまたは在庫不足)のものを削除します
        """

        if self.data:
            for i in list(self.data.keys()):
                if not i.status or i.stock < self.data[i]:
                    del self.data[i]

    @staticmethod
    def delete(mc_uuid: UUID, item: Union[int, 'utils.Item']) -> bool:
        """
        カートからアイテムを削除します

        :param mc_uuid: MinecraftUUID
        :param item: アイテムIDまたはItem型
        :return: 成功したか
        """

        if isinstance(item, int):
            return utils.DatabaseHelper.delete_cart(str(mc_uuid), item)
        elif isinstance(item, utils.Item):
            return utils.DatabaseHelper.delete_cart(str(mc_uuid), item.id)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @staticmethod
    def add(mc_uuid: UUID, item: Union[int, 'utils.Item'], qty: int) -> bool:
        """
        カートにアイテムを追加します

        :param mc_uuid: MinecraftUUID
        :param item: アイテムIDまたはItem型
        :param qty: 数量
        :return: 成功したか
        """

        if isinstance(item, int):
            return utils.DatabaseHelper.add_cart(str(mc_uuid), item, qty)
        elif isinstance(item, utils.Item):
            return utils.DatabaseHelper.add_cart(str(mc_uuid), item.id, qty)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @staticmethod
    def update_quantity(mc_uuid: UUID, item: Union[int, 'utils.Item'], qty: int) -> bool:
        """
        カート内のアイテムの数量を指定された数量に更新します

        :param mc_uuid: MinecraftUUID
        :param item: アイテムIDまたはItem型
        :param qty: 数量
        :return: 成功したか
        """

        if isinstance(item, int):
            return utils.DatabaseHelper.update_cart(str(mc_uuid), item, qty)
        elif isinstance(item, utils.Item):
            return utils.DatabaseHelper.update_cart(str(mc_uuid), item.id, qty)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @staticmethod
    def by_mc_uuid(mc_uuid: UUID) -> 'Cart':
        """
        UUIDからCart型を取得します

        :param mc_uuid: MinecraftUUID
        :return: Cart型(アイテムが見つからなかった場合はNoneを挿入)
        """

        r = utils.DatabaseHelper.get_cart(str(mc_uuid))

        if not r:
            return Cart()

        return Cart({utils.Item.by_id(i["item_id"]): i["quantity"] for i in r})

    @staticmethod
    def by_id_dict(id_dict: dict[Union[int, str], int]):
        """
        {<アイテムID>: <数量>, ...}形式のアイテム辞書をCart型に変換します

        :param id_dict: アイテム辞書
        :return: Cart型
        """

        return Cart({utils.Item.by_id(int(i)): j for i, j in id_dict.items()})
