import asyncio
import datetime
import logging
import secrets

from django.shortcuts import redirect, render
import requests

import util
import config.settings as settings
import config.DBManager
import config.functions


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
            logging.error(f"access_tokenを取得できませんでした(StatusCode: {token_request.status_code}, Code: {code})")

            # エラーを表示
            context = {
                "err": True,
                "content": "内部エラーが発生しました。もう一度お試しください。",
                "url": config.settings.DISCORD_CLIENT["URL"],
            }
            return render(request, "login.html", context=context)

        # access_tokenを指定
        access_token = token_request.json()["access_token"]

        # tokenからユーザーの情報を取得
        token_header = {"Authorization": f"Bearer {access_token}"}
        identify = requests.get("https://discordapp.com/api/users/@me", headers=token_header)

        # StatusCodeが200でなかったらエラーを表示
        if identify.status_code != 200:
            logging.error(f"access_tokenからidentifyを取得できませんでした(StatusCode: {identify.status_code}, Code: {code}, AccessToken: {access_token})")

            # エラーを表示
            context = {
                "err": True,
                "content": "内部エラーが発生しました。お手数ですがもう一度お試しください。",
                "url": config.settings.DISCORD_CLIENT["URL"],
            }
            return render(request, "login.html", context=context)

        # tokenから参加サーバーを取得
        guilds = requests.get("https://discordapp.com/api/users/@me/guilds", headers=token_header)

        # StatusCodeが200でなかったらエラーを表示
        if guilds.status_code != 200:
            logging.error(f"access_tokenからguildsを取得できませんでした(StatusCode: {guilds.status_code}, Code: {code}, AccessToken: {access_token})")

            # エラーを表示
            context = {
                "err": True,
                "content": "内部エラーが発生しました。お手数ですがもう一度お試しください。",
                "url": config.settings.DISCORD_CLIENT["URL"],
            }
            return render(request, "login.html", context=context)

        # Discordサーバーに参加しているかを確認
        for i in guilds.json():
            if i["id"] == str(settings.SERVER_ID):

                discord_id = identify.json()["id"]

                # DiscordConnectでリンクしてるか確認
                mc_uuid = config.DBManager.get_mc_uuid(discord_id)

                if not mc_uuid:
                    # エラーを表示
                    context = {
                        "err": True,
                        "content": "DiscordとMinecraftを接続した上でログインしてください。",
                        "url": config.settings.DISCORD_CLIENT["URL"],
                    }
                    return render(request, "login.html", context=context)

                # セッションを作成
                session_id = f"_Secure-{secrets.token_urlsafe(32)}"
                session_value = f"{secrets.token_urlsafe(128)}"

                # 現在時間と1ヶ月後を取得
                now = datetime.datetime.now().replace(microsecond=0)
                expires = now + datetime.timedelta(days=int(settings.SESSION_EXPIRES))

                # クライアントのIPを取得
                forwarded_addresses = request.META.get("HTTP_X_FORWARDED_FOR")
                if forwarded_addresses:
                    # "HTTP_X_FORWARDED_FOR"ヘッダがある場合: 転送経路の先頭要素を取得する。
                    client_addr = forwarded_addresses.split(",")[0]
                else:
                    # "HTTP_X_FORWARDED_FOR"ヘッダがない場合: 直接接続なので"REMOTE_ADDR"ヘッダを参照する。
                    client_addr = request.META.get("REMOTE_ADDR")
                """
                sessions = config.DBManager.get_session_from_mc_uuid(mc_uuid)
                print(sessions)
                print(mc_uuid)
                if sessions:
                    for i in sessions:
                        print(i)
                        if i == client_addr:
                            break
                    else:
                        asyncio.run_coroutine_threadsafe(bot.send_security(discord_id), bot.client.loop)
                else:
                    asyncio.run_coroutine_threadsafe(bot.send_security(discord_id), bot.client.loop)
                """
                while True:
                    save_session = config.DBManager.save_session(session_id, session_value, mc_uuid, access_token, now, expires, client_addr)

                    if save_session is True:
                        break
                    elif save_session.errno == 1062:
                        continue

                # userテーブルになかったら作成
                config.DBManager.create_user_info(mc_uuid)

                # 問題がなかったらcookie付与しリダイレクト
                response = redirect("/")
                response.set_cookie(session_id, session_value, expires=expires)
                response.set_cookie("LOGIN_STATUS", True, max_age=315360000)
                return response

        else:
            # エラーを表示
            context = {
                "err": True,
                "content": "Discordサーバーに参加されていません。参加の上、もう一度お試しください。",
                "url": config.settings.DISCORD_CLIENT["URL"],
            }
            return render(request, "login.html", context=context)

    else:
        is_session = util.SessionHelper.is_session(request)
        if is_session.valid:
            # 既ログイン処理
            return redirect("/")
        else:
            # 未ログイン処理
            context = {
                "err": False,
                "content": "error",
                "url": config.settings.DISCORD_CLIENT["URL"],
            }
            return render(request, "login.html", context=context)


def logout(request):
    response = redirect("/")

    for key in request.COOKIES:
        if key.startswith("_Secure-"):
            response.delete_cookie(key)

            config.DBManager.delete_session(key)

    response.delete_cookie("LOGIN_STATUS")

    # リダイレクト
    return response
