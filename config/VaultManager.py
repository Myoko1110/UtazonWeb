import socket

import config.settings as settings

socket_port = settings.SOCKET_PORT
socket_host = settings.SOCKET_HOST


def get_player_balance(uuid: str):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((socket_host, int(socket_port)))
            s.sendall(uuid.encode())

            result = s.recv(1024).decode()

            if result == "Invalid UUID":
                return False

            return float(result)
    except Exception:
        print("\033[31m" + f"Socketサーバーに接続できませんでした。Socketサーバーの設定はしましたか？")
        return False
