"""Pure helpers for Chapter 15 motor kinematics and serial framing."""

import math


def to_hex16(value: int) -> str:
    """Return a signed integer as four uppercase two's-complement hex digits."""
    value = max(-32768, min(32767, value))
    return f'{value & 0xFFFF:04X}'


def velocity_to_pwm(
    linear_x: float,
    angular_z: float,
    wheel_separation: float,
    max_linear_speed: float,
    max_pwm: int,
) -> tuple[int, int]:
    """Apply differential-drive kinematics and scale wheel speeds to PWM."""
    if not math.isfinite(linear_x) or not math.isfinite(angular_z):
        return 0, 0
    if max_linear_speed <= 0.0 or max_pwm <= 0:
        return 0, 0

    half_track = wheel_separation / 2.0
    left_speed = linear_x - angular_z * half_track
    right_speed = linear_x + angular_z * half_track
    left_pwm = round(left_speed / max_linear_speed * max_pwm)
    right_pwm = round(right_speed / max_linear_speed * max_pwm)
    return (
        max(-max_pwm, min(max_pwm, left_pwm)),
        max(-max_pwm, min(max_pwm, right_pwm)),
    )


def encode_motor_command(left_pwm: int, right_pwm: int) -> bytes:
    """Encode one fixed-width motor frame followed by a newline."""
    return f'$M,{to_hex16(left_pwm)},{to_hex16(right_pwm)}#\n'.encode('ascii')
