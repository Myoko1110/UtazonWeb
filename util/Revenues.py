import datetime

import util


class Revenues:
    id: int
    mc_uuid: str
    item_id: int
    item_price: float
    qty: int
    total: float
    bought_at: datetime.datetime
    seller: str

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

    @staticmethod
    def get() -> list['Revenues']:
        r = util.DatabaseHelper.get_revenues()
        return [Revenues(i["id"], i["mc_uuid"], i["item_id"], i["item_price"], i["qty"],
                         i["total"], i["bought_at"], i["seller_uuid"]) for i in r]

    @staticmethod
    def delete(seller_uuid: str) -> bool:
        return util.DatabaseHelper.delete_revenues(seller_uuid)
