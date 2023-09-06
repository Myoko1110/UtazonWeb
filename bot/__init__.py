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
    """
    注文が確定されたことをDMで送信します

    :param discord_id: DiscordID
    :param order_id: オーダーID
    :param order_item_obj: アイテムリスト
    :param delivery_time: 配達時間
    """

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
        if len(i['item_name']) > 33:
            order_item += f"・{i['item_name'][:33]}...\n"
        else:
            order_item += f"・{i['item_name']}\n"

    embed.add_field(name="注文品", value=order_item, inline=False)
    embed.add_field(name="お届け予定",
                    value=f"{delivery_time.year}年{delivery_time.month}月{delivery_time.day}日 {delivery_time.hour}時頃",
                    inline=False)
    embed.add_field(name="注文番号", value=order_id, inline=False)
    await author.send(embed=embed)


async def send_order_cancel(discord_id, order_id, order_item_obj):
    """
    オーダーがキャンセルされたことをDMに送信します

    :param discord_id: DiscordID
    :param order_id: オーダーID
    :param order_item_obj: アイテムリスト
    """

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
        if len(i['item_name']) > 33:
            order_item += f"・{i['item_name'][:33]}...\n"
        else:
            order_item += f"・{i['item_name']}\n"

    embed.add_field(name="注文品", value=order_item, inline=False)
    embed.add_field(name="注文番号", value=order_id, inline=False)
    await author.send(embed=embed)


async def send_mailbox_full(discord_id, order_id):
    """
    ポストにアイテムが入れられないことをDMに送信します

    :param discord_id: DiscordID
    :param order_id: オーダーID
    """

    author = await client.fetch_user(discord_id)
    embed = discord.Embed(
        title="商品の配達ができませんでした",
        color=discord.Colour.yellow(),
        description=f"お客様のポストに商品を入れるスペースがなかったため、配達ができませんでした。ポストの整理をしていただいた上、[こちら]({order_history_url}#{order_id})から再配達をお願いします。"
    )
    embed.set_footer(text="またのご利用をお待ちしております。")

    embed.add_field(name="注文番号", value=order_id, inline=False)
    await author.send(embed=embed)


async def send_mailbox_notfound(discord_id, order_id):
    """
    ポストにアイテムが入れられないことをDMに送信します

    :param discord_id: DiscordID
    :param order_id: オーダーID
    """

    author = await client.fetch_user(discord_id)
    embed = discord.Embed(
        title="商品の配達ができませんでした",
        color=discord.Colour.yellow(),
        description=f"お客様のポストが見つかりませんでした。家にポストが設置されているか、または登録した座標にポストがあるかをご確認の上、[こちら]({order_history_url}#{order_id})から再配達をお願いします。"
    )
    embed.set_footer(text="またのご利用をお待ちしております。")

    embed.add_field(name="注文番号", value=order_id, inline=False)
    await author.send(embed=embed)


async def send_complete_order(discord_id, order_id):
    """
    ポストにアイテムが入れられないことをDMに送信します

    :param discord_id: DiscordID
    :param order_id: オーダーID
    """

    global order_history_url
    print(order_history_url)

    author = await client.fetch_user(discord_id)
    embed = discord.Embed(
        title="商品が配達が完了しました",
        color=0x5fbcd3,
        description=f"お客様の注文の商品が配達されましたことをお知らせいたします。返品はできませんので予めご了承ください。詳細は[こちら]({order_history_url}#{order_id})"
    )
    embed.set_footer(text="またのご利用をお待ちしております。")

    embed.add_field(name="注文番号", value=order_id, inline=False)
    await author.send(embed=embed)


async def send_redelivery(discord_id, order_id):
    """
    再発送を承ったことをDMに送信します。

    :param discord_id: DiscordID
    :param order_id: オーダーID
    """

    global order_history_url

    author = await client.fetch_user(discord_id)
    embed = discord.Embed(
        title="注文の再配達を承りました",
        color=discord.Colour.green(),
        description=f"お客様の注文の再配達を承りましたことをお知らせいたします。\n詳細は[こちら]({order_history_url}#{order_id})"
    )
    embed.set_footer(text="またのご利用をお待ちしております。")

    embed.add_field(name="注文番号", value=order_id, inline=False)
    await author.send(embed=embed)


async def send_security(discord_id):
    """
    新しいログインをDMで送信します

    :param discord_id: DiscordID
    """

    author = await client.fetch_user(discord_id)
    embed = discord.Embed(
        title="新しいログイン",
        color=discord.Colour.blue(),
        description="あなたのアカウントへの新しいログインが検出されました。ご自身によるものであれば、何もする必要はありません。ログインに心当たりがない場合は、運営にお問い合わせください。"
    )
    await author.send(embed=embed)
