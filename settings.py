DEBUG = True

PINS = {
    'motor': {
        'left': [27, 22],
        'right': [23, 24]
    },
    'encoder': {
        'left': [12, 16],
        'right': [20, 21]
    }
}

pid_params = {
    'balance': {
        'k': 0.6,
        'p': 30,
        'd': 0.6
    },
    'velocity': {
        'p': 8,
        'i': 8/200
    },
    'turn': {
        'p': 0.4,
        'd': 0.2
    }
}

gyro_offset = {
    'y': 1.4,
    'z': 0.7
}
accel_offset = {
    'x': -230,
    'y': -1.5,
    'z': -14100
}
