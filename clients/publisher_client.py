import socket

from networking.socket_utils import send_msg, recv_msg
from networking.protocol import (
    REGISTER_PUBLISHER,
    PUBLISH,
    STATUS,
    ERROR,
    DISCONNECT,
    create_message,
)

from broker.topic_manager import UNIVERSITY_TOPICS, COLLEGE_TOPICS


HOST = "127.0.0.1"
PORT = 5000


def choose_topic():
    topics = sorted(UNIVERSITY_TOPICS | COLLEGE_TOPICS)

    print("\nAvailable Topics:")

    for index, topic in enumerate(topics, start=1):
        print(f"{index}. {topic}")

    print("0. Cancel")

    choice = input("Choose a topic number: ").strip()

    if choice == "0":
        return None

    if not choice.isdigit():
        print("Invalid choice.")
        return None

    choice = int(choice)

    if choice < 1 or choice > len(topics):
        print("Invalid choice.")
        return None

    return topics[choice - 1]


def compose_message():
    print("\nCompose Announcement")

    title = input("Announcement title: ").strip()
    content = input("Announcement content: ").strip()

    if not title:
        print("Title cannot be empty.")
        return None

    if not content:
        print("Content cannot be empty.")
        return None

    return {
        "title": title,
        "content": content,
    }


def create_announcement():
    topic = choose_topic()

    if topic is None:
        return None

    message = compose_message()

    if message is None:
        return None

    announcement = {
        "topic": topic,
        "title": message["title"],
        "content": message["content"],
    }

    return announcement


def send_announcement(sock, announcement):
    request = create_message(
        PUBLISH,
        topic=announcement["topic"],
        title=announcement["title"],
        content=announcement["content"],
    )

    send_msg(sock, request)

    response = recv_msg(sock)

    if response is None:
        print("No response received from broker.")
        return False

    if response.get("type") == ERROR:
        print("Publishing failed:", response.get("reason"))
        return False

    if (
        response.get("type") == STATUS
        and response.get("status") == "ACCEPTED"
    ):
        print("\nAnnouncement published successfully!")
        print("Message ID:", response.get("message_id"))
        return True

    print("Unexpected broker response:", response)
    return False


def run_publisher(client_id):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((HOST, PORT))

        # Register as a publisher.
        send_msg(
            sock,
            create_message(
                REGISTER_PUBLISHER,
                client_id=client_id,
            ),
        )

        response = recv_msg(sock)

        if (
            response is None
            or response.get("type") != STATUS
            or response.get("status") != "OK"
        ):
            print("Registration failed:", response)
            return

        print(f"Publisher '{client_id}' connected to UniSync.")

        print("\nCommands:")
        print("  publish - Create and send an announcement")
        print("  quit    - Disconnect from UniSync")

        while True:
            command = input("\n> ").strip().lower()

            if command == "quit":
                break

            elif command == "publish":
                announcement = create_announcement()

                if announcement is None:
                    print("Announcement creation cancelled.")
                    continue

                send_announcement(sock, announcement)

            else:
                print("Unknown command. Type 'publish' or 'quit'.")

        # Disconnect from the broker.
        send_msg(
            sock,
            create_message(DISCONNECT),
        )

        print("Publisher disconnected.")

    except (ConnectionError, OSError) as exc:
        print(f"Connection error: {exc}")

    finally:
        sock.close()


if __name__ == "__main__":
    client_id = input("Enter publisher ID: ").strip()

    if client_id:
        run_publisher(client_id)