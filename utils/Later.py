from collections import UserDict
from decimal import Decimal
from typing import Union
from uuid import UUID

import utils


class Later(UserDict):

    __cached_total: Union[float, None] = None
    __cached_amount: Union[int, None] = None

    def __init__(self, later: dict['utils.Item', int] = None):
        super().__init__(later)

    def __str__(self):
        return "Cart" + super().__str__()

    def __repr__(self):
        return f"Later({self.data})"

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
                self.__cached_total = sum(
                    Decimal(str(item.discount_price)) * Decimal(str(quantity))
                    for item, quantity in self.data.items())
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

    def is_in_stock(self) -> bool:
        """
        在庫を確認し、購入できるかを返します

        :return: 購入可か(在庫0があったらFalse, それ以外はTrueを返却)
        """

        if 0 in [i.stock for i in self.data]:
            return False
        else:
            return True

    def are_valid_items(self) -> bool:
        """
        すべて有効なアイテムか確認します

        :return: すべて有効か
        """

        if False in [i.status for i in self.data]:
            return False
        else:
            return True

    def get_quantity(self, item_id: int) -> Union[int, None]:
        """
        アイテムIDからその数量を取得します

        :param item_id: アイテムID
        :return: 数量(見つからなかった場合はNoneを返却)
        """

        for i in self.data:
            if i.id == item_id:
                return self.data[i]
        return None

    @staticmethod
    def delete(mc_uuid: UUID, item: Union[int, 'utils.Item']) -> bool:
        """
        あとで買うからアイテムを削除します

        :param mc_uuid: MinecraftUUID
        :param item: アイテムIDまたはItem型
        :return: 成功したか
        """

        if isinstance(item, int):
            return utils.DatabaseHelper.delete_later(str(mc_uuid), item)
        elif isinstance(item, utils.Item):
            return utils.DatabaseHelper.delete_later(str(mc_uuid), item.id)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @staticmethod
    def add(mc_uuid: UUID, item: Union[int, 'utils.Item'], qty: int) -> bool:
        """
        あとで買うにアイテムを追加します

        :param mc_uuid: MinecraftUUID
        :param item: アイテムIDまたはItem型
        :param qty: 数量
        :return: 成功したか
        """

        if isinstance(item, int):
            return utils.DatabaseHelper.add_later(str(mc_uuid), item, qty)
        elif isinstance(item, utils.Item):
            return utils.DatabaseHelper.add_later(str(mc_uuid), item.id, qty)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @staticmethod
    def update_quantity(mc_uuid: UUID, item: Union[int, 'utils.Item'], qty: int) -> bool:
        """
        あとで買う内のアイテムの数量を指定された数量に更新します

        :param mc_uuid: MinecraftUUID
        :param item: アイテムIDまたはItem型
        :param qty: 数量
        :return: 成功したか
        """

        if isinstance(item, int):
            return utils.DatabaseHelper.update_later(str(mc_uuid), item, qty)
        elif isinstance(item, utils.Item):
            return utils.DatabaseHelper.update_later(str(mc_uuid), item.id, qty)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @staticmethod
    def by_mc_uuid(mc_uuid: UUID) -> 'Later':
        """
        UUIDからLater型を取得します

        :param mc_uuid: MinecraftUUID
        :return: Later型(アイテムが見つからなかった場合はNoneを挿入)
        """

        r = utils.DatabaseHelper.get_later(str(mc_uuid))

        if not r:
            return Later()

        later = {utils.Item.by_id(i["item_id"]): i["quantity"] for i in r}
        return Later(later)
