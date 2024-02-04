import sys
import socket
import time
import struct


HeaderStruct = struct.Struct("IId")

SERVER_IP = "192.168.31.88"


def receive_frame(sock):
    # Read message length
    header_data = sock.recv(HeaderStruct.size)
    seq_id, body_size, timestamp = HeaderStruct.unpack(header_data)

    data = bytearray()
    while len(data) < body_size:
        packet = sock.recv(body_size - len(data))
        if not packet:
            return None
        data.extend(packet)

    delay = round((time.time() - timestamp) * 1000, 2)
    print(f"Seq {seq_id}, data size = {body_size}, delay = {delay} ms")


def frame_processor_client(server_ip=SERVER_IP, server_port=8003):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((server_ip, server_port))
        print("Connected to the server.")

        try:
            while True:
                receive_frame(sock)

        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    frame_processor_client()
