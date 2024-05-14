import socket


def check_connection(client: socket.socket) -> bool:
    try:
        client.sendall(b"")
        return True
    except Exception:
        return False


def response_connection(host: socket.socket) -> bool:
    try:
        return True
    except Exception:
        return False
