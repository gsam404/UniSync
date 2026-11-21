import unittest

from broker.broker_server import BrokerServer


class PublishingTests(unittest.TestCase):

    def setUp(self):
        self.broker = BrokerServer()
        self.publisher_id = "PUB-ICT"

    def test_valid_message_is_accepted_and_stored(self):
        accepted, message = self.broker.publish_message(
            self.publisher_id,
            "college.ict",
            "System Maintenance",
            "The system will undergo maintenance tonight.",
        )

        self.assertTrue(accepted)
        self.assertIn(message["message_id"], self.broker.messages)
        self.assertEqual(message["publisher_id"], self.publisher_id)
        self.assertEqual(message["topic"], "college.ict")
        self.assertEqual(message["title"], "System Maintenance")

    def test_invalid_topic_is_rejected(self):
        accepted, result = self.broker.publish_message(
            self.publisher_id,
            "college.fake",
            "Test",
            "Test content",
        )

        self.assertFalse(accepted)
        self.assertEqual(result, "Invalid topic")

    def test_empty_title_is_rejected(self):
        accepted, result = self.broker.publish_message(
            self.publisher_id,
            "college.ict",
            "   ",
            "Test content",
        )

        self.assertFalse(accepted)
        self.assertEqual(result, "Title cannot be empty")

    def test_empty_content_is_rejected(self):
        accepted, result = self.broker.publish_message(
            self.publisher_id,
            "college.ict",
            "Test title",
            "   ",
        )

        self.assertFalse(accepted)
        self.assertEqual(result, "Content cannot be empty")

    def test_messages_have_unique_ids(self):
        _, message1 = self.broker.publish_message(
            self.publisher_id,
            "college.ict",
            "Announcement 1",
            "First announcement",
        )

        _, message2 = self.broker.publish_message(
            self.publisher_id,
            "college.ict",
            "Announcement 2",
            "Second announcement",
        )

        self.assertNotEqual(
            message1["message_id"],
            message2["message_id"],
        )

        self.assertEqual(len(self.broker.messages), 2)


if __name__ == "__main__":
    unittest.main()