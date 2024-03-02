import json
from typing import Union
from uuid import UUID

import utils


class ItemStack:
    stack_size: int
    damage: int
    material: str
    display_name: str
    enchantments: list
    stock: int = 0

    def __init__(
            self,
            stack_size: int,
            damage: int,
            material: str,
            display_name: str,
            enchantments: list,
            stock: int = 0
    ):
        self.stack_size = stack_size
        self.damage = damage
        self.material = material
        self.display_name = display_name
        self.enchantments = enchantments
        self.stock = stock

    def __dict__(self):
        return {
            "stack_size": self.stack_size,
            "damage": self.damage,
            "material": self.material,
            "display_name": self.display_name,
            "enchantments": self.enchantments,
            "stock": self.stock,
        }

    def __str__(self):
        return "ItemStack" + str(self.__dict__())

    def __repr__(self):
        return (f"ItemStack({self.stack_size.__repr__()}, {self.damage.__repr__()}, {self.material.__repr__()}, {self.display_name.__repr__()}, "
                f"{self.enchantments.__repr__()}, {self.stack_size.__repr__()})")

    def encode(self):
        """
        データベースに保存するようにエンコードします

        :return: エンコードした辞書
        """

        return {
            "amount": self.stack_size,
            "item_damage": self.damage,
            "item_material": self.material,
            "item_display_name": self.display_name,
            "item_enchantments": json.dumps(self.enchantments),
        }

    @staticmethod
    def by_item_id(item: Union[int, 'utils.Item']) -> Union['ItemStack', None]:
        """
        ItemStackを取得します

        :param item: アイテムIDまたはItem型
        :return: ItemStack型
        """
        r = {}
        if isinstance(item, int):
            r = utils.DatabaseHelper.get_item_stack(item)
        elif isinstance(item, utils.Item):
            r = utils.DatabaseHelper.get_item_stack(item.id)
        else:
            TypeError(f"'{type(item)}'は使用できません")

        if not r:
            return None

        return ItemStack(r["stack_size"], r["item_damage"], r["item_material"],
                         r["item_display_name"], json.loads(r["item_enchantments"]), r["stock"])

    @staticmethod
    def by_mc_uuid(mc_uuid: UUID) -> list[Union['ItemStack', None]]:
        """
        待機ストックを取得します

        :param mc_uuid: MinecraftUUID
        :return: ItemStack型
        """

        r = utils.DatabaseHelper.get_waiting_stock(str(mc_uuid))
        if not r:
            return [None for _ in range(54)]

        r = json.loads(r[0])
        return [None if not i
                else ItemStack(i["amount"], i["item_damage"], i["item_material"],
                               i["item_display_name"], json.loads(i["item_enchantments"]))
                for i in r]
