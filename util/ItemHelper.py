import datetime
import json
from decimal import Decimal, ROUND_UP
from statistics import mean

import config.DBManager
import util
from config import settings

point_return = Decimal(settings.POINT_RETURN)


class get_index_item:
	"""
	インデックスアイテムを取得します
	"""

	def __init__(self):
		self.popular_item = config.DBManager.get_popular_item()
		self.latest_item = config.DBManager.get_latest_item()
		special_feature = config.DBManager.get_special_feature()

		self.special_feature_list = {}
		for i in special_feature:
			item_list = i.value
			obj_list = []
			for j in item_list:
				item_obj = config.DBManager.get_item(j)
				item_obj[3] = json.loads(item_obj[3])
				obj_list.append(item_obj)
			self.special_feature_list[i.title] = obj_list


class get_sale:
	"""
	アイテムIDからアイテムのセール情報を取得します

	:param item_id: アイテムID
	:param item_price: アイテム価格
	"""

	def __init__(self, item_id, item_price):
		self.status = False
		self.discount_rate = None
		self.item_price = item_price
		self.past_price = 0

		past_price = item_price

		# セール取得
		sale_id = config.DBManager.get_id_from_item(item_id)
		item_sale = config.DBManager.get_item_sale(sale_id)

		# セールが有効だったら
		if item_sale and item_sale[2]:

			# セール開催時間を確認
			status_per = calc_time_percentage(item_sale[4], item_sale[5])
			if status_per != 0.0 and status_per != 100.0:
				discount_rate = item_sale[3]

				sale_per = Decimal(str(100 - item_sale[3])) / Decimal("100")
				item_price = Decimal(str(item_price)) * sale_per
				item_price = item_price.quantize(Decimal(".01"), rounding=ROUND_UP)

				self.status = True
				self.discount_rate = discount_rate
				self.item_price = item_price
				self.past_price = past_price


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
							self.jp = value["JAPANESE"]
							self.en = english
							self.parent = None
							return
						except TypeError:
							self.jp = value
							self.en = english
							self.parent = None
							return

					try:
						for en, jp in value.items():
							# 該当のものが見つかったら
							if en == english:
								parent_jp = categories[category]["JAPANESE"]
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

		child_categories = {}
		for i in categories.keys():
			if parent_category == i:
				child_categories = categories[i].copy()
				child_categories.pop("JAPANESE")

		return child_categories

	@staticmethod
	def all():
		"""
		全てのカテゴリーを取得します

		:return: 全てのカテゴリー
		"""

		categories = settings.CATEGORIES
		categories_key = categories.keys()
		result = {}

		for i in categories_key:
			try:
				category_jp = categories[i]["JAPANESE"]
				result[category_jp] = i
			except TypeError:
				pass

		return result


def add_review_data(review_obj):
	"""
	Webに表示するために必要なデータをレビューJsonに追加します

	:param review_obj: レビューJson
	:return: 必要な情報を追加したリスト
	"""

	item_review = json.loads(review_obj.replace("\n", "<br>"))

	for i in item_review:
		# item_reviewにmc情報を追加
		mc_uuid = i["mc_uuid"]
		mc_id = util.UserHelper.get_info.from_uuid(mc_uuid).mc_id
		i["mc_id"] = mc_id

		# item_reviewのdateをdatetimeオブジェクトに変換
		date = datetime.datetime.strptime(i["date"], "%Y-%m-%d %H:%M:%S")
		i["date"] = date

	item_review = item_review
	return item_review


def calc_time_percentage(past_time: datetime.datetime, future_time: datetime.datetime):
	"""
	past_timeとfuture_timeの間で現在の時間の進行した割合を計算します

	:param past_time: 過去の時間
	:param future_time: 未来の時間
	:return: 進行した割合
	"""

	current_time = datetime.datetime.now()

	if past_time > future_time:
		past_time, future_time = future_time, past_time

	total_duration = future_time - past_time
	elapsed_duration = current_time - past_time

	if elapsed_duration.total_seconds() < 0:
		percentage = 0.0
	elif elapsed_duration.total_seconds() > total_duration.total_seconds():
		percentage = 100.0
	else:
		percentage = (elapsed_duration.total_seconds() / total_duration.total_seconds()) * 100

	return percentage


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


def calc_point(item_price):
	"""
	アイテムの値段からポイント額を計算します

	:param item_price: アイテムID
	:return: ポイント額(int型)
	"""

	return int(Decimal(str(item_price)) * point_return)


def calc_review_average(review_obj):
	if review_obj:
		review_star_list = [i["star"] for i in review_obj]
		review_average = round(mean(review_star_list), 1)

	else:
		review_average = None

	return review_average
