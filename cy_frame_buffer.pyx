# cython: language_level=3
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy
from cpython.bytes cimport PyBytes_AsString

import time

cdef class CFrameData:
    cdef:
        int number
        double send_time
        float create_time
        int n_received
        int n_total
        char* buffer  # Using C array for buffer

    def __cinit__(self, int packet_size, int total_packets):
        self.buffer = <char*>malloc(packet_size * total_packets)
        if not self.buffer:
            raise MemoryError()

    def __dealloc__(self):
        if self.buffer:
            free(self.buffer)

cdef class FrameBuffer:
    cdef int packet_size
    cdef double expiration
    cdef dict frames

    def __init__(self, int packet_size, double expiration=1.0):
        self.frames = {}
        self.packet_size = packet_size
        self.expiration = expiration

    def add_packet(
        self,
        int frame_number,
        double timestamp,
        int packet_idx,
        int total_packets,
        bytes data
    ):
        cdef CFrameData frame_data
        cdef int start

        if frame_number not in self.frames:
            frame_data = CFrameData(self.packet_size, total_packets)
            frame_data.number = frame_number
            frame_data.send_time = timestamp
            frame_data.create_time = float(time.time())
            frame_data.n_received = 0
            frame_data.n_total = total_packets
            self.frames[frame_number] = frame_data
        else:
            frame_data = self.frames[frame_number]

        # Ensure data is a bytes object and copy into the buffer
        if not isinstance(data, bytes):
            raise ValueError("Data must be of type bytes.")

        start = packet_idx * self.packet_size
        cdef char* data_ptr = PyBytes_AsString(data)
        memcpy(frame_data.buffer + start, data_ptr, self.packet_size)
        frame_data.n_received += 1

        if frame_data.n_received == frame_data.n_total:
            self.flush_frame(frame_data)

    cdef flush_frame(self, CFrameData frame_data):
        cost = 1000 * (time.time() - frame_data.send_time)
        print(f"Frame {frame_data.number} complete. Cost = {cost}")
        del self.frames[frame_data.number]

    def cleanup(self):
        cdef int frame_number
        cdef CFrameData frame_data
        cdef float current_time = float(time.time())
        to_delete = []

        for frame_number, frame_data in self.frames.items():
            if current_time - frame_data.create_time > self.expiration:
                to_delete.append(frame_number)

        for frame_number in to_delete:
            print(f"Frame {frame_number} expired")
            del self.frames[frame_number]
