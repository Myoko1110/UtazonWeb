import datetime
from uuid import UUID

import utils


class Revenues:
    id: int
    mc_uuid: UUID
    item_id: int
    item_price: float
    qty: int
    total: float
    bought_at: datetime.datetime
    seller: UUID

    def __init__(
            self,
            id,
            mc_uuid,
            item_id,
            item_price,
            qty,
            total,
            bought_at,
            seller
    ):
        self.id = id
        self.mc_uuid = mc_uuid
        self.item_id = item_id
        self.item_price = item_price
        self.qty = qty
        self.total = total
        self.bought_at = bought_at
        self.seller = seller

    def __dict__(self):
        return {
            "id": self.id,
            "mc_uuid": self.mc_uuid,
            "item_id": self.item_id,
            "item_price": self.item_price,
            "qty": self.qty,
            "total": self.total,
            "bought_at": self.bought_at,
            "seller": self.seller
        }

    def __str__(self):
        return "Revenues" + str(self.__dict__())

    def __repr__(self):
        return (f"Revenues({self.id.__repr__()}, {self.mc_uuid.__repr__()}, {self.item_id.__repr__()}, {self.item_price.__repr__()}, {self.qty.__repr__()}, "
                f"{self.total.__repr__()}, {self.bought_at.__repr__()}, {self.seller.__repr__()})")

    @staticmethod
    def get() -> list['Revenues']:
        """
        収入情報を取得します

        :return: 収入情報
        """

        r = utils.DatabaseHelper.get_revenues()
        return [Revenues(i["id"], UUID(i["mc_uuid"]), i["item_id"], i["item_price"], i["qty"],
                         i["total"], i["bought_at"], UUID(i["seller_uuid"])) for i in r]

    @staticmethod
    def delete(seller_uuid: UUID) -> bool:
        """
        収入情報を削除します

        :param seller_uuid: MinecraftUUID
        :return: 成功したか
        """

        return utils.DatabaseHelper.delete_revenues(str(seller_uuid))
