from apscheduler.schedulers.background import BackgroundScheduler

from utils import *

allocation_per = Decimal(str(settings.ALLOCATION_PER)) / Decimal(100)


def deposit_revenues():
    revenues = Revenues.get()

    revenues_list = {}
    for i in revenues:

        # 既に販売者があったら
        if i.seller in revenues_list.keys():
            array = revenues_list[i.seller]
            array["total"] += Decimal(str(i.total))

            # 既に商品があったら
            if i.item_id in array["items"].keys():
                array["items"][i.item_id]["qty"] += i.qty
            else:
                array["items"][i.item_id] = {}
                array["items"][i.item_id]["price"] = i.item_price
                array["items"][i.item_id]["qty"] = i.qty
            revenues_list[i.seller] = array

        else:
            array = {
                "total": Decimal(str(i.total)),
                "items": {
                    i.item_id: {
                        "price": i.item_price,
                        "qty": i.qty,
                    }
                }
            }
            revenues_list[i.seller] = array

    for seller, value in revenues_list.items():
        total = float(Decimal(str(value["total"])) * allocation_per)

        reason_list = []
        for i, j in value["items"].items():
            reason_list.append(f"{i}({j['qty']}個:{j['price']})")

        reason = ", ".join(reason_list) + f"(入金額: {value['total']}の{settings.ALLOCATION_PER}%)"

        try:
            if User.by_mc_uuid(seller).deposit(total, "ウェブショップ『Utazon』からの売上入金", reason):
                Revenues.delete(seller)
        except ConnectionRefusedError:
            continue


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(deposit_revenues, 'cron', hour=0)
    scheduler.start()
