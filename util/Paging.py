import math
from typing import Any, Union


class Paging:
    """
    Item型のリスト
    """

    result: Union[list, tuple] = None  # ページングの結果
    result_length: int = None  # 結果数
    page_length: int = None  # ページングのページ数
    has_prev: bool = None  # 前のページがあるか
    has_next: bool = None  # 次のページがあるか
    page_list: range = None  # for文で表示するようのリスト
    page: int = None  # 現在のページ
    first_index: int = None  # ページング結果の最初のIndex
    last_index: int = None  # ページング結果の最後のIndex

    def __init__(self, result, page, page_length):
        self.page = page

        if result:
            self.result_length = len(result)
            self.page_length = math.ceil(self.result_length / page_length)

            self.first_index = (page - 1) * page_length
            self.last_index = page * page_length

            if self.last_index > self.result_length:
                self.last_index = self.result_length

            self.result: list[Union[Any, None]] = result[self.first_index:self.last_index]

            if self.first_index == 0:
                self.has_prev = False
            else:
                self.has_prev = True

            if self.last_index == self.result_length:
                self.has_next = False
            else:
                self.has_next = True
            self.page_list = Paging.generate_range(self.page_length, self.page)

    def get_next(self) -> int:
        """
        次のページのページ数を取得します

        :return: 次のページのページ数
        """

        return self.page + 1

    def get_prev(self) -> int:
        """
        前のページのページ数を取得します

        :return: 前のページのページ数
        """

        return self.page - 1

    def get_first_index(self) -> int:
        """
        ページングした最初の商品の◯件目を取得します

        :return: 最初の商品の◯件目
        """

        return self.first_index + 1

    def get_last_index(self) -> int:
        """
        ページングした最後の商品の◯件目を取得します

        :return: 最後の商品の◯件目
        """

        return self.last_index + 1

    @staticmethod
    def generate_range(upper_limit, specified_number):
        """
        指定されたページ数から、指定されたページ真ん中にする５つの数字を挿入したリストを作成します

        :param upper_limit: ページ数
        :param specified_number: 指定するページ
        :return:
        """

        if upper_limit <= 0:
            return ()

        # 範囲の中央値を計算
        mid = specified_number - 1  # 0-based
        half_length = 2  # 範囲の半分の長さを設定

        # 中央値周りの範囲を計算
        start = max(mid - half_length, 0)
        end = min(mid + half_length + 1, upper_limit)

        # 範囲が5個になるように調整
        while end - start < 5 and (start > 0 or end < upper_limit):
            if start > 0:
                start -= 1
            elif end < upper_limit:
                end += 1

        # 1-based
        start += 1
        end += 1

        return range(start, end)
