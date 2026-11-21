
import socket
import sys
from pathlib import Path

# Allow importing networking modules from the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from networking.socket_utils import send_msg, recv_msg


HOST = "127.0.0.1"
PORT = 5000


def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((HOST, PORT))
        print(f"Connected to UniSync server at {HOST}:{PORT}")

        messages = [
            {
                "type": "PING",
                "sender": "ICT Student",
                "message": "Hello, UniSync!"
            },
            {
                "type": "PING",
                "sender": "Business Student",
                "message": "Testing message number 2"
            },
            {
                "type": "PING",
                "sender": "Engineering Student",
                "message": "Testing message number 3"
            },
            {
                "type": "PING",
                "sender": "Large Payload Test",
                "message": "x" * 100_000
            }
        ]

        # Send all messages before waiting for the replies.
        for message in messages:
            send_msg(client_socket, message)
            print(f"Sent: {message['sender']}")

        print("\nWaiting for server replies...\n")

        for i in range(len(messages)):
            response = recv_msg(client_socket)

            if response is None:
                print("Server disconnected before all replies arrived.")
                break

            print(f"Reply {i + 1} received.")

            if response.get("sender") == "Large Payload Test":
                print(f"Large payload length: {len(response['message'])}")

            else:
                print(f"Response: {response}")

    except (ConnectionError, ConnectionResetError, OSError, ValueError) as error:
        print(f"Client error: {error}")

    finally:
        client_socket.close()
        print("\nClient socket closed.")


if __name__ == "__main__":
    start_client()
