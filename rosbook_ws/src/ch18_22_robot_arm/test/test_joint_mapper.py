import math

import pytest

from ch18_22_robot_arm.joint_mapper import JOINT_NAMES, JointMapper, encode_command


def make_mapper():
    return JointMapper([90] * 5, [1, -1, 1, -1, 1], [10] * 5, [170] * 5)


def test_message_order_does_not_change_servo_order():
    mapper = make_mapper()
    names = list(reversed(JOINT_NAMES))
    positions = list(reversed([0.0, math.pi / 2, 0.0, 0.0, 0.0]))
    ordered = mapper.positions_from_message(names, positions)
    assert mapper.to_servo_degrees(ordered) == [90, 10, 90, 90, 90]


def test_servo_output_is_clamped_to_physical_limits():
    mapper = make_mapper()
    assert mapper.to_servo_degrees([10.0, 10.0, -10.0, -10.0, 0.0]) == [170, 10, 10, 170, 90]


def test_missing_joint_is_rejected():
    with pytest.raises(ValueError, match='missing joints'):
        make_mapper().positions_from_message(JOINT_NAMES[:4], [0.0] * 4)


def test_command_format():
    assert encode_command(7, [90, 80, 70, 60, 50]) == 'SET,7,90,80,70,60,50\n'
