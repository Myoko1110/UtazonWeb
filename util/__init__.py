import datetime

from django.db.models import Max
from django.shortcuts import get_object_or_404

from item.models import Banner
from . import DatabaseHelper, ItemHelper, SessionHelper, UserHelper, VaultHelper


def get_banners():
	"""
	最新のバナーを取得します

	:return: バナーのパス
	"""
	pc_record = Banner.objects.filter(view_type='pc').aggregate(Max('id'))["id__max"]
	pc_img = get_object_or_404(Banner, id=pc_record)

	mobile_record = Banner.objects.filter(view_type='mobile').aggregate(Max('id'))["id__max"]
	mobile_img = get_object_or_404(Banner, id=mobile_record)

	return pc_img, mobile_img


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
