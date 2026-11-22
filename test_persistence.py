
from storage.database import initialize_database
from storage.queue_repository import QueueRepository
from broker.broker_server import BrokerServer


def test_message_persistence():
    initialize_database()

    broker = BrokerServer()
    repository = QueueRepository()

    # Publish a test message.
    success, message = broker.publish_message(
        publisher_id="PUB-TEST",
        topic="university.announcements",
        title="Persistence Test",
        content="Testing SQLite message storage in UniSync."
    )

    if not success:
        print("Message publishing failed:", message)
        return

    # Retrieve the message from SQLite.
    saved_message = repository.get_message(
        message["message_id"]
    )

    print("\n===== PERSISTENCE TEST =====")

    if saved_message:
        print("Message successfully saved to SQLite!")
        print("Message ID:", saved_message["message_id"])
        print("Topic:", saved_message["topic"])
        print("Title:", saved_message["title"])
        print("Content:", saved_message["content"])
    else:
        print("Message was not found in the database.")

    print("============================")


if __name__ == "__main__":
    test_message_persistence()
