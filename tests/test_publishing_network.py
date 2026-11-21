import unittest
import socket

from broker.broker_server import BrokerServer
from networking.socket_utils import send_msg, recv_msg
from networking.protocol import (
    REGISTER_PUBLISHER,
    REGISTER_SUBSCRIBER,
    PUBLISH,
    STATUS,
    ERROR,
    create_message,
)


class PublishingNetworkTests(unittest.TestCase):

    def setUp(self):
        # Start a broker on an automatically assigned port.
        self.broker = BrokerServer(port=0)
        self.broker.start()

        # Keep track of sockets created during each test.
        self.client_sockets = []

    def tearDown(self):
        # Close test client sockets.
        for sock in self.client_sockets:
            try:
                sock.close()
            except OSError:
                pass

        # Stop the broker.
        self.broker.stop()

    def connect_client(self, client_id, registration_type):
        # Connect to the running broker.
        sock = socket.create_connection(
            (self.broker.host, self.broker.port),
            timeout=3,
        )

        self.client_sockets.append(sock)

        # Register the client.
        send_msg(
            sock,
            create_message(
                registration_type,
                client_id=client_id,
            ),
        )

        # Receive registration response.
        response = recv_msg(sock)

        self.assertEqual(response["type"], STATUS)
        self.assertEqual(response["status"], "OK")

        return sock

    def test_publisher_can_publish_over_tcp(self):
        publisher = self.connect_client(
            "PUB-ICT",
            REGISTER_PUBLISHER,
        )

        # Send an actual PUBLISH request through TCP.
        send_msg(
            publisher,
            create_message(
                PUBLISH,
                topic="college.ict",
                title="System Maintenance",
                content="The system will undergo maintenance tonight.",
            ),
        )

        # Receive broker acknowledgment.
        response = recv_msg(publisher)

        self.assertEqual(response["type"], STATUS)
        self.assertEqual(response["status"], "ACCEPTED")
        self.assertEqual(response["ref"], PUBLISH)
        self.assertIn("message_id", response)

        # Verify the message actually reached broker storage.
        message_id = response["message_id"]

        self.assertIn(message_id, self.broker.messages)

        stored_message = self.broker.messages[message_id]

        self.assertEqual(stored_message["publisher_id"], "PUB-ICT")
        self.assertEqual(stored_message["topic"], "college.ict")
        self.assertEqual(stored_message["title"], "System Maintenance")
        self.assertEqual(
            stored_message["content"],
            "The system will undergo maintenance tonight.",
        )

    def test_subscriber_cannot_publish_over_tcp(self):
        subscriber = self.connect_client(
            "STU-001",
            REGISTER_SUBSCRIBER,
        )

        # Attempt to publish as a subscriber.
        send_msg(
            subscriber,
            create_message(
                PUBLISH,
                topic="college.ict",
                title="Unauthorized Message",
                content="This should be rejected.",
            ),
        )

        # Receive rejection.
        response = recv_msg(subscriber)

        self.assertEqual(response["type"], ERROR)
        self.assertEqual(
            response["reason"],
            "Only publishers can publish messages",
        )

        # The broker must not store the rejected message.
        self.assertEqual(len(self.broker.messages), 0)

    def test_invalid_publish_requests_do_not_disconnect_publisher(self):
        publisher = self.connect_client(
            "PUB-ICT",
            REGISTER_PUBLISHER,
        )

        invalid_requests = [
            {
                "topic": "college.fake",
                "title": "Test Announcement",
                "content": "Test content",
                "expected_reason": "Invalid topic",
            },
            {
                "topic": "college.ict",
                "title": "   ",
                "content": "Test content",
                "expected_reason": "Title cannot be empty",
            },
            {
                "topic": "college.ict",
                "title": "Test Announcement",
                "content": "   ",
                "expected_reason": "Content cannot be empty",
            },
        ]

        for request in invalid_requests:

            # Send invalid publishing request.
            send_msg(
                publisher,
                create_message(
                    PUBLISH,
                    topic=request["topic"],
                    title=request["title"],
                    content=request["content"],
                ),
            )

            # Broker should reject the request.
            response = recv_msg(publisher)

            self.assertEqual(response["type"], ERROR)
            self.assertEqual(
                response["reason"],
                request["expected_reason"],
            )

        # The same publisher should still be connected.
        # Send a valid message after the invalid requests.
        send_msg(
            publisher,
            create_message(
                PUBLISH,
                topic="college.ict",
                title="Valid Announcement",
                content="The publisher connection is still working.",
            ),
        )

        response = recv_msg(publisher)

        # The valid request should still be accepted.
        self.assertEqual(response["type"], STATUS)
        self.assertEqual(response["status"], "ACCEPTED")
        self.assertIn("message_id", response)

        # Only the valid message should have been stored.
        self.assertEqual(len(self.broker.messages), 1)


if __name__ == "__main__":
    unittest.main()