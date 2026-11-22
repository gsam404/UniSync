import sqlite3

connection = sqlite3.connect("storage/unisync.db")

# Remove queued deliveries belonging to test subscribers.
connection.execute(
    "DELETE FROM pending_deliveries WHERE subscriber_id IN (?, ?)",
    ("STU-001", "STU-003")
)

# Remove their saved test subscriptions.
connection.execute(
    "DELETE FROM subscriptions WHERE subscriber_id IN (?, ?)",
    ("STU-001", "STU-003")
)

connection.commit()

print("Test pending deliveries and subscriptions cleaned.")

connection.close()