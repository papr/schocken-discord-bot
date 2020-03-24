import typing as T
from .wurf import welcher_wurf, Wurf, priorität
from .spieler import Spieler
from .exceptions import (
    ZuWenigSpieler,
    NochNichtGeworfen,
    ZuOftGeworfen,
    FalscherSpieler,
    KeineWürfeVorhanden,
    UnbekannterSpieler,
)

NUM_MAX_DECKEL = 15


class WurfEvaluierung(T.NamedTuple):
    priorität: float
    wurf_anzahl: int
    reihenfolge: int
    spieler: Spieler
    wurf: Wurf


class SpielzeitStatus(T.NamedTuple):
    deckel_in_topf: int
    spieler: T.List[Spieler]


class RundenDeckelManagement:
    def __init__(self, runden_status: SpielzeitStatus):
        if len(runden_status.spieler) < 2:
            raise ZuWenigSpieler

        self._topf = runden_status.deckel_in_topf
        self._spieler = runden_status.spieler
        self._spieler_namen = [S.name for S in self._spieler]
        self._aktueller_spieler_idx = 0
        self._würfe = {S.name: [] for S in self._spieler}

    def weiter(self) -> int:
        aktueller_spieler = self._spieler_namen[self._aktueller_spieler_idx]
        if not self._würfe[aktueller_spieler]:
            raise NochNichtGeworfen
        if self._aktueller_spieler_idx + 1 >= len(self._spieler):
            raise ValueError("Runde ist bereits vorbei!")
        self._aktueller_spieler_idx += 1
        return self._aktueller_spieler_idx

    def deckel_verteilen(self,) -> SpielzeitStatus:
        hoch, tief = self.hoch_und_tief()
        anzahl_deckel = hoch.wurf.deckel_wert
        if self._topf:
            anzahl_deckel = min(self._topf, anzahl_deckel)
            self._topf -= anzahl_deckel
            tief.spieler.deckel += anzahl_deckel
        else:
            anzahl_deckel = min(hoch.spieler.deckel, anzahl_deckel)
            hoch.spieler.deckel -= anzahl_deckel
            tief.spieler.deckel += anzahl_deckel

        restliche_spieler = [s for s in self._spieler if self._topf or s.deckel]
        return SpielzeitStatus(self._topf, restliche_spieler)


    def wurf(
        self,
        spieler_name: str,
        augen: T.Tuple[int, int, int],
        aus_der_hand: bool = True,
    ) -> WurfEvaluierung:
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

        return WurfEvaluierung(
            priorität(wurf),
            wurf_anzahl=len(bestehende_würfe),
            reihenfolge=spieler_idx,
            spieler=self._spieler[spieler_idx],
            wurf=wurf,
        )

    def hoch_und_tief(self) -> T.Tuple[WurfEvaluierung, WurfEvaluierung]:
        erster_spieler = self._spieler_namen[0]
        if not self._würfe[erster_spieler]:
            raise KeineWürfeVorhanden()

        evaluierungen = []
        for idx, spieler in enumerate(self._spieler):
            bestehende_würfe = self._würfe[spieler.name]
            if not bestehende_würfe:
                break
            letzter_wurf = bestehende_würfe[-1]
            evaluierung = WurfEvaluierung(
                priorität=priorität(letzter_wurf),
                wurf_anzahl=len(bestehende_würfe),
                reihenfolge=idx,
                spieler=spieler,
                wurf=letzter_wurf,
            )
            evaluierungen.append(evaluierung)
        evaluierungen.sort()  # hoch: index 0, tief: index -1
        return evaluierungen[0], evaluierungen[-1]

    @property
    def num_maximale_würfe(self):
        if self._aktueller_spieler_idx == 0:
            return 3
        else:
            start_spieler_name = self._spieler_namen[0]
            würfe_start_spieler = self._würfe[start_spieler_name]
            num_würfe_start_spieler = len(würfe_start_spieler)
            return num_würfe_start_spieler
