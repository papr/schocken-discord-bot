from random import randint


class ZuVieleWuerfel(Exception):
    pass


def werfen(anzahl):
    if anzahl == 3:
        return sorted(tuple(randint(1, 6) for _ in range(3)), reverse=True)
    elif anzahl == 2:
        return sorted(tuple(randint(1, 6) for _ in range(2)), reverse=True)
    elif anzahl == 1:
        return tuple(randint(1, 6) for _ in range(1))
    else:
        raise ZuVieleWuerfel(
            f"Es dürfen maximal 3 Würfel geworfen werden! Nicht {anzahl}."
        )
