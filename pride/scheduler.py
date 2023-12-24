import asyncio

from apscheduler.schedulers.background import BackgroundScheduler

import bot
from util import *

allocation_per = Decimal(str(settings.ALLOCATION_PER)) / Decimal(100)
scheduler = BackgroundScheduler()


def expires_check():
    print("===============================")
    r = Pride.all()
    now = datetime.datetime.now()

    connection_error = False
    for i in r:
        if i.expires_at < now:
            if i.automatically_renew:
                try:
                    withdraw = i.get_user().withdraw(i.plan.pricing,
                                                     "ウェブショップ『Utazon』でPrideの自動更新",
                                                     f"YEARLY({i.plan.pricing}/{i.plan.jp}額)")
                    print(withdraw)
                    if withdraw:
                        i.renew()
                        asyncio.run_coroutine_threadsafe(
                            bot.send_automatically_renew(i.get_user().get_discord_id()),
                            bot.client.loop
                        )
                    else:
                        i.disable()
                        asyncio.run_coroutine_threadsafe(
                            bot.fail_automatically_renew(i.get_user().get_discord_id()),
                            bot.client.loop
                        )
                except ConnectionRefusedError:
                    connection_error = True
                    continue

            else:
                i.disable()
    if connection_error:
        scheduler.add_job(expires_check,
                          'date',
                          run_date=datetime.datetime.now() + datetime.timedelta(minutes=1)
                          )


def start():
    scheduler.add_job(expires_check, 'cron', hour=0)
    scheduler.start()
