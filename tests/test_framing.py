
import json
import socket
import struct
import threading
import unittest

from networking.socket_utils import (
    MAX_MESSAGE_SIZE,
    recv_exact,
    send_msg,
    recv_msg,
)


class FragmentedSocket:
    """Fake socket that returns data in small fragments."""

    def __init__(self, data, fragment_size=1):
        self.data = data
        self.fragment_size = fragment_size

    def recv(self, n):
        if not self.data:
            return b""

        size = min(n, self.fragment_size, len(self.data))

        chunk = self.data[:size]
        self.data = self.data[size:]

        return chunk


class FramingTests(unittest.TestCase):

    def test_recv_exact_fragmented_data(self):
        data = b"abcdefghij"
        fake_socket = FragmentedSocket(data, fragment_size=1)

        result = recv_exact(fake_socket, 10)

        self.assertEqual(result, data)

    def test_recv_exact_zero_bytes(self):
        fake_socket = FragmentedSocket(b"hello")

        result = recv_exact(fake_socket, 0)

        self.assertEqual(result, b"")

    def test_recv_exact_incomplete_data(self):
        fake_socket = FragmentedSocket(b"abcd", fragment_size=2)

        with self.assertRaises(ConnectionError):
            recv_exact(fake_socket, 10)

    def test_clean_disconnect(self):
        sender, receiver = socket.socketpair()

        sender.close()

        try:
            result = recv_msg(receiver)
            self.assertIsNone(result)
        finally:
            receiver.close()

    def test_partial_header(self):
        sender, receiver = socket.socketpair()

        sender.sendall(b"\x00\x00")
        sender.close()

        try:
            with self.assertRaises(ConnectionError):
                recv_msg(receiver)
        finally:
            receiver.close()

    def test_partial_body(self):
        sender, receiver = socket.socketpair()

        header = struct.pack(">I", 100)

        sender.sendall(header + b"1234567890")
        sender.close()

        try:
            with self.assertRaises(ConnectionError):
                recv_msg(receiver)
        finally:
            receiver.close()

    def test_oversized_header(self):
        sender, receiver = socket.socketpair()

        oversized_header = struct.pack(">I", MAX_MESSAGE_SIZE + 1)
        sender.sendall(oversized_header)

        try:
            with self.assertRaises(ValueError):
                recv_msg(receiver)
        finally:
            sender.close()
            receiver.close()

    def test_invalid_json(self):
        sender, receiver = socket.socketpair()

        body = b"not json"
        header = struct.pack(">I", len(body))

        sender.sendall(header + body)

        try:
            with self.assertRaises(ValueError):
                recv_msg(receiver)
        finally:
            sender.close()
            receiver.close()

    def test_invalid_utf8(self):
        sender, receiver = socket.socketpair()

        body = b"\xff\xfe"
        header = struct.pack(">I", len(body))

        sender.sendall(header + body)

        try:
            with self.assertRaises(UnicodeDecodeError):
                recv_msg(receiver)
        finally:
            sender.close()
            receiver.close()

    def test_one_message(self):
        sender, receiver = socket.socketpair()

        message = {
            "type": "PING",
            "message": "Hello, UniSync!"
        }

        try:
            send_msg(sender, message)

            received = recv_msg(receiver)

            self.assertEqual(received, message)
        finally:
            sender.close()
            receiver.close()

    def test_three_consecutive_messages(self):
        sender, receiver = socket.socketpair()

        messages = [
            {"id": 1, "message": "First"},
            {"id": 2, "message": "Second"},
            {"id": 3, "message": "Third"},
        ]

        def send_messages():
            for message in messages:
                send_msg(sender, message)

        sender_thread = threading.Thread(target=send_messages)
        sender_thread.start()

        try:
            received_messages = []

            for _ in range(3):
                received_messages.append(recv_msg(receiver))

            self.assertEqual(received_messages, messages)

        finally:
            sender_thread.join()
            sender.close()
            receiver.close()

    def test_large_payload(self):
        sender, receiver = socket.socketpair()

        message = {
            "type": "TEST",
            "message": "x" * 100_000
        }

        sender_thread = threading.Thread(
            target=lambda: send_msg(sender, message)
        )

        sender_thread.start()

        try:
            received = recv_msg(receiver)

            self.assertEqual(len(received["message"]), 100_000)
            self.assertEqual(received, message)

        finally:
            sender_thread.join()
            sender.close()
            receiver.close()

    def test_message_exceeds_send_limit(self):
        sender, receiver = socket.socketpair()

        message = {
            "message": "x" * (MAX_MESSAGE_SIZE + 100)
        }

        try:
            with self.assertRaises(ValueError):
                send_msg(sender, message)
        finally:
            sender.close()
            receiver.close()


if __name__ == "__main__":
    unittest.main()
