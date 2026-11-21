import socket
import threading
import logging
import uuid
import time

from broker.topic_manager import is_valid_topic
from broker.client_handler import ClientHandler


logger = logging.getLogger(__name__)


class BrokerServer:

    def __init__(self, host="127.0.0.1", port=5000):

        self.host = host
        self.port = port

        self.server_socket = None
        self.accept_thread = None

        self.running = False

        # client_id -> ClientHandler
        self.clients = {}

        # Protects the shared client registry.
        self.lock = threading.Lock()

        # Stores accepted messages in memory.
        self.messages = {}

        # Protects the shared message collection.
        self.message_lock = threading.Lock()

    def start(self):
        """
        Starts the broker in a background thread.
        """

        if self.running:
            return

        self.server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )

        self.server_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1,
        )

        self.server_socket.bind(
            (self.host, self.port)
        )

        self.server_socket.listen()

        self.running = True

        # Update port when port=0 was used for testing.
        self.port = self.server_socket.getsockname()[1]

        self.accept_thread = threading.Thread(
            target=self.accept_clients,
            daemon=True,
        )

        self.accept_thread.start()

        logger.info(
            "Broker started on %s:%s",
            self.host,
            self.port,
        )

    def accept_clients(self):
        """
        Accepts incoming connections continuously.

        Each connection gets its own ClientHandler thread.
        """

        while self.running:

            try:
                client_socket, address = self.server_socket.accept()

            except OSError:

                if not self.running:
                    break

                logger.exception("Accept failed")
                continue

            handler = ClientHandler(
                self,
                client_socket,
                address,
            )

            handler.start()

    def register(self, client_id, role, handler):
        """
        Atomically registers a client.

        Returns:
            True if registration succeeds
            False if the ID is already in use or the broker is stopping
        """

        with self.lock:

            if not self.running:
                return False

            if client_id in self.clients:
                return False

            self.clients[client_id] = handler

            return True

    def unregister(self, client_id):
        """
        Removes a client safely.
        """

        if client_id is None:
            return

        with self.lock:
            self.clients.pop(client_id, None)

    def get_connected(self):
        """
        Returns a snapshot of connected clients.

        The lock protects the copy from concurrent modifications.
        """

        with self.lock:
            return {
                client_id: handler.role
                for client_id, handler in self.clients.items()
            }

    def stop(self):
        """
        Stops the broker and closes all connected client sockets.
        """

        if not self.running:
            return

        logger.info("Stopping broker...")

        self.running = False

        # Close listening socket to unblock accept().
        try:
            self.server_socket.close()

        except OSError:
            pass

        # Take a snapshot without holding the lock while closing sockets.
        with self.lock:
            handlers = list(self.clients.values())

        # Shutdown client connections.
        # ClientHandler will handle closing its own socket.
        for handler in handlers:

            try:
                handler.sock.shutdown(socket.SHUT_RDWR)

            except OSError:
                pass

        # Wait for client handlers to finish cleanup.
        for handler in handlers:
            handler.join(timeout=2)

        # Wait for the accept loop to finish.
        if self.accept_thread is not None:
            self.accept_thread.join(timeout=2)

        logger.info("Broker stopped")

    def publish_message(self, publisher_id, topic, title, content):
        """
        Validates, creates, and stores a published message.

        Returns:
            (True, message) if successful
            (False, error_reason) if rejected
        """

        # Validate topic
        if not is_valid_topic(topic):
            return False, "Invalid topic"

        # Validate title
        if not isinstance(title, str) or not title.strip():
            return False, "Title cannot be empty"

        # Validate content
        if not isinstance(content, str) or not content.strip():
            return False, "Content cannot be empty"

        # Generate a unique message ID
        message_id = f"MSG-{uuid.uuid4().hex}"

        # Create the message record
        message = {
            "message_id": message_id,
            "publisher_id": publisher_id,
            "topic": topic,
            "title": title.strip(),
            "content": content.strip(),
            "timestamp": time.time(),
        }

        # Store the message safely
        with self.message_lock:
            self.messages[message_id] = message

        logger.info(
            "Message published: %s | Topic: %s | Publisher: %s",
            message_id,
            topic,
            publisher_id,
        )

        return True, message