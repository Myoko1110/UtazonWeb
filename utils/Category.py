from enum import Enum
from typing import Union

import utils
from config import settings


class Category:
    english: str
    japanese: str
    type: 'CategoryType'

    def __init__(
            self,
            en: str,
            jp: str,
            type: 'CategoryType',
    ):
        self.english = en
        self.japanese = jp
        self.type = type

    def __dict__(self):
        return {
            "english": self.english,
            "japanese": self.japanese,
            "type": self.type,
        }

    def __str__(self):
        return "Category" + str(self.__dict__())

    def __repr__(self):
        return f"Category({self.english.__repr__()}, {self.japanese.__repr__()}, {self.type.__repr__()})"

    def is_parent(self) -> bool:
        """
        親カテゴリーか取得します

        :return: 親カテゴリーか
        """

        return self.type == CategoryType.PARENT

    def is_child(self) -> bool:
        """
        子カテゴリーか取得します

        :return: 子カテゴリーか
        """

        return self.type == CategoryType.CHILD

    def get_parent(self) -> Union['Category', None]:
        """
        子カテゴリーから親カテゴリーを取得します

        :return: 親のCategory型(参照元が親カテゴリーの場合はNoneを返却)
        """

        if self.type == CategoryType.PARENT:
            return None
        for key, value in settings.CATEGORIES.items():
            for i, j in value["category"].items():
                if i == self.english:
                    return Category(key, value["japanese"], CategoryType.PARENT)

        return None

    def get_child(self) -> Union[list['Category'], None]:
        """
        親カテゴリーから子カテゴリーを取得します

        :return: 子のCategory型のリスト(参照元が子カテゴリーの場合はNoneを返却)
        """

        if self.type == CategoryType.CHILD:
            return None
        array = []
        for key, value in settings.CATEGORIES[self.english]["category"].items():
            array.append(Category(key, value, CategoryType.CHILD))

        return array

    def get_item(self) -> list['utils.Item']:
        """
        カテゴリーのアイテムを取得します

        :return: カテゴリーのアイテム
        """

        if self.type == CategoryType.PARENT:
            # 子カテゴリーを取得 -> 子カテゴリーからアイテム取得 -> 複数の結果を同じ変数に入れる
            return [utils.Item.by_db(j) for i in self.get_child()
                    for j in utils.DatabaseHelper.get_item_by_category(i.english)]

        else:
            return [utils.Item.by_db(i)
                    for i in utils.DatabaseHelper.get_item_by_category(self.english)]

    @staticmethod
    def by_english(english: str) -> Union['Category', None]:
        """
        英語のカテゴリー名からカテゴリー型を取得します

        :param english: 英語のカテゴリー名
        :return: Category型(見つからなかった場合はNoneを返却)
        """

        for key, value in settings.CATEGORIES.items():
            if key == english:
                try:
                    return Category(key, value["japanese"], CategoryType.PARENT)
                except TypeError:
                    return Category(key, value, CategoryType.PARENT)

            if isinstance(value, dict):
                for i, j in value["category"].items():
                    if i == english:
                        return Category(i, j, CategoryType.CHILD)
        return None

    @staticmethod
    def by_japanese(japanese: str) -> Union['Category', None]:
        """
        日本語のカテゴリー名からカテゴリー型を取得します

        :param japanese: 日本語のカテゴリー名
        :return: Category型(見つからなかった場合はNoneを返却)
        """

        for key, value in settings.CATEGORIES.items():
            if value == japanese:
                return Category(key, value, CategoryType.PARENT)

            for i, j in value["category"].items():
                if j == japanese:
                    return Category(i, j, CategoryType.CHILD)
        return None

    @staticmethod
    def all():
        """
        全てのカテゴリーを取得します

        :return: 全てのカテゴリー
        """

        result = {}

        for i in settings.CATEGORIES.keys():
            try:
                category_jp = settings.CATEGORIES[i]["japanese"]
                result[i] = category_jp
            except TypeError:
                pass

        return result


class CategoryType(Enum):
    PARENT = "PARENT"
    CHILD = "CHILD"
