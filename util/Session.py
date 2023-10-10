import datetime
import secrets
from typing import Union

from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render

import util
from config import settings


class Session:
    id: str
    value: str
    mc_uuid: str
    access_token: str
    login_at: datetime
    expires_at: datetime
    logged_ip: str

    is_valid: bool = False
    is_invalid: bool = False
    is_expire: bool = False

    __cached_user: Union['util.User', None] = None

    def __init__(self, id=None, value=None, mc_uuid=None, access_token=None, login_at=None,
                 expires_at=None, logged_ip=None,
                 valid: bool = False, invalid: bool = False, expire: bool = False):
        self.id = id
        self.value = value
        self.mc_uuid = mc_uuid
        self.access_token = access_token
        self.login_at = login_at
        self.expires_at = expires_at
        self.logged_ip = logged_ip

        self.is_valid = valid
        self.is_invalid = invalid
        self.is_expire = expire

    def __bool__(self):
        return self.is_valid

    def get_user(self) -> Union['util.User', None]:
        """
        User型を取得します

        :return: User型(見つからなかった場合はNoneを返却)
        """

        if not self.__cached_user:
            self.__cached_user = util.User.by_mc_uuid(self.mc_uuid)
        return self.__cached_user

    @staticmethod
    def delete_cookie(request: WSGIRequest, template_name: str, context):
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

    @staticmethod
    def save(mc_uuid: str, access_token: str, client_addr: str) -> Union['Session', bool]:
        """
        セッションを保存します

        :param mc_uuid: MinecraftのUUID
        :param access_token: DiscordAPIのアクセストークン
        :param client_addr: ログインされたIP
        :return: User型(失敗した場合はFalseを返却)
        """

        now = datetime.datetime.now().replace(microsecond=0)
        expires = now + datetime.timedelta(days=int(settings.SESSION_EXPIRES))

        while True:
            session_id = f"_Secure-{secrets.token_urlsafe(32)}"
            session_value = f"{secrets.token_urlsafe(128)}"

            save_session = util.DatabaseHelper.save_session(
                session_id, session_value, mc_uuid, access_token, now, expires, client_addr
            )

            if save_session:
                return Session(session_id, session_value, mc_uuid, access_token, now, expires, client_addr, valid=True)
            elif save_session.errno == 1062:
                continue
        return False

    @staticmethod
    def by_request(request: WSGIRequest) -> 'util.Session':
        """
        DjangoのWSGIRequest型からSession型を返却します

        :param request: DjangoのWSGIRequest型
        :return: Session型
        """

        session = request.COOKIES

        for child in session:
            if child.startswith("_Secure-"):

                result = util.DatabaseHelper.get_session(child, session[child])

                if not result:
                    # 未ログイン処理
                    continue
                else:
                    # 有効期限の確認
                    now = datetime.datetime.now()
                    if now > result["expires_at"]:
                        util.DatabaseHelper.delete_session(child)
                        # 期限切れの処理
                        return Session(expire=True)

                    # 既ログイン処理
                    return Session(result["session_id"], result["session_val"],
                                   result["mc_uuid"], result["access_token"],
                                   result["login_at"], result["expires_at"], result["logged_IP"],
                                   valid=True)
        else:
            if "LOGIN_STATUS" in session and session["LOGIN_STATUS"]:
                # 期限切れの処理
                return Session(expire=True)

            # 未ログイン処理
            return Session(expire=True)
