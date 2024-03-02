import datetime
from enum import Enum
from typing import Union
from uuid import UUID

import utils
from config import settings


class Pride:
    mc_uuid: UUID
    status: bool
    plan: 'PridePlan'
    registered_at: datetime
    expires_at: datetime
    automatically_renew: bool

    def __init__(
            self,
            mc_uuid: UUID,
            status: bool,
            plan: 'PridePlan',
            registered_at: datetime,
            expires_at: datetime,
            automatically_renew: bool
    ):
        self.mc_uuid = mc_uuid
        self.status = status
        self.registered_at = registered_at
        self.expires_at = expires_at
        self.automatically_renew = automatically_renew
        self.plan = plan

    def __dict__(self):
        return {
            "mc_uuid": self.mc_uuid,
            "status": self.status,
            "plan": self.plan,
            "registered_at": self.registered_at,
            "expires_at": self.expires_at,
            "automatically_renew": self.automatically_renew,
        }

    def __str__(self):
        return "Pride" + str(self.__dict__())

    def __repr__(self):
        return (f"Pride({self.mc_uuid.__repr__()}, {self.status.__repr__()}, {self.plan.__repr__()}, {self.registered_at.__repr__()}, "
                f"{self.expires_at.__repr__()}, {self.automatically_renew.__repr__()})")

    def renew(self) -> bool:
        """
        Prideを更新します

        :return: 成功したか
        """

        now = datetime.datetime.now()
        if self.plan == PridePlan.MONTHLY:
            expires = now + datetime.timedelta(days=30)
        else:
            expires = now + datetime.timedelta(days=365)
        expires = expires.replace(hour=0, minute=0, second=0, microsecond=0)

        return utils.DatabaseHelper.renew_pride(str(self.mc_uuid), expires)

    def disable(self):
        """
        Prideを無効にします

        :return: 成功したか
        """

        return utils.DatabaseHelper.disable_pride(str(self.mc_uuid))

    @property
    def user(self) -> Union[None, 'utils.User']:
        """
        User型を取得します

        :return: User型
        """

        return utils.User.by_mc_uuid(self.mc_uuid)

    @staticmethod
    def disable_and_renew():
        """
        自動更新・無効にします
        """

        r = Pride.all()
        now = datetime.datetime.now()

        for i in r:
            if i.expires_at < now:
                if i.automatically_renew:
                    i.renew()
                else:
                    i.disable()

    @staticmethod
    def all() -> list['Pride']:
        """
        すべて取得します

        :return: Pride型のリスト
        """

        r = utils.DatabaseHelper.get_pride_all()
        return [Pride(UUID(i["mc_uuid"]), bool(i["status"]), PridePlan(i["plan"]),
                      i["registered_at"], i["expires_at"], bool(i["automatically_renew"]))
                for i in r]

    @staticmethod
    def by_mc_uuid(mc_uuid: UUID):
        """
        MinecraftUUIDからPrime型を取得します

        :param mc_uuid:
        :return:
        """

        r = utils.DatabaseHelper.get_pride(str(mc_uuid))

        if not r:
            return None

        return Pride(UUID(r["mc_uuid"]), bool(r["status"]), PridePlan(r["plan"]),
                     r["registered_at"], r["expires_at"], bool(r["automatically_renew"]))


class PridePlan(Enum):
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"

    def __init__(self, plan):
        if plan == "MONTHLY":
            self.pricing = settings.PRIDE_MONTHLY
            self.jp = "月"
        else:
            self.pricing = settings.PRIDE_YEARLY
            self.jp = "年"
