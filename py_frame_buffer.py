import time


class FrameBuffer:
    def __init__(self, packet_size: int, expiration=1):
        self.frames = {}
        self.packet_size = packet_size
        self.expiration = expiration

    def add_packet(
        self,
        frame_number: int,
        timestamp: float,
        packet_idx: int,
        total_packets: int,
        data: bytes,
    ):
        frame_data = self.frames.get(frame_number)
        if not frame_data:
            frame_data = self.frames[frame_number] = {
                "number": frame_number,
                "send_time": timestamp,
                "create_time": time.time(),
                "buffer": bytearray(total_packets * self.packet_size),
                "n_received": 0,
                "n_total": total_packets,
            }

        frame_data["buffer"][
            packet_idx * self.packet_size : (packet_idx + 1) * self.packet_size
        ] = data
        n_received = frame_data["n_received"] = frame_data["n_received"] + 1

        if n_received == total_packets:
            self.flush_frame(frame_data)

    def flush_frame(self, frame_data: dict):
        frame_number = frame_data["number"]
        cost = round(1000 * (time.time() - frame_data["send_time"]), 2)
        print(
            f"Frame {frame_number} complete with size: {len(frame_data['buffer'])} bytes. Cost = {cost} ms"
        )
        del self.frames[frame_number]

    def cleanup(self):
        current_time = time.time()
        to_delete = [
            frame_number
            for frame_number, frame in self.frames.items()
            if current_time - frame["create_time"] > self.expiration
        ]

        for frame_number in to_delete:
            print(f"Frame {frame_number} expired")
            del self.frames[frame_number]
