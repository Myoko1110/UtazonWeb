import socket
import json

import config.settings as settings

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
                return False

            return float(received_data)
    except Exception:
        print("\033[31m" + f"Socketサーバーに接続できませんでした。Socketサーバーの設定はしましたか？")
        return False


def withdraw_player(uuid: str, amount: float, reason: str):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((socket_host, int(socket_port)))
            send_value = ["withdrawPlayer", uuid, str(amount), reason]
            s.sendall(json.dumps(send_value).encode())

            received_data = s.recv(1024).decode()
            if received_data == "Invalid UUID":
                return False
            elif received_data == "Success":
                return True
            else:
                return False

    except Exception:
        print("\033[31m" + f"Socketサーバーに接続できませんでした。Socketサーバーの設定はしましたか？")
        return False


def deposit_player(uuid: str, amount: float, reason: str):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((socket_host, int(socket_port)))
            send_value = ["depositPlayer", uuid, str(amount), reason]
            s.sendall(json.dumps(send_value).encode())

            received_data = s.recv(1024).decode()
            if received_data == "Invalid UUID":
                return False
            elif received_data == "Success":
                return True
            else:
                return False

    except Exception:
        print("\033[31m" + f"Socketサーバーに接続できませんでした。Socketサーバーの設定はしましたか？")
        return False
