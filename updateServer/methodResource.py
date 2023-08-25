import struct
from typing import Optional


def send_msg(sock, msg):
    # Prefix each message with a 8-byte length (network byte order)
    msg = struct.pack('>Q', len(msg)) + msg
    sock.sendall(msg)


def recv_msg(sock) -> Optional[bytes]:
    # 8-byte
    payload_size = struct.calcsize(">Q")

    # Read message length and unpack it into an integer
    raw_msg_len = recv_all(sock, payload_size)
    if not raw_msg_len:
        return None

    msg_len = struct.unpack('>Q', raw_msg_len)[0]

    # Read the message data
    return recv_all(sock, msg_len)


def recv_all(sock, n) -> Optional[bytes]:
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()

    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None

        data += packet

    return bytes(data)