
import socket
import sys
from pathlib import Path

# Allow importing networking modules from the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from networking.socket_utils import recv_msg, send_msg


HOST = "127.0.0.1"
PORT = 5000


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)

        print(f"UniSync test server listening on {HOST}:{PORT}")
        print("Waiting for a client...")

        client_socket, client_address = server_socket.accept()

        print(f"Connected to: {client_address}")

        with client_socket:
            while True:
                try:
                    message = recv_msg(client_socket)

                    if message is None:
                        print("Client disconnected cleanly.")
                        break

                    print(f"Received: {message}")

                    message["server_reply"] = "Message received"

                    send_msg(client_socket, message)

                    print(f"Echoed: {message}")

                except (ConnectionError, ConnectionResetError, OSError, ValueError) as error:
                    print(f"Client connection ended: {error}")
                    break

    except OSError as error:
        print(f"Server error: {error}")

    finally:
        server_socket.close()
        print("Server socket closed.")


if __name__ == "__main__":
    start_server()
