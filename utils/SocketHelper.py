import json
import socket
import traceback
from decimal import Decimal, ROUND_UP

from config import settings

socket_port = settings.SOCKET_PORT
socket_host = settings.SOCKET_HOST


def get_balance(uuid: str):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((socket_host, int(socket_port)))
            send_value = ["getBalance", uuid]
            s.sendall(json.dumps(send_value).encode())

            received_data = s.recv(1024).decode()

            if received_data == "Invalid UUID":
                return None

            player_balance = Decimal(received_data).quantize(Decimal(".01"), rounding=ROUND_UP)

            return player_balance

    except ConnectionRefusedError:
        traceback.print_exc()
        return None


def withdraw_player(uuid: str, amount: float, action: str, reason: str):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((socket_host, int(socket_port)))
        send_value = ["withdrawPlayer", uuid, str(amount), action, reason]
        s.sendall(json.dumps(send_value).encode())

        received_data = s.recv(1024).decode()
        if received_data == "Invalid UUID":
            return False
        elif received_data == "1":
            return True
        else:
            return False


def deposit_player(uuid: str, amount: float, action: str, reason: str):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((socket_host, int(socket_port)))
        send_value = ["depositPlayer", uuid, str(amount), action, reason]
        s.sendall(json.dumps(send_value).encode())

        received_data = s.recv(1024).decode()
        if received_data == "Invalid UUID":
            return False
        elif received_data == "1":
            return True
        else:
            return False
