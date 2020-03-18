import typing as T
from enum import Enum, auto

_ZAHL = {1: "eins", 2: "zwei", 3: "drei", 4: "vier", 5: "fünf", 6: "sechs"}


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

_generäle = [(f"{_ZAHL[i]}er", (i,) * 3) for i in range(2, 7)]
General = Wurf("General", _generäle)
General.deckel_wert = property(lambda self: 3)

_zahlen_1_bis_4 = tuple(map(lambda i: _ZAHL[i], range(1, 5)))
_straßen_namen = (f"{zahl}er" for zahl in _zahlen_1_bis_4)
_straßen = [(name, (i + 3, i + 2, i + 1)) for i, name in enumerate(_straßen_namen)]
Straße = Wurf("Straße", _straßen)
Straße.deckel_wert = property(lambda self: 2)


class Gemüse(Wurf):
    tiefes = auto()
    hohes = auto()

    @property
    def deckel_wert(self):
        return 1


def welcher_wurf(würfel_augen: T.Tuple[int, int, int], aus_der_hand: bool = True):
    würfel_augen = tuple(sorted(würfel_augen, reverse=True))
    wurf_klassen = [Schock]
    if aus_der_hand:
        wurf_klassen += [SonderWurf, General, Straße]
    for wurf_klasse in wurf_klassen:
        if würfel_augen in [wurf._value_ for wurf in wurf_klasse]:
            return wurf_klasse(würfel_augen)
    else:
        if würfel_augen[0] < 5:
            return Gemüse.tiefes
        else:
            return Gemüse.hohes
