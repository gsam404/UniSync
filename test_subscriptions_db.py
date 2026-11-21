
from storage.database import initialize_database
from storage.queue_repository import QueueRepository

initialize_database()

repository = QueueRepository()

repository.save_subscription(
    "SUB-TEST",
    "university.announcements"
)

print("Saved subscriptions:")
print(repository.get_subscriptions("SUB-TEST"))

print("\nSubscribers of university.announcements:")
print(repository.get_subscribers_by_topic(
    "university.announcements"
))
