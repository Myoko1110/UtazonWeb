import datetime
from typing import Union

import utils


class Sale:
    status: bool = False
    discount_rate: Union[int, None]
    start: Union[datetime.datetime, None]
    end: Union[datetime.datetime, None]
    is_pride_only: Union[bool, None]

    def __init__(self, result):

        # 結果にセール情報が含まれるか確認
        if "sale_status" not in result.keys():
            self.status = False
            self.discount_rate = None
            self.start = None
            self.end = None
            self.is_pride_only = None

        else:
            if not result["sale_status"]:
                self.status = False
            else:

                # セール時間中か確認
                status = utils.calc_time_percentage(result["sale_start"], result["sale_end"])
                if status != 0 and status != 100:
                    self.status = True

            self.discount_rate = result["discount_rate"]
            self.start = result["sale_start"]
            self.end = result["sale_end"]
            self.is_pride_only = result["is_pride_only"]

    def __dict__(self):
        return {
            "status": self.status,
            "discount_rate": self.discount_rate,
            "start": self.status,
            "end": self.end,
            "is_pride_only": self.is_pride_only,
        }

    def __str__(self):
        return "Sale" + str(self.__dict__())

    def __repr__(self):
        return f"Sale({self.status.__repr__()}, {self.discount_rate.__repr__()}, {self.start.__repr__()}, {self.end.__repr__()}, {self.is_pride_only.__repr__()})"
