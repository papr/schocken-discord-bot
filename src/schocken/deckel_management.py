import typing as T


class ZuWenigSpieler(Exception):
    pass


class FalscherSpieler(Exception):
    pass


class DeckelManagement:
    def __init__(self, spieler_reihenfolge: T.List[str]):
        if len(spieler_reihenfolge) < 2:
            raise ZuWenigSpieler

        self._topf = 0
        self._nächster_spieler = spieler_reihenfolge[0]
        self._deckel_stand = {S: 0 for S in spieler_reihenfolge}
        self._würfe = {S: [] for S in spieler_reihenfolge}

    def wurf(
        self, spieler: str, wurf: T.Tuple[int, int, int], aus_der_hand: bool = True
    ):
        pass
