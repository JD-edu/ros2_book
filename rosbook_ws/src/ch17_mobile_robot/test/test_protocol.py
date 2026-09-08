import pytest
from ch17_mobile_robot.protocol import CMD_VEL, PacketParser, pack_packet

def test_packet_round_trip_and_fragmentation():
    parser = PacketParser()
    packet = pack_packet(CMD_VEL, b'\x01\x02\x03')
    assert parser.feed(b'noise' + packet[:3]) == []
    assert parser.feed(packet[3:]) == [(CMD_VEL, b'\x01\x02\x03')]

def test_parser_recovers_after_corruption():
    parser = PacketParser()
    bad = bytearray(pack_packet(CMD_VEL, b'x'))
    bad[-2] ^= 1
    assert parser.feed(bytes(bad) + pack_packet(CMD_VEL, b'y')) == [(CMD_VEL, b'y')]
    assert parser.invalid_packets == 1

def test_payload_limit():
    with pytest.raises(ValueError):
        pack_packet(CMD_VEL, bytes(33))
