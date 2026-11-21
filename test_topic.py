from broker.topic_manager import TopicManager

tm = TopicManager()

tm.subscribe("s1", "college.ict")
tm.subscribe("s1", "university.events")

print("Before removal:")
print(tm.get_subscriptions("s1"))

tm.remove_subscriber("s1")

print("After removal:")
print(tm.get_subscriptions("s1"))