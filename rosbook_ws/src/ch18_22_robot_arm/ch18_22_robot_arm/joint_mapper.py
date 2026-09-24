"""Pure-Python joint-to-servo conversion used by the serial bridge."""

import math


JOINT_NAMES = [
    'joint_1',
    'joint_2',
    'joint_3',
    'joint_4',
    'joint_5',
]


class JointMapper:
    """Apply servo zero, direction and physical limits to ROS joint positions."""

    def __init__(self, offsets, directions, minimums, maximums):
        size = len(JOINT_NAMES)
        values = (offsets, directions, minimums, maximums)
        if any(len(value) != size for value in values):
            raise ValueError(f'all calibration arrays must contain {size} values')
        if any(direction not in (-1, 1) for direction in directions):
            raise ValueError('directions must contain only -1 or 1')
        if any(low > high for low, high in zip(minimums, maximums)):
            raise ValueError('each minimum angle must be <= its maximum angle')
        self.offsets = list(offsets)
        self.directions = list(directions)
        self.minimums = list(minimums)
        self.maximums = list(maximums)

    def positions_from_message(self, names, positions):
        """Return positions in canonical joint order, independent of message order."""
        if len(names) != len(positions):
            raise ValueError('joint name and position counts differ')
        values = dict(zip(names, positions))
        missing = [name for name in JOINT_NAMES if name not in values]
        if missing:
            raise ValueError(f'missing joints: {", ".join(missing)}')
        ordered = [float(values[name]) for name in JOINT_NAMES]
        if not all(math.isfinite(value) for value in ordered):
            raise ValueError('joint positions must be finite')
        return ordered

    def to_servo_degrees(self, positions):
        if len(positions) != len(JOINT_NAMES):
            raise ValueError(f'exactly {len(JOINT_NAMES)} joint positions are required')
        result = []
        for position, offset, direction, low, high in zip(
                positions, self.offsets, self.directions,
                self.minimums, self.maximums):
            angle = offset + direction * math.degrees(position)
            result.append(int(round(min(max(angle, low), high))))
        return result


def encode_command(sequence, angles):
    """Encode one newline-terminated command understood by the Arduino firmware."""
    if len(angles) != len(JOINT_NAMES):
        raise ValueError(f'exactly {len(JOINT_NAMES)} servo angles are required')
    return f'SET,{sequence},' + ','.join(str(int(value)) for value in angles) + '\n'
