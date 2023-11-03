from decimal import Decimal
from typing import Union

import util


class Later:
    later: Union[dict['util.Item', int], None]

    __cached_total: Union[float, None] = None
    __cached_amount: Union[int, None] = None
    __index: int = 0
    __keys: list = None

    def __init__(
            self,
            later: dict['util.Item', int] = None
    ):
        self.later = later

        if self.later is not None:
            self.__keys = list(self.later.keys())

    def __getitem__(self, item: 'util.Item'):
        return self.later[item]

    def __iter__(self):
        return self

    def __next__(self):
        if self.__index < len(self.__keys):
            key = self.__keys[self.__index]
            value = self.later[key]
            self.__index += 1
            return key, value
        else:
            raise StopIteration

    def __len__(self):
        return len(self.later)

    def __bool__(self):
        return bool(self.later)

    def __str__(self):
        return "Later" + str(self.later)

    def items(self):
        if not self.later:
            return None

        return self.later.items()

    def keys(self):
        if not self.later:
            return None

        return self.later.keys()

    def values(self):
        if not self.later:
            return None

        return self.later.values()
    
    def get_total(self) -> float:
        """
        合計金額を取得します

        :return: 合計金額
        """

        if not self.__cached_total:
            if not self.later:
                self.__cached_total = 0.0
            else:
                self.__cached_total = sum(
                    Decimal(str(item.get_discounted_price())) * Decimal(str(quantity))
                    for item, quantity in self.later.items())
        return self.__cached_total

    def get_amount(self) -> int:
        """
        合計の商品数を計算します

        :return: 合計商品数
        """

        if not self.__cached_amount:
            if not self.later:
                self.__cached_amount = 0
            else:
                self.__cached_amount = sum([i for i in self.later.values()])
        return self.__cached_amount

    def is_in_stock(self) -> bool:
        """
        在庫を確認し、購入できるかを返します

        :return: 購入可か(在庫0があったらFalse, それ以外はTrueを返却)
        """

        if 0 in [i.get_stock() for i in self.later]:
            return False
        else:
            return True

    def is_valid_items(self) -> bool:
        """
        すべて有効なアイテムか確認します

        :return: すべて有効か
        """

        if False in [i.status for i in self.later]:
            return False
        else:
            return True

    def get_qty(self, item_id: int) -> Union[int, None]:
        """
        アイテムIDからその数量を取得します

        :param item_id: アイテムID
        :return: 数量(見つからなかった場合はNoneを返却)
        """

        for i in self.later:
            if i.id == item_id:
                return self.later[i]
        return None

    @staticmethod
    def delete(mc_uuid: str, item: Union[int, 'util.Item']) -> bool:
        """
        あとで買うからアイテムを削除します

        :param mc_uuid: MinecraftのUUID
        :param item: アイテムIDまたはItem型
        :return: 成功したか
        """

        if isinstance(item, int):
            return util.DatabaseHelper.delete_later(mc_uuid, item)
        elif isinstance(item, util.Item):
            return util.DatabaseHelper.delete_later(mc_uuid, item.id)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @staticmethod
    def add(mc_uuid: str, item: Union[int, 'util.Item'], qty: int) -> bool:
        """
        あとで買うにアイテムを追加します

        :param mc_uuid: MinecraftのUUID
        :param item: アイテムIDまたはItem型
        :param qty: 数量
        :return: 成功したか
        """

        if isinstance(item, int):
            return util.DatabaseHelper.add_later(mc_uuid, item, qty)
        elif isinstance(item, util.Item):
            return util.DatabaseHelper.add_later(mc_uuid, item.id, qty)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @staticmethod
    def update_qty(mc_uuid: str, item: Union[int, 'util.Item'], qty: int) -> bool:
        """
        あとで買う内のアイテムの数量を指定された数量に更新します

        :param mc_uuid: MinecraftのUUId
        :param item: アイテムIDまたはItem型
        :param qty: 数量
        :return: 成功したか
        """

        if isinstance(item, int):
            return util.DatabaseHelper.update_later(mc_uuid, item, qty)
        elif isinstance(item, util.Item):
            return util.DatabaseHelper.update_later(mc_uuid, item.id, qty)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @staticmethod
    def by_mc_uuid(mc_uuid: str) -> 'Later':
        """
        UUIDからLater型を取得します

        :param mc_uuid: MinecraftのUUID
        :return: Later型(アイテムが見つからなかった場合はNoneを挿入)
        """

        r = util.DatabaseHelper.get_later(mc_uuid)

        if not r:
            return Later()

        later = {util.Item.by_id(i["item_id"]): i["quantity"] for i in r}
        return Later(later)
