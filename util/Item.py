import asyncio
import datetime
import json
import secrets
import urllib.parse
from decimal import Decimal
from typing import Union

import bot
import util


class Item:
    sale_id: int
    id: int
    name: str
    price: float
    image: list
    kind: list
    detail: str
    category: str
    sold_count: int
    mc_uuid: str
    search_keyword: list
    created_at: datetime
    updated_at: datetime
    status: bool

    __cached_discount_price: Decimal
    __cached_stock: Union[int, None]

    def __init__(self, sale_id, id, name, price, image, kind, detail, category, sold_count, mc_uuid,
                 search_keyword, created_at, updated_at, status, sale_status, discount_rate,
                 start, end):

        # itemテーブル関係
        self.sale_id = sale_id
        self.id = id
        self.name = name
        self.price = price
        self.image = image
        self.kind = kind
        self.detail = detail
        self.category = category
        self.sold_count = sold_count
        self.mc_uuid = mc_uuid
        self.search_keyword = search_keyword
        self.created_at = created_at
        self.updated_at = updated_at
        self.status = status

        # saleテーブル関係
        self.sale_status = sale_status
        self.discount_rate = discount_rate
        self.sale_start = start
        self.sale_end = end

        self.__cached_discount_price = Decimal()
        self.__cached_stock = None

    def __str__(self):
        return f"Item{{id: {self.id}, name: {self.name}, price: {self.price}}}"

    def get_review(self) -> Union['util.ReviewList', None]:
        """
        レビュー型を取得します

        :return: Review型
        """

        return util.ReviewList.by_item_id(self.id)

    def get_stock(self) -> int:
        """
        在庫を取得します

        :return: 在庫
        """

        if not self.__cached_stock:
            self.__cached_stock = util.DatabaseHelper.get_stock(self.id)[0]
        return self.__cached_stock

    def reduce_stock(self, qty: int) -> bool:
        """
        在庫を減らします

        :return: 成功したか
        """

        result = util.DatabaseHelper.reduce_stock(self.id, qty)
        stock = self.get_stock()

        # 在庫が15以下になったらDM送信
        if 15 in range(stock, stock + qty):
            asyncio.run_coroutine_threadsafe(
                bot.send_stock(self.mc_uuid, self),
                bot.client.loop
            )

        return result

    def increase_stock(self, qty: int) -> bool:
        """
        在庫を追加します

        :return: 成功しました
        """

        return util.DatabaseHelper.increase_stock(self.id, qty)

    def add_revenues(self, buyer: str, qty: int) -> bool:
        """
        収入情報を追加します

        :param buyer: 購入者のUUID
        :param qty: 商品の数量
        :return: 成功したか
        """

        total = Decimal(str(self.price)) * Decimal(str(qty))
        return util.DatabaseHelper.add_revenues(buyer, self.id, self.price, qty, total,
                                                self.mc_uuid)

    def get_category(self) -> Union['util.Category', None]:
        """
        カテゴリーを取得します

        :return: Category型
        """
        return util.Category.by_english(self.category)

    def get_discounted_price(self) -> float:
        """
        割引した値段を取得します

        :return: 割引した値段
        """
        if self.sale_status:
            sale_per = Decimal(str(100 - self.discount_rate)) / Decimal("100")
            price = Decimal(str(self.price)) * sale_per

            self.__cached_discount_price = price
            return float(price)
        else:

            self.__cached_discount_price = Decimal(str(self.price))
            return self.price

    def get_discounted_point(self) -> int:
        """
        割引した値段のポイントを取得します

        :return: 割引した値段のポイント
        """

        if not self.__cached_discount_price:
            self.get_discounted_price()

        return util.calc_point(self.__cached_discount_price)

    def increase_sold_count(self, qty) -> bool:
        """
        購入数を追加します

        :param qty: 数量
        :return: 成功したか
        """

        return util.DatabaseHelper.increase_sold_count(self.id, qty)

    def get_seller(self) -> Union['util.User', None]:
        """
        販売者のUser型を取得します

        :return: User型
        """

        return util.User.by_mc_uuid(self.mc_uuid)

    def encode_image(self) -> str:
        """
        画像リストをJSONに変換し、パーセントエンコーディングにします

        :return: JSON
        """

        return urllib.parse.quote(json.dumps(self.image))

    def get_item_stack(self) -> 'util.ItemStack':
        """
        ItemStack型を取得します

        :return: ItemStack型
        """

        return util.ItemStack.by_item_id(self.id)

    def return_stock(self, stock: int) -> bool:
        """
        在庫をユーザーのポストに返却します

        :return: 成功したか
        """
        self.reduce_stock(stock)
        return util.DatabaseHelper.add_return_stock(self.mc_uuid, self.id, stock)

    def delete(self):
        """
        アイテムを削除(無効に)します

        :return: 成功したか
        """

        stock = self.get_stock()
        if stock > 0:
            self.return_stock(stock)

        return util.DatabaseHelper.delete_item(self.id)

    def update(self, name: str, price: float, image: list, about: list, detail: str, category: 'util.Category'):
        """
        商品の情報を更新します

        :param name: アイテム名
        :param price: 値段
        :param image: 画像
        :param about: 概要
        :param category: カテゴリー
        :return:
        """

        util.DatabaseHelper.update_item(self.id, name, float(price), json.dumps(image), json.dumps(about), detail, category.english)

    @staticmethod
    def search(query: str, category: Union['util.Category', None] = None) -> list['util.Item']:
        """
        アイテムを検索します

        :param query: 検索クエリ
        :param category: カテゴリー
        :return: 検索結果
        """

        return [Item.by_db(i) for i in util.DatabaseHelper.search_item(query, category)]

    @staticmethod
    def create(item_id: int, item_name: str, item_price: float, image_path: list[str], about: str,
               detail: str, category: 'util.Category', keyword: str, mc_uuid: str):
        """
        商品を新規作成します

        :param item_id: アイテムID
        :param item_name: 商品名
        :param item_price: 値段
        :param image_path: 画像
        :param about: 概要のJSON
        :param detail: 詳細(html)
        :param category: カテゴリー型
        :param keyword: 検索キーワードのJSON
        :param mc_uuid: MinecraftのUUID
        :return: 成功したか
        """

        return util.DatabaseHelper.create_item(
            item_id, item_name, item_price, json.dumps(image_path), about, detail, category.english, keyword, mc_uuid)

    @staticmethod
    def create_id():
        """
        アイテムIDを作成します

        :return: アイテムID
        """

        while True:
            item_id = secrets.randbelow(100000)
            item = Item.by_id(item_id)
            if not item:
                return item_id

    @staticmethod
    def create_stack(item_id: int, stack: 'util.ItemStack', stock):
        util.DatabaseHelper.add_item_stack(
            item_id, stack.display_name, stack.material, json.dumps(stack.enchantments), stack.damage,
            stack.stack_size, stock)

    @staticmethod
    def get_popular() -> list['util.Item']:
        """
        人気アイテム上位4つを取得します

        :return: Item型のリスト
        """

        r = util.DatabaseHelper.get_popular_item()
        return [Item.by_db(i) for i in r]

    @staticmethod
    def get_latest() -> list['util.Item']:
        """
        新着アイテム4つを取得します

        :return: Item型のリスト
        """

        r = util.DatabaseHelper.get_latest_item()
        return [Item.by_db(i) for i in r]

    @staticmethod
    def get_featured() -> dict[str, 'util.Item']:
        """
        特集アイテムを取得します

        :return:
        """

        r = util.DatabaseHelper.get_featured_item()
        return {i.title: [Item.by_id(j) for j in i.value] for i in r}

    @staticmethod
    def by_id(id: int) -> Union['Item', None]:
        """
        アイテムIDからアイテム型を取得します

        :param id: アイテムID
        :return: アイテム型(アイテムが見つからなければNoneを返却)
        """

        r = util.DatabaseHelper.get_item(id)

        if not r:
            return None

        return Item.by_db(r)

    @staticmethod
    def by_id_list(id_list: list[int]) -> Union[list['Item'], None]:
        """
        アイテムIDからアイテム型を取得します

        :param id_list: アイテムIDのリスト
        :return: アイテム型のリスト(アイテムが見つからなければNoneを挿入)
        """

        r = util.DatabaseHelper.get_item_by_list(id_list)

        if not r:
            return None

        return [Item.by_db(i) for i in r]

    @staticmethod
    def by_db(r: dict) -> 'Item':
        """
        データベースから返されたデータをItem型に変換します

        :param r: データベースから返されたデータ
        :return: Item型
        """
        if "sale_status" in r.keys() and r["sale_status"]:
            status = util.calc_time_percentage(r["sale_start"], r["sale_end"])
        else:
            r["sale_status"] = None
            r["discount_rate"] = None
            r["sale_start"] = None
            r["sale_end"] = None

        if not r["sale_status"]:
            sale_status = False
        else:
            if status == 0 or status == 100:
                sale_status = False
            else:
                sale_status = True
        return Item(r["sale_id"], r["item_id"], r["item_name"], r["price"],
                    json.loads(r["image"]), json.loads(r["kind"]), r["detail"], r["category"],
                    r["sold_count"], r["mc_uuid"], r["search_keyword"],
                    r["created_at"], r["updated_at"], bool(r["status"]),
                    sale_status, r["discount_rate"], r["sale_start"], r["sale_end"])
