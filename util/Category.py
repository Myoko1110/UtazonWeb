from typing import Union

import util
from config import settings


class Category:
    english: str
    japanese: str

    is_parent: bool
    is_child: bool

    def __init__(self, en: str, jp: str, is_parent: bool):
        self.english = en
        self.japanese = jp

        self.is_parent = is_parent
        if is_parent:
            self.is_child = False
        else:
            self.is_child = True

    def __str__(self):
        if self.is_parent:
            type = "PARENT"
        else:
            type = "CHILD"

        return f"Category{{type: {type}, english: {self.english}, japanese: {self.japanese}}}"

    def get_parent(self) -> Union['Category', None]:
        """
        子カテゴリーから親カテゴリーを取得します

        :return: 親のCategory型(参照元が親カテゴリーの場合はNoneを返却)
        """

        if self.is_parent:
            return None
        for key, value in settings.CATEGORIES.items():
            for i, j in value["category"].items():
                if i == self.english:
                    return Category(key, value["japanese"], True)

        return None

    def get_child(self) -> Union[list['Category'], None]:
        """
        親カテゴリーから子カテゴリーを取得します

        :return: 子のCategory型のリスト(参照元が子カテゴリーの場合はNoneを返却)
        """

        if self.is_child:
            return None
        array = []
        for key, value in settings.CATEGORIES[self.english]["category"].items():
            array.append(Category(key, value, False))

        return array

    def get_item(self) -> list['util.Item']:
        """
        カテゴリーのアイテムを取得します

        :return: カテゴリーのアイテム
        """

        if self.is_parent:
            # 子カテゴリーを取得 -> 子カテゴリーからアイテム取得 -> 複数の結果を同じ変数に入れる
            return [util.Item.by_db(j) for i in self.get_child()
                    for j in util.DatabaseHelper.get_item_by_category(i.english)]

        else:
            return [util.Item.by_db(i)
                    for i in util.DatabaseHelper.get_item_by_category(self.english)]

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
                    return Category(key, value["japanese"], True)
                except TypeError:
                    return Category(key, value, True)

            if isinstance(value, dict):
                for i, j in value["category"].items():
                    if i == english:
                        return Category(i, j, False)
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
                return Category(key, value, True)

            for i, j in value["category"].items():
                if j == japanese:
                    return Category(i, j, False)
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
