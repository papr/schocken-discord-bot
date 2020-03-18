from random import randint


def werfen():
    return tuple(randint(1, 6) for _ in range(3))
