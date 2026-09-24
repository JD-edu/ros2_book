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
    max_angular_speed: float | None = None,
) -> tuple[int, int]:
    """Mix linear/angular commands and scale them to left/right PWM.

    When ``max_angular_speed`` is set, a pure rotation at that angular speed
    uses the full PWM range.  This gives an open-loop robot enough starting
    torque to rotate instead of deriving a very small PWM from its track
    width.  Omitting it preserves the kinematic conversion used previously.
    """
    if not math.isfinite(linear_x) or not math.isfinite(angular_z):
        return 0, 0
    if max_linear_speed <= 0.0 or max_pwm <= 0:
        return 0, 0

    linear_pwm = linear_x / max_linear_speed * max_pwm
    if max_angular_speed is None:
        angular_pwm = (
            angular_z * (wheel_separation / 2.0)
            / max_linear_speed * max_pwm
        )
    else:
        if not math.isfinite(max_angular_speed) or max_angular_speed <= 0.0:
            return 0, 0
        angular_pwm = angular_z / max_angular_speed * max_pwm

    left_pwm = round(linear_pwm - angular_pwm)
    right_pwm = round(linear_pwm + angular_pwm)
    return (
        max(-max_pwm, min(max_pwm, left_pwm)),
        max(-max_pwm, min(max_pwm, right_pwm)),
    )


def encode_motor_command(left_pwm: int, right_pwm: int) -> bytes:
    """Encode one fixed-width motor frame followed by a newline."""
    return f'$M,{to_hex16(left_pwm)},{to_hex16(right_pwm)}#\n'.encode('ascii')
