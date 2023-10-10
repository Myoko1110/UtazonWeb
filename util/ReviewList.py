from statistics import mean
from typing import Union

import util


class ReviewList:
    reviews: list['util.Review']

    def __init__(self, reviews: list['util.Review']):
        self.reviews = reviews

    def __getitem__(self, index):
        return self.reviews[index]

    def __len__(self):
        return len(self.reviews)

    def get_average(self) -> float:
        """
        レビュー型のリストからレビューの平均を取得します

        :return: レビューの平均
        """

        if not self.reviews:
            return 0

        star_list = [i.star for i in self.reviews]
        return round(mean(star_list), 1)

    def count_review(self) -> int:
        """
        レビューの数を取得します

        :return: 有効なレビュー数
        """

        return sum(1 for i in self.reviews if i.type == "REVIEW")

    def count_rating(self) -> int:
        """
        評価(レビューを除く)の数を取得します

        :return: 有効なレビュー数
        """

        return sum(1 for i in self.reviews if i.type == "RATING")

    def has_review(self) -> bool:
        """
        レビューが存在するか取得します

        :return: 存在するか
        """

        return any(i.type == "REVIEW" for i in self.reviews)

    def has_rating(self) -> bool:
        """
        評価が存在するか取得します

        :return: 存在するか
        """

        return any(i.type == "RATING" for i in self.reviews)

    @staticmethod
    def by_item_id(item: Union[int, 'util.Item']) -> Union['ReviewList', None]:
        """
        アイテムIDからレビュー型のリストを取得します

        :param item: アイテムIDまたはItem型
        :return: ReviewList型(結果なしはNoneを返却)
        """

        if isinstance(item, int):
            result = util.DatabaseHelper.get_review(item)
        elif isinstance(item, util.Item):
            result = util.DatabaseHelper.get_review(item.id)
        else:
            return None

        if not result:
            return None

        i = [util.Review(i["item_id"], i["id"], i["created_at"], i["updated_at"], i["rating"],
                         i["title"], i["value"], i["helpful_votes"], i["mc_uuid"],
                         util.User(i["mc_uuid"]).get_mc_id(), i["type"])
             for i in result]

        return ReviewList(i)
