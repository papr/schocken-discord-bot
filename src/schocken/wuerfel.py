from random import randint


def werfen3W():
    return sorted(tuple(randint(1, 6) for _ in range(3)), reverse=True)

def werfen2W():
    return sorted(tuple(randint(1, 6) for _ in range(2)), reverse=True)

def werfen1W():
    return tuple(randint(1, 6) for _ in range(1))
