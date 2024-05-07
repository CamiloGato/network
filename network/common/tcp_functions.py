from socket import socket as Socket


def check_connection(client: Socket) -> bool:
    try:
        client.sendall(b"")
        return True
    except Exception:
        return False


def response_connection(host: Socket) -> bool:
    try:
        return True
    except Exception:
        return False
