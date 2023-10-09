from urllib.parse import urljoin

import discord

from config import settings

client = discord.Client(intents=discord.Intents.default())
delivery_status_url = ""
order_history_url = ""
add_stock_url = ""


async def setup():
    global delivery_status_url
    global order_history_url
    global add_stock_url
    delivery_status_url = urljoin(settings.HOST, "history/status/?id=")
    order_history_url = urljoin(settings.HOST, "history/")
    add_stock_url = urljoin(settings.HOST, "mypage/on_sale/stock/?id=")


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    await setup()


async def send_order_confirm(discord_id, order_id, item, delivers_at):
    """
    注文が確定されたことをDMで送信します

    :param discord_id: DiscordID
    :param order_id: オーダーID
    :param item: アイテムリスト
    :param delivers_at: 配達時間
    """

    global delivery_status_url

    author = await client.fetch_user(discord_id)
    embed = discord.Embed(
        title="ご注文が確定されました",
        color=discord.Colour.green(),
        description="ご購入ありがとうございます。\nお客様のご注文が確定されたことをお知らせいたします。"
                    + f"配送状況は[こちら]({delivery_status_url}{order_id})からご確認ください。"
    )
    embed.set_footer(text="またのご利用をお待ちしております。")

    order_item = ""
    for i in item.keys():
        if len(i.name) > 33:
            order_item += f"・{i.name[:33]}...\n"
        else:
            order_item += f"・{i.name}\n"

    embed.add_field(name="注文品", value=order_item, inline=False)
    embed.add_field(name="お届け予定",
                    value=f"{delivers_at.year}年{delivers_at.month}月{delivers_at.day}日"
                          + f" {delivers_at.hour}時頃",
                    inline=False)
    embed.add_field(name="注文番号", value=order_id, inline=False)
    await author.send(embed=embed)


async def send_order_cancel(discord_id, order_id, item):
    """
    オーダーがキャンセルされたことをDMに送信します

    :param discord_id: DiscordID
    :param order_id: オーダーID
    :param item: アイテムリスト
    """

    global order_history_url

    author = await client.fetch_user(discord_id)
    embed = discord.Embed(
        title="ご注文がキャンセルされました",
        color=discord.Colour.red(),
        description="お客様のご注文がキャンセルされたことをお知らせいたします。"
                    + f"また、キャンセルにつき購入額の{settings.CANCELLATION_FEE}%分のキャンセル料がかかります。"
                    + f"注文履歴は[こちら]({order_history_url})からご確認ください。"
    )
    embed.set_footer(text="またのご利用をお待ちしております。")
    order_item = ""
    for i in item:
        if len(i.name) > 33:
            order_item += f"・{i.name[:33]}...\n"
        else:
            order_item += f"・{i.name}\n"

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
        description=f"お客様のポストに商品を入れるスペースがなかったため、配達ができませんでした。"
                    + f"ポストの整理をしていただいた上、[こちら]({order_history_url}#{order_id})から再配達をお願いします。"
    )
    embed.set_footer(text="またのご利用をお待ちしております。")

    embed.add_field(name="注文番号", value=order_id, inline=False)
    await author.send(embed=embed)


async def send_mailbox_notfound(discord_id, order_id):
    """
    ポストにアイテムが見つからないことをDMに送信します

    :param discord_id: DiscordID
    :param order_id: オーダーID
    """

    author = await client.fetch_user(discord_id)
    embed = discord.Embed(
        title="商品の配達ができませんでした",
        color=discord.Colour.yellow(),
        description="お客様のポストが見つかりませんでした。家にポストが設置されているか、"
                    + f"または登録した座標にポストがあるかをご確認の上、[こちら]({order_history_url}#{order_id})から再配達をお願いします。"
    )
    embed.set_footer(text="またのご利用をお待ちしております。")

    embed.add_field(name="注文番号", value=order_id, inline=False)
    await author.send(embed=embed)


async def send_complete_order(discord_id, order_id):
    """
    配達が完了したことをDMに送信します

    :param discord_id: DiscordID
    :param order_id: オーダーID
    """

    global order_history_url

    author = await client.fetch_user(discord_id)
    embed = discord.Embed(
        title="商品が配達が完了しました",
        color=discord.Colour.blue(),
        description="お客様の注文の商品が配達されましたことをお知らせいたします。"
                    + f"返品はできませんので予めご了承ください。詳細は[こちら]({order_history_url}#{order_id})からご確認ください。"
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
        description=f"お客様の注文の再配達を承りましたことをお知らせいたします。詳細は[こちら]({order_history_url}#{order_id})からご確認ください。"
    )
    embed.set_footer(text="またのご利用をお待ちしております。")

    embed.add_field(name="注文番号", value=order_id, inline=False)
    await author.send(embed=embed)


async def send_stock(discord_id, item):
    """
    アイテムの在庫が少なくなったことをお知らせします

    :param discord_id: DiscordID
    :param item: アイテム
    """

    global order_history_url

    author = await client.fetch_user(discord_id)
    embed = discord.Embed(
        title="出品中の商品の在庫が少なくなっています",
        color=discord.Colour.orange(),
        description="お客様が販売中の商品の在庫の残りが15個以下になりましたことをお知らせいたします。"
                    + f"つきましては、[こちら]({add_stock_url}{item.id})より在庫の追加をお願いいたします。"
    )
    embed.add_field(name="該当の商品", value=item.name[:34], inline=False)
    embed.set_footer(text="またのご利用をお待ちしております。")
    await author.send(embed=embed)


async def send_returnstock_item_notfound(discord_id):
    """
    商品が無効であることをDMに送信します

    :param discord_id: DiscordID
    """

    author = await client.fetch_user(discord_id)
    embed = discord.Embed(
        title="在庫返却の配達ができませんでした",
        color=discord.Colour.red(),
        description="お客様の在庫返却の商品が無効だったため在庫返却がキャンセルされましたことをお知らせします。"
    )
    embed.set_footer(text="またのご利用をお待ちしております。")
    await author.send(embed=embed)


async def send_returnstock_mailbox_full(discord_id):
    """
    ポストにアイテムが入れられないことをDMに送信します

    :param discord_id: DiscordID
    """

    author = await client.fetch_user(discord_id)
    embed = discord.Embed(
        title="在庫返却の配達ができませんでした",
        color=discord.Colour.yellow(),
        description="お客様のポストに商品を入れるスペースがなかったため、配達ができませんでした。"
                    + "つきましては、ポストの整理をしていただくようお願いします。１時間後に配達が再実行されます。"
    )
    embed.set_footer(text="またのご利用をお待ちしております。")
    await author.send(embed=embed)


async def send_returnstock_mailbox_notfound(discord_id):
    """
    ポストにアイテムが見つからないことをDMに送信します

    :param discord_id: DiscordID
    """

    author = await client.fetch_user(discord_id)
    embed = discord.Embed(
        title="在庫返却の配達ができませんでした",
        color=discord.Colour.yellow(),
        description="お客様のポストが見つかりませんでした。家にポストが設置されているか、"
                    + "または登録した座標にポストがあるかをご確認していただくようお願いします。１時間後に配達が再実行されます。"
    )
    embed.set_footer(text="またのご利用をお待ちしております。")

    await author.send(embed=embed)


async def send_complete_returnstock(discord_id):
    """
    配達が完了したことをDMに送信します

    :param discord_id: DiscordID
    """

    global order_history_url

    author = await client.fetch_user(discord_id)
    embed = discord.Embed(
        title="在庫返却の配達が完了しました",
        color=discord.Colour.blue(),
        description="お客様の商品の在庫返却の配達が完了しましたことをお知らせいたします。"
    )
    embed.set_footer(text="またのご利用をお待ちしております。")

    await author.send(embed=embed)


async def send_returnstock_confirm(discord_id):
    """
    在庫返却を承ったことをDMに送信します

    :param discord_id: DiscordID
    """

    global order_history_url

    author = await client.fetch_user(discord_id)
    embed = discord.Embed(
        title="在庫返却を承りました",
        color=discord.Colour.blue(),
        description="お客様の商品の在庫返却を承りましたをお知らせいたします。"
    )
    embed.set_footer(text="またのご利用をお待ちしております。")

    await author.send(embed=embed)


async def send_security(discord_id):
    """
    新しいログインをDMで送信します

    :param discord_id: DiscordID
    """

    author = await client.fetch_user(discord_id)
    embed = discord.Embed(
        title="新しいログイン",
        color=0x5fbcd3,
        description="あなたのアカウントへの新しいログインが検出されました。ご自身によるものであれば、何もする必要はありません。ログインに心当たりがない場合は、運営にお問い合わせください。"
    )
    await author.send(embed=embed)
