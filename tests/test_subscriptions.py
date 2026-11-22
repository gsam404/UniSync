
import unittest

from broker.topic_manager import TopicManager


class TopicManagerTests(unittest.TestCase):

    def setUp(self):
        self.tm = TopicManager()

    def test_subscribe_valid_topic(self):
        result = self.tm.subscribe("SUB-001", "college.ict")

        self.assertTrue(result)
        self.assertIn("SUB-001", self.tm.get_subscribers("college.ict"))

    def test_duplicate_subscription(self):
        self.tm.subscribe("SUB-001", "college.ict")
        self.tm.subscribe("SUB-001", "college.ict")

        subscribers = self.tm.get_subscribers("college.ict")

        self.assertEqual(len(subscribers), 1)

    def test_subscribe_invalid_topic(self):
        result = self.tm.subscribe("SUB-001", "college.invalid")

        self.assertFalse(result)
        self.assertEqual(self.tm.subscriptions, {})

    def test_unsubscribe_existing_subscriber(self):
        self.tm.subscribe("SUB-001", "college.ict")
        self.tm.subscribe("SUB-002", "college.ict")

        result = self.tm.unsubscribe("SUB-001", "college.ict")

        self.assertTrue(result)
        self.assertEqual(self.tm.get_subscribers("college.ict"), {"SUB-002"})

    def test_unsubscribe_nonexistent_subscriber(self):
        result = self.tm.unsubscribe("SUB-001", "college.ict")

        self.assertTrue(result)
        self.assertEqual(self.tm.subscriptions, {})

    def test_unsubscribe_invalid_topic(self):
        result = self.tm.unsubscribe("SUB-001", "college.invalid")

        self.assertFalse(result)
        self.assertEqual(self.tm.subscriptions, {})

    def test_unsubscribe_last_subscriber(self):
        self.tm.subscribe("SUB-001", "college.ict")

        self.tm.unsubscribe("SUB-001", "college.ict")

        self.assertEqual(self.tm.subscriptions, {})

    def test_get_subscribers_multiple(self):
        self.tm.subscribe("SUB-001", "college.ict")
        self.tm.subscribe("SUB-002", "college.ict")

        self.assertEqual(
            self.tm.get_subscribers("college.ict"),
            {"SUB-001", "SUB-002"},
        )

    def test_get_subscribers_empty_topic(self):
        self.assertEqual(self.tm.get_subscribers("college.ict"), set())

    def test_get_subscribers_returns_copy(self):
        self.tm.subscribe("SUB-001", "college.ict")

        subscribers = self.tm.get_subscribers("college.ict")
        subscribers.clear()

        self.assertEqual(
            self.tm.get_subscribers("college.ict"),
            {"SUB-001"},
        )

    def test_get_subscriptions_multiple_topics(self):
        self.tm.subscribe("SUB-001", "college.ict")
        self.tm.subscribe("SUB-001", "university.announcements")
        self.tm.subscribe("SUB-002", "college.business")

        self.assertEqual(
            self.tm.get_subscriptions("SUB-001"),
            ["college.ict", "university.announcements"],
        )

    def test_get_subscriptions_empty(self):
        self.assertEqual(self.tm.get_subscriptions("SUB-999"), [])

    def test_get_subscriptions_sorted(self):
        self.tm.subscribe("SUB-001", "university.library")
        self.tm.subscribe("SUB-001", "college.ict")
        self.tm.subscribe("SUB-001", "university.academic")

        self.assertEqual(
            self.tm.get_subscriptions("SUB-001"),
            ["college.ict", "university.academic", "university.library"],
        )

 # Tests for remove_subscriber()

    def test_remove_subscriber_from_all_topics(self):
        self.tm.subscribe("SUB-001", "college.ict")
        self.tm.subscribe("SUB-001", "university.events")
        self.tm.subscribe("SUB-002", "college.ict")

        self.tm.remove_subscriber("SUB-001")

        self.assertEqual(self.tm.get_subscriptions("SUB-001"), [])
        self.assertEqual(
            self.tm.get_subscribers("college.ict"),
            {"SUB-002"},
        )

    def test_remove_last_subscriber_cleans_empty_topics(self):
        self.tm.subscribe("SUB-001", "college.ict")
        self.tm.subscribe("SUB-001", "university.events")

        self.tm.remove_subscriber("SUB-001")

        self.assertEqual(self.tm.subscriptions, {})


if __name__ == "__main__":
    unittest.main()
