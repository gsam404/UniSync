
import socket

from networking.socket_utils import send_msg, recv_msg
from networking.protocol import (
    REGISTER_SUBSCRIBER,
    STATUS,
    DISCONNECT,
    create_message,
)


HOST = "127.0.0.1"
PORT = 5000


def run_subscriber(client_id):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((HOST, PORT))

        # Register as a subscriber
        send_msg(
            sock,
            create_message(
                REGISTER_SUBSCRIBER,
                client_id=client_id,
            ),
        )

        response = recv_msg(sock)

        if response is None or response.get("type") != STATUS:
            print("Registration failed:", response)
            return

        print(f"Subscriber '{client_id}' connected to UniSync.")
        print("Type 'quit' to disconnect.")

        while True:
            command = input("> ").strip().lower()

            if command == "quit":
                break

            print("Receiving messages is not implemented yet.")

        send_msg(sock, create_message(DISCONNECT))
        print("Subscriber disconnected.")

    except (ConnectionError, OSError) as exc:
        print(f"Connection error: {exc}")

    finally:
        sock.close()


if __name__ == "__main__":
    client_id = input("Enter subscriber ID: ").strip()

    if client_id:
        run_subscriber(client_id)
