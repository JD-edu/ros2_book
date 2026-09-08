"""Bidirectional MCU packet protocol shared by the Chapter 17 nodes."""

STX = 0xAA
ETX = 0x55
CMD_VEL = 0x01
ENCODER = 0x02
ACK = 0x03
HEARTBEAT = 0x04
ERROR = 0x05
RESET = 0x06
MAX_PAYLOAD = 32


def pack_packet(type_byte: int, payload: bytes = b'') -> bytes:
    if not 0 <= type_byte <= 255 or len(payload) > MAX_PAYLOAD:
        raise ValueError('invalid packet type or payload length')
    body = bytes((type_byte, len(payload))) + payload
    checksum = 0
    for value in body:
        checksum ^= value
    return bytes((STX,)) + body + bytes((checksum, ETX))


class PacketParser:
    def __init__(self):
        self.buffer = bytearray()
        self.invalid_packets = 0

    def feed(self, data: bytes):
        self.buffer.extend(data)
        packets = []
        while len(self.buffer) >= 5:
            try:
                start = self.buffer.index(STX)
            except ValueError:
                self.buffer.clear()
                break
            del self.buffer[:start]
            if len(self.buffer) < 5:
                break
            length = self.buffer[2]
            if length > MAX_PAYLOAD:
                self.invalid_packets += 1
                del self.buffer[0]
                continue
            frame_length = length + 5
            if len(self.buffer) < frame_length:
                break
            frame = self.buffer[:frame_length]
            checksum = 0
            for value in frame[1:3 + length]:
                checksum ^= value
            if frame[-1] != ETX or frame[-2] != checksum:
                self.invalid_packets += 1
                del self.buffer[0]
                continue
            packets.append((frame[1], bytes(frame[3:3 + length])))
            del self.buffer[:frame_length]
        return packets
