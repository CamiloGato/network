import json
import socket
import threading

from network.common.data import DataMessage


def send_message(client_socket, message):
    try:
        # Convertir el mensaje a JSON
        json_message = json.dumps(message)

        # Enviar el mensaje al servidor
        client_socket.sendall(json_message.encode('utf-8'))
        print("Mensaje enviado al servidor")
    except Exception as e:
        print(f"Error al enviar mensaje: {e}")


def receive_message(client_socket):
    try:
        # Esperar la respuesta del servidor
        response = client_socket.recv(1024)
        print("Respuesta del servidor:", response.decode('utf-8'))
    except Exception as e:
        print(f"Error al recibir respuesta: {e}")


def main():
    # Dirección y puerto del servidor
    host = input("Ingrese la dirección del servidor: ")
    port = int(input("Ingrese el puerto del servidor: "))

    try:
        # Crear un socket TCP
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Conectar al servidor
        client_socket.connect((host, port))
        print(f"Conectado al servidor en {host}:{port}")

        # Mantener el cliente abierto para enviar mensajes
        while True:
            # Leer el mensaje desde la entrada del usuario
            input_message = input("Ingrese el mensaje para enviar al servidor: ")

            # Si el mensaje es "exit", salir del bucle
            if input_message.lower() == "exit":
                break

            # Crear el mensaje a enviar al servidor
            message_data = DataMessage(
                destination_ip="localhost",
                destination_port=8889,
                message=input_message,
                path=[]
            )

            # Enviar el mensaje al servidor en un hilo
            threading.Thread(target=send_message, args=(client_socket, message_data.__dict__())).start()

            # Recibir la respuesta del servidor en un hilo
            threading.Thread(target=receive_message, args=(client_socket,)).start()

    except Exception as e:
        print(f"Error al conectar al servidor: {e}")
    finally:
        # Cerrar el socket al salir
        client_socket.close()


if __name__ == "__main__":
    main()
