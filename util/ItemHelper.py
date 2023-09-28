import datetime
import json
import math
import random
from decimal import Decimal, ROUND_UP
from statistics import mean

import util
from config import settings

point_return = Decimal(settings.POINT_RETURN)
point_return_percent = int(point_return * Decimal("100"))


class get_item:
    @staticmethod
    def id_list(items):
        """
        アイテムIDのリストからアイテム情報を取得します

        :param items: アイテムIDのリスト
        :return: 情報を追加したアイテムリスト
        """

        item_list = []
        for i in items:
            item_id = i

            # アイテム情報取得
            item_info = util.DatabaseHelper.get_item(item_id)
            if not item_info:
                continue

            # アイテムのセール情報を取得
            sale = util.ItemHelper.get_sale(item_info["sale_id"], item_info["price"])
            item_price = sale.item_price

            # 商品画像をlistにデコード
            item_info["image"] = json.loads(item_info["image"])

            # ポイント計算
            point = util.ItemHelper.calc_point(item_price)
            item_info["point"] = f"{point:,}"

            # アイテム価格など
            item_info["item_price"] = item_price
            item_info["item_price_format"] = f"{item_price:,.2f}"
            item_info["sale"] = sale

            # レビュー平均
            item_info["review"] = json.loads(item_info["review"])
            item_info["review_av"] = calc_review_average(item_info["review"])

            item_list.append(item_info)

        return item_list

    @staticmethod
    def obj_list(item_obj):
        """
        アイテムオブジェクトからアイテム情報を追加します

        :param item_obj: アイテム情報のあるアイテムリスト
        :return: 情報を追加したアイテムリスト
        """

        item_list = []
        for i in item_obj:
            # アイテム情報取得
            item_info = i

            # アイテムのセール情報を取得
            sale = util.ItemHelper.get_sale(item_info["sale_id"], item_info["price"])
            item_price = sale.item_price

            # 商品画像をlistにデコード
            item_info["image"] = json.loads(item_info["image"])

            # ポイント計算
            point = util.ItemHelper.calc_point(item_price)
            item_info["point"] = f"{point:,}"

            # アイテム価格など
            item_info["item_price"] = item_price
            item_info["item_price_format"] = f"{item_price:,.2f}"
            item_info["sale"] = sale

            # レビュー平均
            item_info["review"] = json.loads(item_info["review"])
            item_info["review_av"] = calc_review_average(item_info["review"])

            item_list.append(item_info)

        return item_list

    class cart_list:
        """
        アイテムIDと数量のリストからアイテム情報を取得します

        :param items: 数量情報のあるアイテムIDリスト
        :returns: 情報を追加したアイテムリスト
        """

        def __init__(self, items):
            self.item_list = []
            self.total_point = 0
            self.total_amount = 0
            self.total_qty = 0

            for i in items:
                item_id = i[0]
                item_qty = i[1]

                # アイテム情報取得
                result = util.DatabaseHelper.get_item(item_id)
                if not result:
                    continue

                # アイテムのセール情報を取得
                sale = util.ItemHelper.get_sale(result["sale_id"], result["price"])
                item_price = sale.item_price

                # 商品画像をlistにデコード
                result["image"] = json.loads(result["image"])

                # ポイント計算
                point = util.ItemHelper.calc_point(item_price)
                result["point"] = f"{point:,}"

                # 在庫取得
                result["stock"] = util.DatabaseHelper.get_item_stock(item_id)

                # トータルに追加
                total_item_price = Decimal(str(item_price)) * Decimal(str(i[1]))
                self.total_amount += total_item_price
                self.total_qty += item_qty
                self.total_point += point

                result["item_price"] = item_price
                result["item_price_format"] = f"{item_price:,.2f}"
                result["qty"] = item_qty
                result["sale"] = sale

                self.item_list.append(result)


class get_index_item:
    """
    インデックスアイテムを取得します
    """

    def __init__(self):
        self.popular_item = util.DatabaseHelper.get_popular_item()
        self.latest_item = util.DatabaseHelper.get_latest_item()
        special_feature = util.DatabaseHelper.get_special_feature()

        self.special_feature_list = {}
        for i in special_feature:
            item_list = i.value
            obj_list = []
            for j in item_list:
                item_obj = util.DatabaseHelper.get_item(j)
                if not item_obj:
                    continue
                item_obj["image"] = json.loads(item_obj["image"])
                obj_list.append(item_obj)
            self.special_feature_list[i.title] = obj_list

        for i in range(len(self.popular_item)):
            self.popular_item[i]["image"] = json.loads(self.popular_item[i]["image"])
        for i in range(len(self.latest_item)):
            self.latest_item[i]["image"] = json.loads(self.latest_item[i]["image"])


class get_sale:
    """
    アイテムIDからアイテムのセール情報を取得します

    :param sale_id: セールID(idカラム)
    :param item_price: アイテム価格
    """

    def __init__(self, sale_id, item_price):
        self.status = False
        self.discount_rate = None
        self.item_price = item_price
        self.past_price = 0
        self.item_price_format = f"{item_price:,.2f}"

        past_price = self.item_price_format

        # セール取得
        item_sale = util.DatabaseHelper.get_item_sale(sale_id)

        # セールが有効だったら
        if item_sale and item_sale["sale_status"]:

            # セール開催時間を確認
            status_per = util.calc_time_percentage(item_sale["sale_start"], item_sale["sale_end"])
            if status_per != 0.0 and status_per != 100.0:
                discount_rate = item_sale["discount_rate"]

                sale_per = Decimal(str(100 - discount_rate)) / Decimal("100")
                item_price = Decimal(str(item_price)) * sale_per
                item_price = item_price.quantize(Decimal(".01"), rounding=ROUND_UP)

                self.status = True
                self.discount_rate = discount_rate
                self.item_price = item_price
                self.past_price = past_price
                self.item_price_format = f"{item_price:,.2f}"


class get_category:
    class info:
        """
        カテゴリーの情報を取得します
        """

        class from_id:
            """
            カテゴリーIDからカテゴリー情報を取得します

            :param english: カテゴリー名
            :return: カテゴリー情報
            """

            def __init__(self, english):

                categories = settings.CATEGORIES
                for category, value in categories.items():

                    # englishが親カテゴリーだった時の処理
                    if category == english:
                        try:
                            self.jp = value["japanese"]
                            self.en = english
                            self.parent = None
                            return
                        except TypeError:
                            self.jp = value
                            self.en = english
                            self.parent = None
                            return

                    try:
                        for en, jp in value["category"].items():
                            # 該当のものが見つかったら
                            if en == english:
                                parent_jp = categories[category]["japanese"]
                                self.jp = jp
                                self.en = english
                                self.parent = {"en": category, "jp": parent_jp}
                                return

                    except AttributeError:
                        pass
                else:
                    self.jp = None
                    self.en = None
                    self.parent = None

    @staticmethod
    def child(parent_category):
        """
        親カテゴリーから子カテゴリーのを取得します

        :param parent_category: 親カテゴリー名
        :return: 子カテゴリー
        """

        categories = settings.CATEGORIES

        child_categories = categories[parent_category]["category"]

        return child_categories

    @staticmethod
    def all():
        """
        全てのカテゴリーを取得します

        :return: 全てのカテゴリー
        """

        categories = settings.CATEGORIES
        result = {}

        for i in categories.keys():
            try:
                category_jp = categories[i]["japanese"]
                result[category_jp] = i
            except TypeError:
                pass

        return result


def add_review_data(review_obj):
    """
    Webに表示するために必要なデータをレビューに追加します

    :param review_obj: レビュー
    :return: 必要な情報を追加したリスト
    """

    review_obj = list(review_obj)

    for i in review_obj:
        # item_reviewにmc情報を追加
        mc_uuid = i["mc_uuid"]
        mc_id = util.UserHelper.get_info.from_uuid(mc_uuid).mc_id
        i["mc_id"] = mc_id

    review_obj = review_obj
    return review_obj


def calc_delivery_time():
    """
    現在時刻からお届け時間を計算します

    :return: お届け時間(datetime型)
    """

    now = datetime.datetime.now()
    if now > datetime.datetime.strptime("13:00:00", "%H:%M:%S"):
        rand_time = now + datetime.timedelta(days=2)
    else:
        rand_time = now + datetime.timedelta(days=1)

    return rand_time


def calc_delivery_time_perfect():
    """
    正確なお届け時間を計算します

    :return: お届け時間(datetime型)
    """

    now = datetime.datetime.now().replace(microsecond=0)
    if now > datetime.datetime.strptime("13:00:00", "%H:%M:%S"):
        delivery_time = (now.replace(hour=random.randint(8, 18), minute=random.randint(0, 59),
                                     second=0, microsecond=0)
                         + datetime.timedelta(days=2))
    else:
        delivery_time = (now.replace(hour=random.randint(8, 18), minute=random.randint(0, 59),
                                     second=0, microsecond=0)
                         + datetime.timedelta(days=1))

    return delivery_time


def create_order_id():
    """
    オーダーIDを作成します
    :return: オーダーID
    """

    return (f"U{str(random.randint(0, 999)).zfill(3)}-" +
            f"{str(random.randint(0, 999999)).zfill(6)}-" +
            f"{str(random.randint(0, 999999)).zfill(6)}")


def calc_point(item_price):
    """
    アイテムの値段からポイント額を計算します

    :param item_price: アイテムID
    :return: ポイント額(int型)
    """

    return int(Decimal(str(item_price)) * point_return)


def calc_review_average(review_obj):
    """
    レビューのリストからレビューの平均を計算します

    :param review_obj: レビューのリスト
    :return: 平均値
    """
    if review_obj:
        review_star_list = [i["star"] for i in review_obj]
        review_average = round(mean(review_star_list), 1)
    else:
        review_average = None

    return review_average


def paging(result: list or tuple, page: int, count: int):
    """
    結果をページングします
    :return: [ページングした結果, 結果数, トータルのページ数, 次のページを表示可か, 前のページを表示可か, "ページングナビ用のrange"]
    """

    result_len = len(result)
    page_len = math.ceil(result_len / count)

    min_index = (page - 1) * count
    max_index = page * count

    if max_index > result_len:
        max_index = result_len

    result_paging = result[min_index:max_index]

    if min_index == 0:
        revable = False
    else:
        revable = True

    if max_index == result_len:
        nextable = False
    else:
        nextable = True
    page_range = generate_range(page_len, page)

    return result_paging, result_len, page_len, revable, nextable, page_range, min_index + 1, max_index


def generate_range(upper_limit, specified_number):
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
