import threading
import logging

from networking.socket_utils import send_msg, recv_msg
from networking.protocol import (
    REGISTER_PUBLISHER,
    REGISTER_SUBSCRIBER,
    VALID_REGISTRATION_TYPES,
    PUBLISH,
    SUBSCRIBE,
    UNSUBSCRIBE,
    STATUS,
    ERROR,
    DISCONNECT,
    create_message,
)


logger = logging.getLogger(__name__)


class ClientHandler(threading.Thread):

    def __init__(self, broker, client_socket, address):
        super().__init__(daemon=True)

        self.broker = broker
        self.sock = client_socket
        self.address = address

        self.client_id = None
        self.role = None
        self.registered = False

        # Prevent concurrent writes from corrupting TCP message framing.
        self.send_lock = threading.Lock()

    def send(self, message):
        """
        Safely sends a message through this client's socket.
        """

        with self.send_lock:
            send_msg(self.sock, message)

    def run(self):
        try:
            self.handle_client()

        except (ConnectionError, ValueError, OSError) as exc:
            logger.warning(
                "Client connection error from %s: %s",
                self.address,
                exc,
            )

        except Exception:
            logger.exception(
                "Unexpected error handling client %s",
                self.address,
            )

        finally:
            self.cleanup()

    def handle_client(self):
        """
        Handles the initial registration and the client's
        connection lifecycle.
        """

        # 1. Wait for the client's first message.
        first_message = recv_msg(self.sock)

        if first_message is None:
            return

        # 2. Validate the registration message.
        if not isinstance(first_message, dict):
            self.send_error("Invalid message format")
            return

        message_type = first_message.get("type")

        if message_type not in VALID_REGISTRATION_TYPES:
            self.send_error("First message must be a registration")
            return

        client_id = first_message.get("client_id")

        if not isinstance(client_id, str) or not client_id.strip():
            self.send_error("Missing or invalid client_id")
            return

        client_id = client_id.strip()

        # 3. Determine client role.
        if message_type == REGISTER_PUBLISHER:
            role = "publisher"

        elif message_type == REGISTER_SUBSCRIBER:
            role = "subscriber"

        else:
            self.send_error("Invalid client role")
            return

        # 4. Register with the broker.
        accepted = self.broker.register(
            client_id,
            role,
            self,
        )

        if not accepted:
            self.send_error("client_id already connected")
            return

        self.client_id = client_id
        self.role = role
        self.registered = True

        logger.info(
            "%s connected | ID: %s | Address: %s",
            role.capitalize(),
            client_id,
            self.address,
        )

        # 5. Tell the client registration was successful.
        self.send(
            create_message(
                STATUS,
                status="OK",
                ref=message_type,
            )
        )

        # 6. Keep the connection alive.
        while True:

            message = recv_msg(self.sock)

            # Client disconnected unexpectedly.
            if message is None:
                break

            if not isinstance(message, dict):
                self.send_error("Invalid message format")
                continue

            message_type = message.get("type")

            # Normal disconnect.
            if message_type == DISCONNECT:
                break

            # Handle published messages.
            if message_type == PUBLISH:

                # Only publishers are allowed to publish.
                if self.role != "publisher":
                    self.send_error(
                        "Only publishers can publish messages"
                    )
                    continue

                # Extract message fields.
                topic = message.get("topic")
                title = message.get("title")
                content = message.get("content")

                # Let the broker validate and store the message.
                accepted, result = self.broker.publish_message(
                    self.client_id,
                    topic,
                    title,
                    content,
                )

                # Reject invalid messages.
                if not accepted:
                    self.send_error(result)
                    continue

                # Confirm that the message was accepted.
                self.send(
                    create_message(
                        STATUS,
                        status="ACCEPTED",
                        ref=PUBLISH,
                        message_id=result["message_id"],
                    )
                )

                continue

                            # Handle subscription requests.
            if message_type == SUBSCRIBE:

                # Only subscribers are allowed to subscribe.
                if self.role != "subscriber":
                    self.send_error(
                        "Only subscribers can subscribe to topics"
                    )
                    continue

                # Extract the requested topic.
                topic = message.get("topic")

                # Ask the broker's TopicManager to subscribe this client.
                accepted = self.broker.topic_manager.subscribe(
                    self.client_id,
                    topic,
                )

                # Reject invalid topics.
                if not accepted:
                    self.send_error("Invalid topic")
                    continue

                # Confirm successful subscription.
                self.send(
                    create_message(
                        STATUS,
                        status="SUBSCRIBED",
                        ref=SUBSCRIBE,
                        topic=topic,
                    )
                )

                continue

            # Handle unsubscription requests.
                        # Handle unsubscription requests.
            if message_type == UNSUBSCRIBE:

                # Only subscribers are allowed to unsubscribe.
                if self.role != "subscriber":
                    self.send_error(
                        "Only subscribers can unsubscribe from topics"
                    )
                    continue

                # Extract the requested topic.
                topic = message.get("topic")

                # Ask the broker's TopicManager to unsubscribe this client.
                accepted = self.broker.topic_manager.unsubscribe(
                    self.client_id,
                    topic,
                )

                # Reject invalid topics.
                if not accepted:
                    self.send_error("Invalid topic")
                    continue

                # Confirm successful unsubscription.
                self.send(
                    create_message(
                        STATUS,
                        status="UNSUBSCRIBED",
                        ref=UNSUBSCRIBE,
                        topic=topic,
                    )
                )

                continue

            # Other messages are not supported yet.
            # Routing and subscriptions will be implemented later.
            self.send_error(
                f"Unsupported message type: {message_type}"
            )

    def send_error(self, reason):
        """
        Sends an ERROR response to the client.
        """

        try:
            self.send(
                create_message(
                    ERROR,
                    reason=reason,
                )
            )

        except (ConnectionError, OSError):
            logger.debug(
                "Could not send error to %s",
                self.address,
            )

    def cleanup(self):
        """
        Removes the client from the broker and closes its socket.
        """

        if self.registered:
            self.broker.unregister(self.client_id)

            logger.info(
                "%s disconnected | ID: %s",
                self.role.capitalize(),
                self.client_id,
            )

            self.registered = False

        try:
            self.sock.shutdown(2)

        except OSError:
            pass

        try:
            self.sock.close()

        except OSError:
            pass