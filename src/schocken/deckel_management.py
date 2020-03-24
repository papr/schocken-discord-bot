import typing as T
from .wurf import welcher_wurf, Wurf
from .spieler import Spieler
from .exceptions import (
    ZuWenigSpieler,
    ZuOftGeworfen,
    FalscherSpieler,
    KeineWürfeVorhanden,
    UnbekannterSpieler,
)

NUM_MAX_DECKEL = 15


class WurfEvaluierung(T.NamedTuple):
    priorität: int
    wurf_anzahl: int
    reihenfolge: int
    spieler: Spieler


class DeckelManagement:
    def __init__(
        self, spieler_reihenfolge: T.List[Spieler], deckel_in_topf=NUM_MAX_DECKEL
    ):
        pass


class RundenDeckelManagement:
    def __init__(self, deckel_in_topf, spieler: T.List[Spieler]):
        if len(spieler) < 2:
            raise ZuWenigSpieler

        self._topf = deckel_in_topf
        self._spieler = spieler
        self._spieler_namen = [S.name for S in self._spieler]
        self._aktueller_spieler_idx = 0
        self._würfe = {S.name: [] for S in spieler}

    def weiter(self):
        if self._aktueller_spieler_idx + 1 >= len(self._spieler):
            raise ValueError("Runde ist bereits vorbei!")
        self._aktueller_spieler_idx += 1

    def wurf(
        self,
        spieler_name: str,
        augen: T.Tuple[int, int, int],
        aus_der_hand: bool = True,
    ) -> Wurf:
        try:
            spieler_idx = self._spieler_namen.index(spieler_name)
        except ValueError as err:
            raise UnbekannterSpieler(spieler_name) from err

        if spieler_idx != self._aktueller_spieler_idx:
            aktueller_spieler = self._spieler_namen[self._aktueller_spieler_idx]
            raise FalscherSpieler(
                f"{spieler_name} hat geworfen, {aktueller_spieler} war aber dran!"
            )

        bestehende_würfe = self._würfe[spieler_name]
        if len(bestehende_würfe) >= self.num_maximale_würfe:
            raise ZuOftGeworfen()

        wurf = welcher_wurf(augen, aus_der_hand)
        bestehende_würfe.append(wurf)
        return wurf

    def hoch_und_tief(self):
        erster_spieler = self._spieler_namen[0]
        if not self._würfe[erster_spieler]:
            raise KeineWürfeVorhanden()

        # for spieler in self._spieler

    @property
    def num_maximale_würfe(self):
        if self._aktueller_spieler_idx == 0:
            return 3
        else:
            aktueller_name = self._spieler_namen[self._aktueller_spieler_idx]
            würfe_start_spieler = self._würfe[aktueller_name]
            num_würfe_start_spieler = len(würfe_start_spieler)
            return num_würfe_start_spieler
