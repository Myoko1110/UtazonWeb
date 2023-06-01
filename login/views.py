from django.views.generic import TemplateView
from django.shortcuts import redirect, render
import requests
import logging
import secrets
import mysql.connector
import datetime


def Login(request):
    # codeパラメーターを参照
    code = request.GET.get('code')
    if code is not None:

        # POST内容を指定
        request_postdata = {
            'client_id': '1112974860956745798',
            'client_secret': 'S-ZSUdeUKJWSiCD2zybhz1VcZe5m3Ihl',
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': 'http://localhost:8000/login/',
        }

        # access_tokenを取得
        token_request = requests.post('https://discordapp.com/api/oauth2/token', data=request_postdata)

        # StatusCodeが200でなかったらエラーを表示
        if token_request.status_code != 200:
            logging.error(f'access_tokenを取得できませんでした(StatusCode: {token_request.status_code}, Code: {code})')

            # エラーを表示
            context = {'err': True, 'content': '内部エラーが発生しました。もう一度お試しください。'}
            return render(request, 'login.html', context=context)

        # access_tokenを指定
        access_token = token_request.json()['access_token']

        # tokenからユーザーの情報を取得
        token_header = {'Authorization': f'Bearer {access_token}'}
        identify = requests.get('https://discordapp.com/api/users/@me', headers=token_header)

        # StatusCodeが200でなかったらエラーを表示
        if identify.status_code != 200:
            logging.error(f'access_tokenからidentifyを取得できませんでした(StatusCode: {identify.status_code}, Code: {code}, AccessToken: {access_token})')

            # エラーをhtmlに表示
            context = {'err': True, 'content': '内部エラーが発生しました。お手数ですがもう一度お試しください。'}
            return render(request, 'login.html', context=context)

        # tokenから参加サーバーを取得
        guilds = requests.get('https://discordapp.com/api/users/@me/guilds', headers=token_header)

        # StatusCodeが200でなかったらエラーを表示
        if guilds.status_code != 200:
            logging.error(f'access_tokenからguildsを取得できませんでした(StatusCode: {guilds.status_code}, Code: {code}, AccessToken: {access_token})')

            # エラーを表示
            context = {'err': True, 'content': '内部エラーが発生しました。お手数ですがもう一度お試しください。'}
            return render(request, 'login.html', context=context)

        # Discordサーバーに参加しているかを確認
        for i in guilds.json():
            if i['id'] == '1110194264324972615':
                # セッションを作成
                session_id = f"l__{secrets.token_urlsafe(128)}"
                session_value = f"{secrets.token_urlsafe(128)}"

                config = {
                    'user': 'root',
                    'password': 'myon1614',
                    'host': 'localhost',
                    'database': 'sessions',
                }

                connection = mysql.connector.connect(**config)

                # 現在時間と1ヶ月後を取得
                now = datetime.datetime.now().replace(microsecond=0)
                expires = now + datetime.timedelta(days=30)

                # dbにセッションを記録
                with connection:
                    with connection.cursor() as cursor:
                        sql = """INSERT INTO `session` (
                                 `session_id`, `session_val`, `user_id`, `access_token`, `login_data`, `expires`
                                 ) VALUES (%s, %s, %s, %s, %s, %s)"""

                        cursor.execute(sql,
                                       (session_id, session_value, identify.json()['id'], access_token, now, expires))
                    connection.commit()
                cursor.close()

                # 問題がなかったらcookie付与・リダイレクト
                response = redirect('/')
                response.set_cookie(session_id, session_value)
                return response

        else:
            # エラーを表示
            context = {'err': True, 'content': 'Discordサーバーに参加されていません。参加の上、もう一度お試しください。'}
            return render(request, 'login.html', context=context)

    else:
        context = {'err': False, 'content': 'error'}
        return render(request, 'login.html', context=context)
