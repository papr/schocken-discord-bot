from random import randint


class ZuVieleWuerfel(Exception):
    pass


def werfen(anzahl):
    if anzahl <= 3:
        return tuple(sorted([randint(1, 6) for _ in range(anzahl)], reverse=True))
    else:
        raise ZuVieleWuerfel(
            f"Es dürfen maximal 3 Würfel geworfen werden! Nicht {anzahl}."
        )
