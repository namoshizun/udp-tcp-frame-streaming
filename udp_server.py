import socket
import struct
import asyncio
import time

# from py_frame_buffer import FrameBuffer

from cy_frame_buffer import FrameBuffer


# Header format: frame_number, packet_idx, total_packets, packet_size, timestamp
HeaderStruct = struct.Struct("!IIIId")
unpack_header = HeaderStruct.unpack
SERVER_IP = "0.0.0.0"


class FrameBufferManager:

    def __init__(self):
        self.buffers: dict[int, FrameBuffer] = {}  # Client ID => Frame Buffer
        self.last_clean_up = time.time()

    def add_packet(
        self,
        client_id: int,
        data: bytes,
    ):
        frame_number, packet_idx, total_packets, packet_size, timestamp = unpack_header(
            data[: HeaderStruct.size]
        )
        if not (buf := self.buffers.get(client_id)):
            buf = self.buffers[client_id] = FrameBuffer(packet_size)

        body_data = data[HeaderStruct.size :]
        buf.add_packet(frame_number, timestamp, packet_idx, total_packets, body_data)
        self.cleanup()

    def cleanup(self):
        current_time = time.time()
        if current_time - self.last_clean_up > 1:
            for buf in self.buffers.values():
                buf.cleanup()
            self.last_clean_up = current_time


class EchoDatagramProtocol(asyncio.DatagramProtocol):
    def __init__(self, buffer_manager):
        self.buffer_manager: FrameBufferManager = buffer_manager

    def datagram_received(self, data, addr):
        client_id = addr[1]
        self.buffer_manager.add_packet(client_id, data)


async def async_udp_server(host=SERVER_IP, port=8003):
    loop = asyncio.get_running_loop()
    buffer_manager = FrameBufferManager()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: EchoDatagramProtocol(buffer_manager), local_addr=(host, port)
    )
    print(f"Server listening on {host}:{port}")

    try:
        await asyncio.Future()  # Run forever
    finally:
        transport.close()


def udp_server(host=SERVER_IP, port=8003):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((host, port))
        buffer_manager = FrameBufferManager()
        print(f"UDP Server listening on {host}:{port}")

        while True:
            message, client_address = sock.recvfrom(1080 * 61)
            client_id = client_address[1]  # Using client's port as a simple identifier
            buffer_manager.add_packet(client_id, message)


if __name__ == "__main__":
    udp_server()
    # asyncio.run(async_udp_server())
