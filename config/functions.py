import datetime
import requests

from django.db.models import Max
from django.shortcuts import get_object_or_404

import config.DBManager
import config.settings as settings
from item.models import Banner


class is_session:
    """
    セッションが有効か確認

    引数:
        request: Djangoのrequestオブジェクト
    """
    def __init__(self, request):
        self.request = request
        self.valid = False
        self.expire = False
        self.invalid = False

        session = self.request.COOKIES

        # 一つずつ処理
        for child in session:
            if child.startswith("_Secure-"):

                result = config.DBManager.get_session(child, session[child])

                # EmptySetを判定
                if not result:
                    # 未ログイン処理
                    continue
                else:
                    # 有効期限の確認
                    now = datetime.datetime.now()
                    if now > result[5]:
                        config.DBManager.delete_session(child)
                        # 期限切れの処理
                        self.expire = True
                        return

                    # 既ログイン処理
                    self.valid = True
                    return
        else:
            if "LOGIN_STATUS" in session and session["LOGIN_STATUS"]:
                # 期限切れの処理
                self.expire = True

            # 未ログイン処理
            self.invalid = True


def get_categories():
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


def get_child_categories(parent_category):
    categories = settings.CATEGORIES

    child_categories = {}
    for i in categories.keys():
        if parent_category == i:
            child_categories = categories[i].copy()
            child_categories.pop("JAPANESE")
    return child_categories


def get_banners():
    pc_record = Banner.objects.filter(view_type='pc').aggregate(Max('id'))["id__max"]
    pc_img = get_object_or_404(Banner, id=pc_record)

    mobile_record = Banner.objects.filter(view_type='mobile').aggregate(Max('id'))["id__max"]
    mobile_img = get_object_or_404(Banner, id=mobile_record)

    return pc_img, mobile_img
