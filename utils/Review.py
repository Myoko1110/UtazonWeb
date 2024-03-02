import datetime
from enum import Enum
from typing import Union
from uuid import UUID

import utils


class Review:
    item_id: int
    id: int
    created_at: datetime
    updated_at: datetime
    star: int
    title: str
    value: str
    helpful: int
    mc_uuid: UUID
    mc_id: str
    type: 'ReviewType'

    def __init__(
            self,
            item_id,
            id,
            created_at,
            updated_at,
            star,
            title,
            value,
            helpful,
            mc_uuid,
            mc_id,
            type: 'ReviewType'
    ):
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

    def __dict__(self):
        return {
            "item_id": self.item_id,
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "star": self.star,
            "title": self.title,
            "value": self.value,
            "helpful": self.helpful,
            "mc_uuid": self.mc_uuid,
            "mc_id": self.mc_id,
            "type": self.type,
        }

    def __str__(self):
        return "Review" + str(self.__dict__())

    def __repr__(self):
        return (f"Review({self.item_id.__repr__()}, {self.id.__repr__()}, {self.created_at.__repr__()}, {self.updated_at.__repr__()}, {self.star.__repr__()}, "
                f"{self.title.__repr__()}, {self.value.__repr__()}, {self.helpful.__repr__()}, {self.mc_uuid.__repr__()}, {self.mc_id.__repr__()}, {self.type.__repr__()})")

    def is_review(self) -> bool:
        """
        レビューであるかを取得します

        :return: 通常のレビューか
        """
        return self.type == ReviewType.REVIEW

    def is_rating(self) -> bool:
        """
        評価であるかを取得します

        :return: 評価のみのレビューか
        """

        return self.type == ReviewType.RATING

    @staticmethod
    def add_review(mc_uuid: UUID, item: Union[int, 'utils.Item'], star: int, title: str,
                   value: str) -> bool:
        """
        商品のレビューを追加します

        :param mc_uuid: MinecraftUUID
        :param item: アイテムIDまたはItem型
        :param star: 評価
        :param title: レビューのタイトル
        :param value: レビューの本文
        :return: 成功したか
        """

        if isinstance(item, int):
            return utils.DatabaseHelper.add_review(
                str(mc_uuid), item, star, title, value, ReviewType.REVIEW.name
            )
        elif isinstance(item, utils.Item):
            return utils.DatabaseHelper.add_review(
                str(mc_uuid), item.id, star, title, value, ReviewType.REVIEW.name
            )
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @staticmethod
    def add_rating(mc_uuid: UUID, item: Union[int, 'utils.Item'], star: int) -> bool:
        """
        商品の評価を追加します

        :param mc_uuid: MinecraftUUID
        :param item: アイテムIDまたはItem型
        :param star: 評価
        :return: 成功したか
        """

        if isinstance(item, int):
            return utils.DatabaseHelper.add_review(
                str(mc_uuid), item, star, None, None, ReviewType.RATING.name
            )
        elif isinstance(item, utils.Item):
            return utils.DatabaseHelper.add_review(
                str(mc_uuid), item.id, star, None, None, ReviewType.RATING.name
            )
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @staticmethod
    def update(mc_uuid: UUID, item: Union[int, 'utils.Item'], star: int, title: str,
               value: str) -> bool:
        """
        商品のレビューを追加します

        :param mc_uuid: MinecraftUUID
        :param item: アイテムIDまたはItem型
        :param star: 評価
        :param title: レビューのタイトル
        :param value: レビューの本文
        :return: 成功したか
        """

        if isinstance(item, int):
            return utils.DatabaseHelper.update_review(str(mc_uuid), item, star, title, value)
        elif isinstance(item, utils.Item):
            return utils.DatabaseHelper.update_review(str(mc_uuid), item.id, star, title, value)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @staticmethod
    def helpful(item: Union[int, 'utils.Item'], review_id: int) -> bool:
        """
        商品のレビューに役に立ったを追加します

        :param item: アイテムIDまたはItem型
        :param review_id: レビューID
        :return: 成功したか
        """

        if isinstance(item, int):
            return utils.DatabaseHelper.helpful_review(item, review_id)
        elif isinstance(item, utils.Item):
            return utils.DatabaseHelper.helpful_review(item.id, review_id)
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @staticmethod
    def has_review(mc_uuid: UUID, item: int) -> bool:
        """
        レビューが存在するか取得します

        :param mc_uuid: MinecraftUUID
        :param item: アイテムIDまたはItem型
        :return: 存在するか
        """

        if isinstance(item, int):
            return bool(utils.DatabaseHelper.check_review(str(mc_uuid), item)[0])
        elif isinstance(item, utils.Item):
            return bool(utils.DatabaseHelper.check_review(str(mc_uuid), item.id)[0])
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @staticmethod
    def has_rating(mc_uuid: UUID, item: Union[int, 'utils.Item']) -> bool:
        """
        レビューが存在するか取得します

        :param mc_uuid: MinecraftUUID
        :param item: アイテムIDまたはItem型
        :return: 存在するか
        """

        if isinstance(item, int):
            return bool(utils.DatabaseHelper.check_rating(str(mc_uuid), item)[0])
        elif isinstance(item, utils.Item):
            return bool(utils.DatabaseHelper.check_rating(str(mc_uuid), item.id)[0])
        else:
            TypeError(f"'{type(item)}'は使用できません")

    @staticmethod
    def by_mc_uuid(mc_uuid: UUID, item: Union[int, 'utils.Item']) -> Union['Review', None]:
        """
        UUIDと指定されたアイテムIDからレビューを取得します

        :param mc_uuid: MinecraftUUID
        :param item: アイテムIDまたはItem型
        :return: Review型
        """

        r = None
        if isinstance(item, int):
            r = utils.DatabaseHelper.get_review_by_mc_uuid(str(mc_uuid), item)
        elif isinstance(item, utils.Item):
            r = utils.DatabaseHelper.get_review_by_mc_uuid(str(mc_uuid), item.id)
        else:
            TypeError(f"'{type(item)}'は使用できません")

        if not r:
            return None
        return Review(r["item_id"], r["id"], r["created_at"], r["updated_at"], r["rating"],
                      r["title"], r["value"], r["helpful_votes"], UUID(r["mc_uuid"]),
                      utils.User.by_mc_uuid(r["mc_uuid"]).mc_id, ReviewType(r["type"]))


class ReviewType(Enum):
    REVIEW = "REVIEW"
    RATING = "RATING"
