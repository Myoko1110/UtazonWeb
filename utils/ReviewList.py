from collections import UserList
from statistics import mean
from typing import Union
from uuid import UUID

from typing_extensions import deprecated

import utils


class ReviewList(UserList):
    def __init__(self, reviews: list['utils.Review']):
        super().__init__(reviews)

    def __str__(self):
        return "ReviewList" + super().__str__()

    def __repr__(self):
        return f"({self.data})"

    @property
    def average(self) -> float:
        """
        レビュー型のリストからレビューの平均を取得します

        :return: レビューの平均
        """

        if not self.data:
            return 0

        star_list = [i.star for i in self.data]
        return round(mean(star_list), 1)

    @property
    def reviews(self) -> list['utils.Review']:
        """
        レビューの数を取得します

        :return: 有効なレビュー数
        """

        return [i for i in self.data if i.type == utils.ReviewType.REVIEW]

    @property
    def ratings(self) -> list['utils.Review']:
        """
        評価(レビューを除く)の数を取得します

        :return: 有効なレビュー数
        """

        return [i for i in self.data if i.type == utils.ReviewType.RATING]

    @deprecated
    def has_review(self) -> bool:
        """
        レビューが存在するか取得します

        :return: 存在するか
        """

        return any(i.type == utils.ReviewType.REVIEW for i in self.data)

    @deprecated
    def has_rating(self) -> bool:
        """
        評価が存在するか取得します

        :return: 存在するか
        """

        return any(i.type == utils.ReviewType.RATING for i in self.data)

    @staticmethod
    def by_item_id(item: Union[int, 'utils.Item']) -> Union['ReviewList', None]:
        """
        アイテムIDからレビュー型のリストを取得します

        :param item: アイテムIDまたはItem型
        :return: ReviewList型(結果なしはNoneを返却)
        """

        result = []
        if isinstance(item, int):
            result = utils.DatabaseHelper.get_review(item)
        elif isinstance(item, utils.Item):
            result = utils.DatabaseHelper.get_review(item.id)
        else:
            TypeError(f"'{type(item)}'は使用できません")

        if not result:
            return None

        i = [utils.Review(i["item_id"], i["id"], i["created_at"], i["updated_at"], i["rating"],
                          i["title"], i["value"], i["helpful_votes"], UUID(i["mc_uuid"]),
                          utils.User(UUID(i["mc_uuid"])).mc_id, utils.ReviewType(i["type"]))
             for i in result]

        return ReviewList(i)
