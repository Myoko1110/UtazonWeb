from _decimal import Decimal
from apscheduler.schedulers.background import BackgroundScheduler

import util
from config import settings

allocation_per = Decimal(str(settings.ALLOCATION_PER)) / Decimal(100)

def deposit_revenues():
    revenues = util.DatabaseHelper.get_revenues()

    revenues_list = {}
    for i in revenues:
        amount = i["amount"]
        sale_by = i["sale_by"]
        item_id = i["item_id"]
        item_price = i["item_price"]
        qty = i["qty"]

        if sale_by in revenues_list.keys():
            array = revenues_list[sale_by]
            array["amount"] += amount
            if item_id in array["items"].keys():
                array["items"][item_id]["qty"] += qty
            else:
                array["items"][item_id] = {}
                array["items"][item_id]["item_price"] = item_price
                array["items"][item_id]["qty"] = qty
            revenues_list[sale_by] = array

        else:
            array = {
                "amount": amount,
                "items": {
                    item_id: {
                        "item_price": item_price,
                        "qty": qty,
                    }
                }
            }
            revenues_list[sale_by] = array

    for key, value in revenues_list.items():
        sale_by = key
        amount = float(Decimal(str(value["amount"])) * allocation_per)

        reason_list = []
        for i, j in value["items"].items():
            total_amount = Decimal(str(j["item_price"])) * Decimal(str(j["qty"]))
            reason_list.append(f"{i}({j['qty']}個:{total_amount})")

        reason = ", ".join(reason_list) + f"(この配分額率{settings.ALLOCATION_PER}%)"

        util.SocketHelper.deposit_revenues(sale_by, amount, reason)
        util.DatabaseHelper.delete_revenues()


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(deposit_revenues, 'cron', hour=0)
    scheduler.start()
