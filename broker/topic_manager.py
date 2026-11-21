
import threading


# University-wide topics
UNIVERSITY_TOPICS = {
    "university.announcements",
    "university.academic",
    "university.events",
    "university.emergency",
    "university.it",
    "university.library",
}

# College-specific topics
COLLEGE_TOPICS = {
    "college.ict",
    "college.business",
    "college.engineering",
    "college.education",
    "college.arts_sciences",
    "college.nursing",
    "college.agriculture",
}

# Combine all valid topics
VALID_TOPICS = UNIVERSITY_TOPICS | COLLEGE_TOPICS


def is_valid_topic(topic):
    """
    Checks whether a topic is recognized by UniSync.
    """
    return isinstance(topic, str) and topic in VALID_TOPICS


class TopicManager:
    def __init__(self):
        self.subscriptions = {}
        self.lock = threading.Lock()


    def subscribe(self, subscriber_id, topic):
        if not is_valid_topic(topic):
            return False

        with self.lock:
            self.subscriptions.setdefault(topic, set()).add(subscriber_id)

        return True


    def unsubscribe(self, subscriber_id, topic):
        if not is_valid_topic(topic):
            return False

        with self.lock:
            subscribers = self.subscriptions.get(topic, set())
            subscribers.discard(subscriber_id)

            if not subscribers:
                self.subscriptions.pop(topic, None)

        return True


    def get_subscribers(self, topic):
        with self.lock:
            return set(self.subscriptions.get(topic, set()))


    def get_subscriptions(self, subscriber_id):
        with self.lock:
            topics = [
                topic
                for topic, subscribers in self.subscriptions.items()
                if subscriber_id in subscribers
            ]

        return sorted(topics)
