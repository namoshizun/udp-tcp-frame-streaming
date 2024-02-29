import sys
import socket
import time
import struct


HeaderStruct = struct.Struct("IId")

SERVER_IP = "0.0.0.0"

N = 0


def get_frame_data():
    return b"\0" * 600 * 1024  # 600KB dummy data


def send_frame(sock, frame_data):
    global N
    header_data = HeaderStruct.pack(N, len(frame_data), time.time())
    sock.sendall(header_data + frame_data)
    print(f"Sent frame {N}")
    N += 1


def frame_producer_server(port=8003):
    frame_data = get_frame_data()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, port))
    server_socket.listen()

    print("Waiting for a connection...")
    client_socket, addr = server_socket.accept()
    print(f"Connected to {addr}")

    try:
        while True:
            send_frame(client_socket, frame_data)
            time.sleep(1 / 20)  # 20 fps
    except KeyboardInterrupt:
        pass
    finally:
        client_socket.close()
        server_socket.close()


if __name__ == "__main__":
    frame_producer_server()
