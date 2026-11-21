
import json
import struct


MAX_MESSAGE_SIZE = 1024 * 1024  # 1 MB


def recv_exact(sock, n):
    """Receive exactly n bytes from a socket."""
    if n == 0:
        return b""

    chunks = []
    bytes_received = 0

    while bytes_received < n:
        chunk = sock.recv(n - bytes_received)

        if chunk == b"":
            raise ConnectionError("Connection closed before all bytes were received")

        chunks.append(chunk)
        bytes_received += len(chunk)

    return b"".join(chunks)


def send_msg(sock, obj):
    """Serialize a dictionary and send it using length-prefixed framing."""
    body = json.dumps(obj).encode("utf-8")

    if len(body) > MAX_MESSAGE_SIZE:
        raise ValueError("Message exceeds the 1 MB size limit")

    header = struct.pack(">I", len(body))

    sock.sendall(header + body)


def recv_msg(sock):
    """Receive one complete framed JSON message."""
    # Read the first byte separately to detect a clean disconnect.
    first_byte = sock.recv(1)

    if first_byte == b"":
        return None

    # The first byte exists, so the rest of the header must arrive.
    remaining_header = recv_exact(sock, 3)
    header = first_byte + remaining_header

    message_length = struct.unpack(">I", header)[0]

    if message_length > MAX_MESSAGE_SIZE:
        raise ValueError("Received message exceeds the 1 MB size limit")

    body = recv_exact(sock, message_length)

    decoded_body = body.decode("utf-8")
    message = json.loads(decoded_body)

    if not isinstance(message, dict):
        raise ValueError("Received JSON message must be a dictionary")

    return message
