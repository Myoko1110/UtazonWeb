from urllib.parse import urljoin

import discord

from config import settings

client = discord.Client(intents=discord.Intents.default())
delivery_status_url = ""
order_history_url = ""


async def setup():
	global delivery_status_url
	global order_history_url
	delivery_status_url = urljoin(settings.HOST, "history/status/?id=")
	order_history_url = urljoin(settings.HOST, "history/")


@client.event
async def on_ready():
	print(f"Logged in as {client.user}")
	await setup()


async def send_order_confirm(discord_id, order_id, order_item_obj, delivery_time):
	global delivery_status_url

	author = await client.fetch_user(discord_id)
	embed = discord.Embed(
		title="ご注文が確定されました",
		color=discord.Colour.green(),
		description=f"ご購入ありがとうございます。\nお客様のご注文が確定されたことをお知らせいたします。\n配送状況は[こちら]({delivery_status_url}{order_id})から"
	)
	embed.set_footer(text="またのご利用をお待ちしております。")

	order_item = ""
	for i in order_item_obj:
		if len(i[1]) > 33:
			order_item += f"・{i[1][:33]}...\n"
		else:
			order_item += f"・{i[1]}\n"

	embed.add_field(name="注文品", value=order_item, inline=False)
	embed.add_field(name="お届け予定", value=f"{delivery_time.year}年{delivery_time.month}月{delivery_time.day}日 {delivery_time.hour}時頃", inline=False)
	embed.add_field(name="注文番号", value=order_id, inline=False)
	await author.send(embed=embed)


async def send_order_cancel(discord_id, order_id, order_item_obj):
	global order_history_url

	author = await client.fetch_user(discord_id)
	embed = discord.Embed(
		title="ご注文がキャンセルされました",
		color=discord.Colour.red(),
		description=f"お客様のご注文がキャンセルされたことをお知らせいたします。\nまた、キャンセルにつき購入額の{settings.CANCELLATION_FEE}%分のキャンセル料がかかります。\n注文履歴は[こちら]({order_history_url})"
	)
	embed.set_footer(text="またのご利用をお待ちしております。")
	order_item = ""
	for i in order_item_obj:
		if len(i[1]) > 33:
			order_item += f"・{i[1][:33]}...\n"
		else:
			order_item += f"・{i[1]}\n"

	embed.add_field(name="注文品", value=order_item, inline=False)
	embed.add_field(name="注文番号", value=order_id, inline=False)
	await author.send(embed=embed)


async def send_security(discord_id):
	author = await client.fetch_user(discord_id)
	embed = discord.Embed(
		title="新しいログイン",
		color=discord.Colour.blue(),
		description=f"あなたのアカウントへの新しいログインが検出されました。ご自身によるものであれば、何もする必要はありません。ログインに心当たりがない場合は、運営にお問い合わせください。"
	)
	await author.send(embed=embed)

