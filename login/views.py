import logging

import requests
from django.shortcuts import redirect, render

import utils
from config import settings
from utils import Session, User


def login(request):
    # codeパラメーターを参照
    code = request.GET.get("code")

    # codeがあったら
    if code is not None:

        # POST内容を指定
        request_post = {
            "client_id": settings.DISCORD_CLIENT["CLIENT-ID"],
            "client_secret": settings.DISCORD_CLIENT["CLIENT-SECRET"],
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.DISCORD_CLIENT["REDIRECT"],
        }

        # access_tokenを取得
        token_request = requests.post("https://discordapp.com/api/oauth2/token", data=request_post)

        # StatusCodeが200でなかったらエラーを表示
        if token_request.status_code != 200:
            logging.error(
                f"access_tokenを取得できませんでした(Error: {token_request.json()}, Code: {code})"
            )

            # エラーを表示
            context = {
                "err": True,
                "content": "内部エラーが発生しました。もう一度お試しください。",
                "url": settings.DISCORD_CLIENT["URL"],
            }
            return render(request, "login.html", context=context)

        # access_tokenを指定
        access_token = token_request.json()["access_token"]

        # tokenからユーザーの情報を取得
        token_header = {"Authorization": f"Bearer {access_token}"}
        identify = requests.get("https://discordapp.com/api/users/@me", headers=token_header)

        # StatusCodeが200でなかったらエラーを表示
        if identify.status_code != 200:
            logging.error(
                f"access_tokenからidentifyを取得できませんでした(StatusCode: {identify.json()}, Code: {code})"
            )

            # エラーを表示
            context = {
                "err": True,
                "content": "内部エラーが発生しました。お手数ですがもう一度お試しください。",
                "url": settings.DISCORD_CLIENT["URL"],
            }
            return render(request, "login.html", context=context)

        # tokenから参加サーバーを取得
        guilds = requests.get("https://discordapp.com/api/users/@me/guilds", headers=token_header)

        # StatusCodeが200でなかったらエラーを表示
        if guilds.status_code != 200:
            logging.error(
                f"access_tokenからguildsを取得できませんでした(StatusCode: {guilds.json()}, Code: {code})"
            )

            # エラーを表示
            context = {
                "err": True,
                "content": "内部エラーが発生しました。お手数ですがもう一度お試しください。",
                "url": settings.DISCORD_CLIENT["URL"],
            }
            return render(request, "login.html", context=context)

        # Discordサーバーに参加しているかを確認
        for i in guilds.json():
            if i["id"] == str(settings.SERVER_ID):

                discord_id = identify.json()["id"]

                # DiscordConnectでリンクしてるか確認
                u = User.by_discord_id(discord_id)

                if not u:
                    # エラーを表示
                    context = {
                        "err": True,
                        "content": "DiscordとMinecraftを接続した上でログインしてください。",
                        "url": settings.DISCORD_CLIENT["URL"],
                    }
                    return render(request, "login.html", context=context)

                # クライアントのIPを取得
                forwarded_addresses = request.META.get("HTTP_X_FORWARDED_FOR")
                if forwarded_addresses:
                    # "HTTP_X_FORWARDED_FOR"ヘッダがある場合: 転送経路の先頭要素を取得する。
                    client_addr = forwarded_addresses.split(",")[0]
                else:
                    # "HTTP_X_FORWARDED_FOR"ヘッダがない場合: 直接接続なので"REMOTE_ADDR"ヘッダを参照する。
                    client_addr = request.META.get("REMOTE_ADDR")

                s = Session.save(u.mc_uuid, access_token, client_addr)

                # 問題がなかったらcookie付与しリダイレクト
                response = redirect("/")
                response.set_cookie(s.id, s.value, expires=s.expires_at)
                response.set_cookie("LOGIN_STATUS", True, max_age=315360000)
                return response

        else:
            # エラーを表示
            context = {
                "err": True,
                "content": "Discordサーバーに参加されていません。参加の上、もう一度お試しください。",
                "url": settings.DISCORD_CLIENT["URL"],
            }
            return render(request, "login.html", context=context)

    else:
        s = Session.by_request(request)
        if s.is_valid:
            # 既ログイン処理
            return redirect("/")
        else:
            # 未ログイン処理
            context = {
                "err": False,
                "content": "error",
                "url": settings.DISCORD_CLIENT["URL"],
            }
            return render(request, "login.html", context=context)


def logout(request):
    response = redirect("/")

    for key in request.COOKIES:
        if key.startswith("_Secure-"):
            response.delete_cookie(key)

            utils.DatabaseHelper.delete_session(key)

    response.delete_cookie("LOGIN_STATUS")

    # リダイレクト
    return response
