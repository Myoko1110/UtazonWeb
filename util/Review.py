import datetime
from typing import Union

import util


class Review:
    item_id: int
    id: int
    created_at: datetime
    updated_at: datetime
    star: int
    title: str
    value: str
    helpful: int
    mc_uuid: str
    mc_id: str
    type: str

    def __init__(self, item_id, id, created_at, updated_at, star, title, value, helpful, mc_uuid,
                 mc_id, type):
        self.item_id = item_id
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.star = star
        self.title = title
        self.value = value
        self.helpful = helpful
        self.mc_uuid = mc_uuid
        self.mc_id = mc_id
        self.type = type

    def __str__(self):
        return f"Review{{id: {self.id}, item_id: {self.item_id}}}"

    def is_review(self) -> bool:
        """
        レビューであるかを取得します

        :return: 通常のレビューか
        """

        return self.type == "REVIEW"

    def is_rating(self) -> bool:
        """
        評価であるかを取得します

        :return: 評価のみのレビューか
        """

        return self.type == "RATING"

    @staticmethod
    def add_review(mc_uuid: str, item: Union[int, 'util.Item'], star: int, title: str, value: str) -> bool:
        """
        商品のレビューを追加します

        :param mc_uuid: MinecraftのUUID
        :param item: アイテムIDまたはItem型
        :param star: 評価
        :param title: レビューのタイトル
        :param value: レビューの本文
        :return: 成功したか
        """

        if isinstance(item, int):
            return util.DatabaseHelper.add_review(mc_uuid, item, star, title, value, "REVIEW")
        elif isinstance(item, util.Item):
            return util.DatabaseHelper.add_review(mc_uuid, item.id, star, title, value, "REVIEW")
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @staticmethod
    def add_rating(mc_uuid: str, item: Union[int, 'util.Item'], star: int) -> bool:
        """
        商品の評価を追加します

        :param mc_uuid: MinecraftのUUID
        :param item: アイテムIDまたはItem型
        :param star: 評価
        :return: 成功したか
        """

        if isinstance(item, int):
            return util.DatabaseHelper.add_review(mc_uuid, item, star, None, None, "RATING")
        elif isinstance(item, util.Item):
            return util.DatabaseHelper.add_review(mc_uuid, item.id, star, None, None, "RATING")
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @staticmethod
    def update(mc_uuid: str, item: Union[int, 'util.Item'], star: int, title: str, value: str) -> bool:
        """
        商品のレビューを追加します

        :param mc_uuid: MinecraftのUUID
        :param item: アイテムIDまたはItem型
        :param star: 評価
        :param title: レビューのタイトル
        :param value: レビューの本文
        :return: 成功したか
        """

        if isinstance(item, int):
            return util.DatabaseHelper.update_review(mc_uuid, item, star, title, value)
        elif isinstance(item, util.Item):
            return util.DatabaseHelper.update_review(mc_uuid, item.id, star, title, value)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @staticmethod
    def helpful(item: Union[int, 'util.Item'], review_id: int) -> bool:
        """
        商品のレビューに役に立ったを追加します

        :param item: アイテムIDまたはItem型
        :param review_id: レビューID
        :return: 成功したか
        """

        if isinstance(item, int):
            return util.DatabaseHelper.helpful_review(item, review_id)
        elif isinstance(item, util.Item):
            return util.DatabaseHelper.helpful_review(item.id, review_id)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @staticmethod
    def has_review(mc_uuid: str, item: int) -> bool:
        """
        レビューが存在するか取得します

        :param mc_uuid: MinecraftのUUID
        :param item: アイテムIDまたはItem型
        :return: 存在するか
        """

        if isinstance(item, int):
            return bool(util.DatabaseHelper.check_review(mc_uuid, item)[0])
        elif isinstance(item, util.Item):
            return bool(util.DatabaseHelper.check_review(mc_uuid, item.id)[0])
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @staticmethod
    def has_rating(mc_uuid: str, item: Union[int, 'util.Item']) -> bool:
        """
        レビューが存在するか取得します

        :param mc_uuid: MinecraftのUUID
        :param item: アイテムIDまたはItem型
        :return: 存在するか
        """

        if isinstance(item, int):
            return bool(util.DatabaseHelper.check_rating(mc_uuid, item)[0])
        elif isinstance(item, util.Item):
            return bool(util.DatabaseHelper.check_rating(mc_uuid, item.id)[0])
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @staticmethod
    def by_mc_uuid(mc_uuid: str, item: Union[int, 'util.Item']) -> Union['Review', None]:
        """
        UUIDと指定されたアイテムIDからレビューを取得します

        :param mc_uuid: MinecraftのUUID
        :param item: アイテムIDまたはItem型
        :return: Review型
        """

        r = None
        if isinstance(item, int):
            r = util.DatabaseHelper.get_review_by_mc_uuid(mc_uuid, item)
        elif isinstance(item, util.Item):
            r = util.DatabaseHelper.get_review_by_mc_uuid(mc_uuid, item.id)
        else:
            TypeError(f"'{type(item)}'は使用できません")

        if not r:
            return None

        return Review(r["item_id"], r["id"], r["created_at"], r["updated_at"], r["rating"],
                      r["title"], r["value"], r["helpful_votes"], r["mc_uuid"],
                      util.User.by_mc_uuid(r["mc_uuid"]).get_mc_id(), r["type"])
