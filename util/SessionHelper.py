import datetime

import django
from django.shortcuts import render

import config.DBManager


class is_session:
    """
    セッションが有効か確認します

    :param request: DjangoのHttpRequestオブジェクト
    """

    def __init__(self, request: django):
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


def delete_cookie(request: django, template_name: str, context):
    """
    session関係のcookieを削除します

    :param request: DjangoのHttpRequestオブジェクト
    :param template_name: テンプレート名
    :param context: 返すコンテキスト
    :return: DjangoのResponseオブジェクト
    """

    response = render(request, template_name, context=context)

    for key in request.COOKIES:
        if key.startswith("_Secure-"):
            response.delete_cookie(key)
    response.delete_cookie("LOGIN_STATUS")

    return response
