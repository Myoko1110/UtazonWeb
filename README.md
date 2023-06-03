# UtazonWeb
Djangoを使用した
## Get Started
1. セッション情報やユーザー情報を保存するMySQLを設定します
```shell
# データベースの作成
$ mysql -uroot -p
mysql -> CREATE DATEBASE <DatebaseName>;
mysql -> USE <DatebaseName>;

# セッション情報保存のテーブルを作成
mysql -> CREATE TABLE <SessionTableName> (session_id VARCHAR, session_val VARCHAR, user_id VARCHAR, access_token VARCHAR, login_date DATETIME, expires DATETIME);

# ユーザー情報保存のテーブルを作成
etc...
```
2. [Discord Developer Portal](https://discord.com/developers/applications)のApplicationsからCLIENT IDなどを取得します
3. 