# UtazonWeb
ウェブでアイテムを注文できるwebアプリ

## 依存関係
- [UtazonPlugin]() - Minecraftサーバーとの接続に使用します（どちらからセットアップしても問題ありません）
- [DiscordConnect]() - DiscordとMinecraftの紐づけに使用します
- [AddressManager]() - 住所を参照する際に使用します

## 使い方

1. MySQL(10.2以上)をインストールします
2. 必要なライブラリをインストールします
    ```shell
    $ pip install django
    $ pip install pykakasi
    $ pip install pyyaml
    $ pip install python-dotenv
    $ pip install discord
    $ pip install mysql-connector-python
    $ pip install apscheduler
    $ pip install requests
    ```
3. インストールしたDBにUtazon関係のデータを保存するデータベースを作成します
    ```mysql
    CREATE DATABASE データベース名;
    ```
4. `.env`を環境に合わせて編集します。DB_UTAZON_DBには先程作成したデータベース名にしてください。Socket関係の設定は[Utazonプラグイン](https://github.com/UtakataNetwork/UN_Utazon)の設定と必ず合わせて下さい。
5. 必要に応じて`settings_*.yml`を編集します
6. サーバーを起動します
    ```shell
    $ python3 manage.py runserver
    ```
7. Minecraftサーバーに[Utazonプラグイン](https://github.com/UtakataNetwork/UN_Utazon)を導入し、起動します

## 本番環境での運用
本番環境で運用する場合は、Djangoの組み込みサーバーは推奨されません。<br>
NginxやuWSGI、gunicornなどを組み合わせて運用してください。

## Adminサイトへの接続
UtazonにはAdminサイト（`/admin`）でデータベースの簡単な編集をすることができます。
使用にはユーザを作成する必要があります。
```shell
   $ python manage.py createsuperuser
```
