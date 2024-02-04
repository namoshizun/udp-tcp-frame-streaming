import socket
import time
import struct


# Packet format: frame_number, packet_idx, total_packets, packet_size, timestamp
HeaderStruct = struct.Struct("!IIIId")
pack_header = HeaderStruct.pack
SERVER_IP = "192.168.31.88"


def send_frame_data(sock, server_address, frame_number, data):
    # NOTE: Need to increase the `net.inet.udp.maxdgram` to `65535`. Default is `9216`.
    # MacOS: sudo sysctl -w net.inet.udp.maxdgram=65535
    # Ubuntu: sudo sysctl -w net.core.rmem_default=2621440
    #         sudo sysctl -w net.core.rmem_max=2621440
    MAX_PACKET_SIZE = 1080 * 60
    total_packets = (len(data) + MAX_PACKET_SIZE - 1) // MAX_PACKET_SIZE
    since = time.time()

    for i in range(total_packets):
        header = pack_header(frame_number, i, total_packets, MAX_PACKET_SIZE, since)
        packet = header + data[i * MAX_PACKET_SIZE : (i + 1) * MAX_PACKET_SIZE]
        sock.sendto(packet, server_address)
    print(f"Sent frame {frame_number} with {total_packets} packets. Start at {since}")


def video_stream_client(server_ip, server_port):
    server_address = (server_ip, server_port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    frame_number = 0
    try:
        frame_data = b"\0" * 600 * 1024  # 600KB dummy data
        while True:
            # Simulate capturing a frame (600KB of data)
            send_frame_data(sock, server_address, frame_number, frame_data)
            frame_number += 1
            time.sleep(1 / 20)  # Simulate a 20fps frame rate
    finally:
        sock.close()


# Example usage
if __name__ == "__main__":
    video_stream_client(SERVER_IP, 8003)
