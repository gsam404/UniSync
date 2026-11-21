import socket

from networking.socket_utils import send_msg, recv_msg
from networking.protocol import (
    REGISTER_SUBSCRIBER,
    SUBSCRIBE,
    UNSUBSCRIBE,
    STATUS,
    DISCONNECT,
    create_message,
)


HOST = "127.0.0.1"
PORT = 5000

UNIVERSITY_TOPICS = {
    "1": "university.announcements",
    "2": "university.academic",
    "3": "university.events",
    "4": "university.emergency",
    "5": "university.it",
    "6": "university.library",
}

COLLEGE_TOPICS = {
    "7": "college.ict",
    "8": "college.business",
    "9": "college.engineering",
    "10": "college.education",
    "11": "college.arts_sciences",
    "12": "college.nursing",
    "13": "college.agriculture",
}

ALL_TOPICS = {
    **UNIVERSITY_TOPICS,
    **COLLEGE_TOPICS,
}


def display_topics():
    print("\n===== UniSync Available Topics =====")

    for number, topic in ALL_TOPICS.items():
        print(f"{number}. {topic}")

    print("===============================")


def subscribe_to_topic(sock, topic):
    send_msg(
        sock,
        create_message(
            SUBSCRIBE,
            topic=topic,
        ),
    )

    response = recv_msg(sock)

    if response is None:
        print("No response from broker.")
        return

    if response.get("type") == STATUS:
        print(f"Successfully subscribed to {topic}.")
    else:
        print("Subscription failed:", response)

def unsubscribe_from_topic(sock, topic):
    send_msg(
        sock,
        create_message(
            UNSUBSCRIBE,
            topic=topic,
        ),
    )

    response = recv_msg(sock)

    if response is None:
        print("No response from broker.")
        return

    if response.get("type") == STATUS:
        print(f"Successfully unsubscribed from {topic}.")
    else:
        print("Unsubscription failed:", response)

def select_topic():
    display_topics()

    choice = input("Select a topic number: ").strip()

    topic = ALL_TOPICS.get(choice)

    if topic is None:
        print("Invalid topic selection.")
        return None

    return topic

def subscriber_menu(sock):
    while True:
        print("\n===== UniSync Subscriber Menu =====")
        print("1. Subscribe to a topic")
        print("2. Unsubscribe from a topic")
        print("3. View available topics")
        print("4. Disconnect")

        choice = input("Select an option: ").strip()

        if choice == "1":
            topic = select_topic()

            if topic:
                subscribe_to_topic(sock, topic)

        elif choice == "2":
            topic = select_topic()

            if topic:
                unsubscribe_from_topic(sock, topic)

        elif choice == "3":
            display_topics()

        elif choice == "4":
            break

        else:
            print("Invalid choice. Please try again.")

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

        subscriber_menu(sock)

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