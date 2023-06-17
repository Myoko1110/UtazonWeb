from django.shortcuts import redirect, render
import requests
import logging
import secrets
import mysql.connector
import datetime
import config.settings as settings
from config.functions import session_is_valid


def login(request):

    # codeパラメーターを参照
    code = request.GET.get('code')

    # codeがあったら
    if code is not None:

        # POST内容を指定
        request_post = {
            'client_id': settings.DISCORD_CLIENT['CLIENT-ID'],
            'client_secret': settings.DISCORD_CLIENT['CLIENT-SECRET'],
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': settings.DISCORD_CLIENT['REDIRECT'],
        }

        # access_tokenを取得
        token_request = requests.post('https://discordapp.com/api/oauth2/token', data=request_post)

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

            # エラーを表示
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
            if i['id'] == str(settings.SERVER_ID):
                # セッションを作成
                session_id = f'_Secure-{secrets.token_urlsafe(32)}'
                session_value = f'{secrets.token_urlsafe(128)}'

                session_cnx = mysql.connector.connect(**settings.DATABASE_CONFIG)

                # 現在時間と1ヶ月後を取得
                now = datetime.datetime.now().replace(microsecond=0)
                expires = now + datetime.timedelta(days=int(settings.SESSION_EXPIRES))

                discord_id = identify.json()['id']
                user_avatar = identify.json()['avatar']

                # dbにセッションを記録
                with session_cnx:
                    with session_cnx.cursor() as cursor:
                        sql = """INSERT INTO `session` (
                                 `session_id`, `session_val`, `discord_id`, `access_token`, `login_date`, `expires`
                                 ) VALUES (%s, %s, %s, %s, %s, %s)"""

                        cursor.execute(sql,
                                       (session_id, session_value, discord_id, access_token, now, expires))
                    session_cnx.commit()
                cursor.close()

                # ユーザーのアイコンを取得
                user_icon_url = f"https://cdn.discordapp.com/avatars/{discord_id}/{user_avatar}"
                user_icon = requests.get(user_icon_url).content
                file_name = settings.BASE_DIR / "assets" / "usericon" / f"{discord_id}.webp"

                # アイコンをローカルに保存
                with open(file_name, mode='wb') as f:
                    f.write(user_icon)

                # 問題がなかったらcookie付与・リダイレクト
                response = redirect('/')
                response.set_cookie(session_id, session_value, expires=expires)
                response.set_cookie("LOGIN_STATUS", True, max_age=315360000)
                return response

        else:
            # エラーを表示
            context = {'err': True, 'content': 'Discordサーバーに参加されていません。参加の上、もう一度お試しください。'}
            return render(request, 'login.html', context=context)

    else:
        if session_is_valid(request)[0]:
            # 既ログイン処理
            return redirect('/')
        elif session_is_valid(request)[1]:
            # 期限切れ処理
            context = {'err': False, 'content': 'error'}
            return render(request, 'login.html', context=context)
        else:
            # 未ログイン処理
            context = {'err': False, 'content': 'error'}
            return render(request, 'login.html', context=context)