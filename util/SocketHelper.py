import json
import socket
from decimal import Decimal, ROUND_UP

from config import settings

socket_port = settings.SOCKET_PORT
socket_host = settings.SOCKET_HOST


def get_balance(uuid: str):
    """
    ユーザーの残高を取得します

    :param uuid: プレイヤーのUUID
    :return: プレイヤーの残高
    """

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((socket_host, int(socket_port)))
            send_value = ["getBalance", uuid]
            s.sendall(json.dumps(send_value).encode())

            received_data = s.recv(1024).decode()

            if received_data == "Invalid UUID":
                return False

            player_balance = Decimal(received_data).quantize(Decimal(".01"), rounding=ROUND_UP)

            return player_balance

    except ConnectionRefusedError:
        return False


def withdraw_player(uuid: str, amount: float, action: str, reason: str):
    """
    ユーザーの口座からお金を出金します

    :param uuid: 出金元のプレイヤーのUUID
    :param amount: 出金する金額
    :param action: 簡単な理由
    :param reason: 出金する理由
    :return: お金が出金されたか(キャンセルされた場合や接続失敗した場合はFalseを返却)
    """

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((socket_host, int(socket_port)))
            send_value = ["withdrawPlayer", uuid, str(amount), action, reason]
            s.sendall(json.dumps(send_value).encode())

            received_data = s.recv(1024).decode()
            if received_data == "Invalid UUID":
                return False
            elif received_data == "Success":
                return True
            else:
                return False

    except ConnectionRefusedError:
        return False


def deposit_player(uuid: str, amount: float, action: str, reason: str):
    """
    ユーザーの口座にお金を入金します

    :param uuid: 入金先のプレイヤーのUUID
    :param amount: 入金する金額
    :param action: 簡単な理由
    :param reason: 入金する理由
    :return: お金が入金されたか(キャンセルされた場合または接続失敗した場合はFalseを返却)
    """

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((socket_host, int(socket_port)))
            send_value = ["depositPlayer", uuid, str(amount), action, reason]
            s.sendall(json.dumps(send_value).encode())

            received_data = s.recv(1024).decode()
            if received_data == "Invalid UUID":
                return False
            elif received_data == "Success":
                return True
            else:
                return False

    except ConnectionRefusedError:
        return False
