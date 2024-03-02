import asyncio
import datetime
import json
import secrets
import urllib.parse
from uuid import UUID
from decimal import Decimal, ROUND_UP
from typing import Union

import bot
import utils


class Item:
    sale_id: int
    id: int
    name: str
    price: float
    image: list
    kind: list
    detail: str
    __category: str
    sold_count: int
    mc_uuid: UUID
    search_keyword: list
    created_at: datetime.datetime
    updated_at: datetime.datetime
    status: bool
    sale: 'utils.Sale'

    __cached_discount_price: Decimal
    __cached_stock: Union[int, None]

    def __init__(
            self,
            sale_id: int,
            id: int,
            name: str,
            price: float,
            image: list,
            kind: list,
            detail: str,
            category: str,
            sold_count: int,
            mc_uuid: UUID,
            search_keyword: list,
            created_at: datetime.datetime,
            updated_at: datetime.datetime,
            status: bool,
            sale: 'utils.Sale'
    ):

        # itemテーブル関係
        self.sale_id = sale_id
        self.id = id
        self.name = name
        self.price = price
        self.image = image
        self.kind = kind
        self.detail = detail
        self.__category = category
        self.sold_count = sold_count
        self.mc_uuid = mc_uuid
        self.search_keyword = search_keyword
        self.created_at = created_at
        self.updated_at = updated_at
        self.status = status
        self.sale = sale

        self.__cached_discount_price = Decimal()
        self.__cached_stock = None
        self.__cached_review = None

    def __dict__(self):
        return {"id": self.id,
                "sale_id": self.sale_id,
                "name": self.name,
                "price": self.price,
                "image": self.image,
                "kind": self.kind,
                "detail": self.detail,
                "category": self.__category,
                "sold_count": self.sold_count,
                "mc_uuid": self.mc_uuid,
                "search_keyword": self.search_keyword,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
                "status": self.status,
                "sale": self.sale,
                }

    def __str__(self):
        return "Item" + str(self.__dict__())

    def __repr__(self):
        return (f"Item({self.sale_id.__repr__()}, {self.id.__repr__()}, {self.name.__repr__()}, {self.price.__repr__()}, {self.image.__repr__()}, "
                f"{self.kind.__repr__()}, {self.detail.__repr__()}, {self.category.__repr__()}, {self.sold_count.__repr__()}, {self.mc_uuid.__repr__()}, "
                f"{self.search_keyword.__repr__()}, {self.created_at.__repr__()}, {self.updated_at.__repr__()}, "
                f"{self.status.__repr__()}, {self.sale.__repr__()})")

    @property
    def review(self) -> Union['utils.ReviewList', None]:
        """
        レビュー型を取得します

        :return: Review型
        """
        if not self.__cached_review:
            self.__cached_review = utils.ReviewList.by_item_id(self.id)
        return self.__cached_review

    @property
    def stock(self) -> int:
        """
        在庫を取得します

        :return: 在庫
        """

        if not self.__cached_stock:
            self.__cached_stock = utils.DatabaseHelper.get_stock(self.id)[0]
        return self.__cached_stock

    def reduce_stock(self, qty: int) -> bool:
        """
        在庫を減らします

        :return: 成功したか
        """

        result = utils.DatabaseHelper.reduce_stock(self.id, qty)
        stock = self.stock

        # 在庫が15以下になったらDM送信
        if 15 in range(stock, stock + qty):
            asyncio.run_coroutine_threadsafe(
                bot.send_stock(str(self.mc_uuid), self),
                bot.client.loop
            )

        return result

    def increase_stock(self, qty: int) -> bool:
        """
        在庫を追加します

        :return: 成功しました
        """

        return utils.DatabaseHelper.increase_stock(self.id, qty)

    def add_revenues(self, buyer_uuid: UUID, qty: int) -> bool:
        """
        収入情報を追加します

        :param buyer_uuid: 購入者のUUID
        :param qty: 商品の数量
        :return: 成功したか
        """

        total = Decimal(str(self.price)) * Decimal(str(qty))
        return utils.DatabaseHelper.add_revenues(str(buyer_uuid), self.id, self.price, qty, total,
                                                 self.mc_uuid)

    @property
    def category(self) -> Union['utils.Category', None]:
        """
        カテゴリーを取得します

        :return: Category型
        """

        return utils.Category.by_english(self.__category)

    @property
    def discount_price(self) -> float:
        """
        割引した値段を取得します

        :return: 割引した値段
        """
        if self.sale.status:
            sale_per = Decimal(str(100 - self.sale.discount_rate)) / Decimal("100")
            price = (Decimal(str(self.price)) * sale_per).quantize(Decimal("0.01"), ROUND_UP)

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
            get = self.discount_price

        return utils.calc_point(self.__cached_discount_price)

    def increase_sold_count(self, qty) -> bool:
        """
        購入数を追加します

        :param qty: 数量
        :return: 成功したか
        """

        return utils.DatabaseHelper.increase_sold_count(self.id, qty)

    def get_seller(self) -> Union['utils.User', None]:
        """
        販売者のUser型を取得します

        :return: User型
        """

        return utils.User.by_mc_uuid(self.mc_uuid)

    def encode_image(self) -> str:
        """
        画像リストをJSONに変換し、パーセントエンコーディングにします

        :return: JSON
        """

        return urllib.parse.quote(json.dumps(self.image))

    def get_item_stack(self) -> 'utils.ItemStack':
        """
        ItemStack型を取得します

        :return: ItemStack型
        """

        return utils.ItemStack.by_item_id(self.id)

    def return_stock(self, stock: int) -> bool:
        """
        在庫をユーザーのポストに返却します

        :return: 成功したか
        """
        self.reduce_stock(stock)
        return utils.DatabaseHelper.add_return_stock(str(self.mc_uuid), self.id, stock)

    def delete(self):
        """
        アイテムを削除(無効に)します

        :return: 成功したか
        """

        stock = self.stock
        if stock > 0:
            self.return_stock(stock)

        return utils.DatabaseHelper.delete_item(self.id)

    def update(self, name: str, price: float, image: list, about: list, detail: str,
               category: 'utils.Category'):
        """
        商品の情報を更新します

        :param name: アイテム名
        :param price: 値段
        :param image: 画像
        :param about: 概要
        :param detail: 詳細
        :param category: カテゴリー
        :return:
        """

        utils.DatabaseHelper.update_item(self.id, name, float(price), json.dumps(image),
                                         json.dumps(about), detail, category.english)

    def set_sale(self, discount_rate: int, start_date: datetime.datetime,
                 end_date: datetime.datetime, is_pride_only: bool) -> bool:
        """
        セールを設定します

        :param discount_rate: 割引率
        :param start_date: セール開始日時
        :param end_date: セール終了日時
        :param is_pride_only: プライド限定セールか
        :return: 成功したか
        """

        print(start_date)
        print(end_date)

        return utils.DatabaseHelper.set_sale(
            self.id, discount_rate, start_date, end_date, is_pride_only
        )

    def end_sale(self) -> bool:
        """
        セールを終了します

        :return: 成功したか
        """

        return utils.DatabaseHelper.end_sale(self.id)

    def to_dict(self) -> dict:
        """
        辞書にエンコードします

        :return: 辞書
        """

        obj = {"id": self.id,
               "name": self.name,
               "price": self.price,
               "image": self.image,
               "kind": self.kind,
               "detail": self.detail,
               "category": self.category,
               "sold_count": self.sold_count,
               "mc_uuid": str(self.mc_uuid),
               "mc_id": str(self.get_seller().mc_id),
               "search_keyword": self.search_keyword,
               "created_at": str(self.created_at),
               "updated_at": str(self.updated_at),
               "status": self.status,
               "sale_status": self.sale.status,
               "discount_rate": self.sale.discount_rate,
               "discounted_price": self.discount_price,
               "sale_start": str(self.sale.start),
               "sale_end": str(self.sale.end),
               "is_prime_only": self.sale.is_pride_only,
               "stock": self.stock,
               }

        return obj

    @staticmethod
    def search(query: str, category: Union['utils.Category', None] = None) -> list['utils.Item']:
        """
        アイテムを検索します

        :param query: 検索クエリ
        :param category: カテゴリー
        :return: 検索結果
        """

        return [Item.by_db(i) for i in utils.DatabaseHelper.search_item(query, category)]

    @staticmethod
    def create(item_id: int, item_name: str, item_price: float, image_path: list[str], about: str,
               detail: str, category: 'utils.Category', keyword: str, mc_uuid: UUID):
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
        :param mc_uuid: MinecraftUUID
        :return: 成功したか
        """

        return utils.DatabaseHelper.create_item(
            item_id, item_name, item_price, json.dumps(image_path), about, detail, category.english,
            keyword, str(mc_uuid))

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
    def create_stack(item_id: int, stack: 'utils.ItemStack', stock):
        utils.DatabaseHelper.add_item_stack(
            item_id, stack.display_name, stack.material, json.dumps(stack.enchantments),
            stack.damage,
            stack.stack_size, stock)

    @staticmethod
    def get_popular() -> list['utils.Item']:
        """
        人気アイテム上位4つを取得します

        :return: Item型のリスト
        """

        r = utils.DatabaseHelper.get_popular_item()
        return [Item.by_db(i) for i in r]

    @staticmethod
    def get_latest() -> list['utils.Item']:
        """
        新着アイテム4つを取得します

        :return: Item型のリスト
        """

        r = utils.DatabaseHelper.get_latest_item()
        return [Item.by_db(i) for i in r]

    @staticmethod
    def get_featured() -> dict[str, 'utils.Item']:
        """
        特集アイテムを取得します

        :return:
        """

        r = utils.DatabaseHelper.get_featured_item()
        return {i.title: [Item.by_id(j) for j in i.value] for i in r}

    @staticmethod
    def by_id(id: int) -> Union['Item', None]:
        """
        アイテムIDからアイテム型を取得します

        :param id: アイテムID
        :return: アイテム型(アイテムが見つからなければNoneを返却)
        """

        r = utils.DatabaseHelper.get_item(id)

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

        r = utils.DatabaseHelper.get_item_by_list(id_list)

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
        return Item(r["sale_id"], r["item_id"], r["item_name"], r["price"],
                    json.loads(r["image"]), json.loads(r["kind"]), r["detail"], r["category"],
                    r["sold_count"], UUID(r["mc_uuid"]), r["search_keyword"],
                    r["created_at"], r["updated_at"], bool(r["status"]), utils.Sale(r))

    @staticmethod
    def get_active():
        """
        有効なアイテムを全て取得します

        :return: Item型のリスト
        """

        r = utils.DatabaseHelper.get_active_item()

        if not r:
            return None

        return [Item.by_db(i) for i in r]
