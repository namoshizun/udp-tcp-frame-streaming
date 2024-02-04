## UDP vs TCP Socket for Frame Streaming

Simple programs to compare the performance of UDP and TCP sockets for frame streaming.

**Note**:

Linux and MacOS have limited UDP buffer size. You may need to increase the buffer size to get better performance:
  - MacOS: `sudo sysctl -w net.inet.udp.maxdgram=65535`
  - Linux:
    - `sudo sysctl -w net.core.rmem_max=26214400`
    - `sudo sysctl -w net.core.rmem_default=26214400`
