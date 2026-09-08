from ch15_motor_control.protocol import (
    encode_motor_command,
    to_hex16,
    velocity_to_pwm,
)


def test_to_hex16_handles_positive_negative_and_limits():
    assert to_hex16(120) == '0078'
    assert to_hex16(-100) == 'FF9C'
    assert to_hex16(40000) == '7FFF'
    assert to_hex16(-40000) == '8000'


def test_encode_motor_command_has_fixed_width():
    frame = encode_motor_command(120, -100)
    assert frame == b'$M,0078,FF9C#\n'
    assert len(frame) == 14


def test_velocity_to_pwm_forward_turn_and_saturation():
    assert velocity_to_pwm(0.5, 0.0, 0.2, 0.5, 255) == (255, 255)
    assert velocity_to_pwm(0.0, 1.0, 0.2, 0.5, 255) == (-51, 51)
    assert velocity_to_pwm(1.0, 0.0, 0.2, 0.5, 255) == (255, 255)


def test_velocity_to_pwm_rejects_non_finite_input():
    assert velocity_to_pwm(float('nan'), 0.0, 0.2, 0.5, 255) == (0, 0)
