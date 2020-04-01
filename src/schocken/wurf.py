import typing as T
from enum import Enum

_ZAHL = {1: "eins", 2: "zwei", 3: "drei", 4: "vier", 5: "fuenf", 6: "sechs"}


class Wurf(Enum):
    pass


class SonderWurf(Wurf):
    Jule = (4, 2, 1)
    Herrenwurf = (6, 5, 5)

    @property
    def deckel_wert(self):
        return {self.Jule: 7, self.Herrenwurf: 1}[self]


_zahlen_3_bis_6 = tuple(map(lambda i: _ZAHL[i], range(3, 7)))
_schock_namen = ("out", "doof") + _zahlen_3_bis_6
_schocks = [
    (schock_name, (schock_suffix, 1, 1))
    for schock_name, schock_suffix in zip(_schock_namen, range(1, 7))
]
Schock = Wurf("Schock", _schocks)
Schock.deckel_wert = property(
    lambda self: 15 if self is Schock.out else self._value_[0]
)

_generaele = [(f"{_ZAHL[i]}er", (i,) * 3) for i in range(2, 7)]
General = Wurf("General", _generaele)
General.deckel_wert = property(lambda self: 3)

_zahlen_1_bis_4 = tuple(map(lambda i: _ZAHL[i], range(1, 5)))
_straßen_namen = (f"{zahl}er" for zahl in _zahlen_1_bis_4)
_straßen = [(name, (i + 3, i + 2, i + 1)) for i, name in enumerate(_straßen_namen)]
Straße = Wurf("Straße", _straßen)
Straße.deckel_wert = property(lambda self: 2)


class Gemuese:
    def __init__(self, augen):
        self._value_ = augen

    def __repr__(self):
        return f"<{type(self).__name__}: {self._value_}>"

    @property
    def deckel_wert(self):
        return 1


def welcher_wurf(wuerfel_augen: T.Tuple[int, int, int], aus_der_hand: bool = True):
    wuerfel_augen = tuple(sorted(wuerfel_augen, reverse=True))
    wurf_klassen = [Schock]
    if aus_der_hand:
        wurf_klassen += [SonderWurf, General, Straße]
    for wurf_klasse in wurf_klassen:
        if wuerfel_augen in [wurf._value_ for wurf in wurf_klasse]:
            return wurf_klasse(wuerfel_augen)
    else:
        return Gemuese(wuerfel_augen)


def prioritaet(wurf):
    prio = None
    if isinstance(wurf, Gemuese) or wurf is SonderWurf.Herrenwurf:
        prio = wurf._value_[0] / 10 + wurf._value_[1] / 100 + wurf._value_[2] / 1000
    elif wurf is SonderWurf.Jule:
        prio = 4.07
    elif wurf in Schock:
        prio = 4 + wurf.deckel_wert / 100
    elif wurf in General:
        prio = 3 + wurf._value_[0] / 10
    elif wurf in Straße:
        prio = 2 + wurf._value_[0] / 10
    else:
        raise ValueError(f"Unhandled wurf {wurf}")
    return -prio
