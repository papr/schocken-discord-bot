import typing as T
import pysm
import threading
from . import events, wuerfel
from .deckel_management import RundenDeckelManagement, SpielzeitStatus
from .exceptions import (
    DuHastMistGebaut,
    FalscheAktion,
    FalscherSpieler,
    ZuOftGeworfen,
    NochNichtGeworfen,
    RundeVorbei,
    LustWurf,
)
from .spieler import Spieler


class Einwerfen(pysm.StateMachine):
    def __init__(self):
        super().__init__("Einwerfen")
        self.init_sm()
        self.spieler_liste = []
        self.stecher_count = 0
        self.stecher_liste = []
        self.gestochen_liste = []

    def init_sm(self):
        idle = pysm.State("einwerfen")
        stechen = pysm.State("stechen")

        self.add_state(idle, initial=True)
        self.add_state(stechen)

        idle.handlers = {
            "einwerfen": self.einwurf_handler,
            "wuerfeln": self.wuerfeln_handler,
            "exit": self.spieler_liste_fixieren,
        }

        stechen.handlers = {
            "stechen": self.stechen_handler,
            "einwerfen": self.raise_falsche_aktion,
            "wuerfeln": self.wuerfeln_handler,
            "exit": self.spieler_liste_fixieren,
        }

        self.add_transition(
            idle,
            stechen,
            events=["stechen"],
            condition=self.stechen_possible,
            after=self.stechen_handler,
        )

        self.initialize()

    def einwurf_handler(self, state, event):
        """Called when event "einwerfen" is dispatched"""
        spieler_name = event.cargo["spieler_name"]
        if spieler_name in [sp.name for sp in self.spieler_liste]:
            raise FalscherSpieler

        spieler = Spieler(spieler_name)
        einwurf = wuerfel.werfen(1)

        spieler.augen = einwurf
        self.spieler_liste.append(spieler)

        roll_list = [sp.augen[0] for sp in self.spieler_liste]

        self.stecher_liste = [
            sp for sp in self.spieler_liste if sp.augen[0] == min(roll_list)
        ]
        self.stecher_count = len(self.stecher_liste)

    def stechen_handler(self, state, event):
        spieler_name = event.cargo["spieler_name"]
        if len(self.gestochen_liste) == 0:
            self._init_stecher_count = len(self.stecher_liste)

        # check if already gestochen
        if spieler_name in [pl.name for pl in self.gestochen_liste]:
            raise FalscherSpieler

        # check if eligible
        if spieler_name not in [st.name for st in self.stecher_liste]:
            raise FalscherSpieler

        stich = wuerfel.werfen(1)
        stecher = [sp for sp in self.spieler_liste if sp.name == spieler_name][0]
        stecher.augen = stich

        self.gestochen_liste.append(stecher)
        # if all stiche done, determine starting player or stech again
        if len(self.gestochen_liste) == self._init_stecher_count:
            stich_list = [st.augen[0] for st in self.gestochen_liste]
            self.stecher_liste = [
                sp for sp in self.gestochen_liste if sp.augen[0] == min(stich_list)
            ]
            self.gestochen_liste = []
            # sort stecher by stich
        elif len(self.gestochen_liste) < self._init_stecher_count:
            pass

        self.stecher_count = len(self.stecher_liste)

    def wuerfeln_handler(self, state, event):
        spieler_name = event.cargo["spieler_name"]
        if not self.wuerfeln_possible():
            raise FalscheAktion
        elif spieler_name != self.stecher_liste[0].name:
            raise FalscherSpieler(f"Nur {self.stecher_liste[0].name} darf anfangen!")

    def raise_falsche_aktion(self, state, event):
        raise FalscheAktion

    def stechen_possible(self, state, event):
        if len(self.spieler_liste) > 1 and self.stecher_count > 1:
            return True
        else:
            raise FalscheAktion("Stechen geht gerade nicht")

    def wuerfeln_possible(self):
        return len(self.spieler_liste) > 1 and self.stecher_count <= 1

    def sortierte_spieler_liste(self):
        try:
            return self.spieler_liste_fixiert
        except AttributeError as err:
            raise DuHastMistGebaut("Einwerfen war noch nicht vorbei!") from err

    def spieler_liste_fixieren(self, state, event):
        spieler_liste = self.spieler_liste
        if self.state.name == "stechen":
            # rotate spieler_liste according to lowest stecher
            spieler = self.stecher_liste[0]
            idx = self.spieler_liste.index(spieler)
            spieler_liste = spieler_liste[idx:] + spieler_liste[:idx]
        else:
            # rotate spieler_liste such that lowest roll is first element
            roll_list = [sp.augen for sp in spieler_liste]
            min_roll = min(roll_list)
            min_index = roll_list.index(min_roll)
            spieler_liste = spieler_liste[min_index:] + spieler_liste[:min_index]
        self.spieler_liste_fixiert = spieler_liste


class Halbzeit(pysm.StateMachine):
    def __init__(self):
        super().__init__("Halbzeit")
        self.verlierende = None
        self.spielzeit_status = None
        self.rdm = None
        self.letzter_wurf = (None, None, None)

        self.handlers = {"enter": self.enter, "kein_finale": self.kein_finale}

        wuerfeln = pysm.State("wuerfeln")
        wuerfeln.handlers = {
            "wuerfeln": self.wuerfeln_handler,
            "beiseite legen": self.beiseite_legen_handler,
            "weiter": self.naechster_spieler_handler,
            "umdrehen": self.sechsen_handler,
        }
        self.add_state(wuerfeln, initial=True)

        self.initialize()

    def enter(self, state, event):
        num_halbzeit = [
            x for x in self.parent.state_stack.deque if x.name == "Halbzeit"
        ]
        if len(num_halbzeit) > 1:
            verlierende_1 = self.root_machine.halbzeit_erste.verlierende
            verlierende_2 = self.root_machine.halbzeit_zweite.verlierende
            spieler_liste = [verlierende_2, verlierende_1]
        else:
            vorheriger_state = self.root_machine.state_stack.peek()
            spieler_liste = vorheriger_state.sortierte_spieler_liste()
            self.initiale_spieler = spieler_liste.copy()

        self._spielerinnen_unique = set(s.name for s in spieler_liste)
        for s in spieler_liste:
            s.deckel = 0
        self.spielzeit_status = SpielzeitStatus(15, spieler_liste)
        self.rdm = RundenDeckelManagement(self.spielzeit_status)

    def kein_finale(self, state, event):
        if len(self._spielerinnen_unique) == 1:
            self.root_machine.dispatch(pysm.Event(events.FERTIG_HALBZEIT))

    @property
    def spieler_liste(self) -> T.List[Spieler]:
        return self.spielzeit_status.spieler

    @property
    def aktiver_spieler(self) -> T.Optional[Spieler]:
        return self.rdm.aktiver_spieler if self.rdm else None

    def sortierte_spieler_liste(self):
        if not self.verlierende:
            raise DuHastMistGebaut("Es gibt noch keinen definierten Startspieler")
        for idx, spieler in enumerate(self.initiale_spieler):
            if spieler.name == self.verlierende.name:
                break
        else:
            raise DuHastMistGebaut(
                f"Der/die Verlierende `{self.verlierende.name}`)` spielt gar nicht "
                f"mit! Mitspielende: {self.initiale_spieler}"
            )
        sotiert = self.initiale_spieler[idx:] + self.initiale_spieler[:idx]
        return sotiert

    def wuerfeln_handler(self, state, event):
        lust_wurf_geworfen = False
        akt_spieler = self.aktiver_spieler
        spieler_name = event.cargo["spieler_name"]

        if spieler_name != akt_spieler.name:
            raise FalscherSpieler(
                f"{spieler_name} wollte würfeln, {akt_spieler.name} ist aber dran!"
            )

        if akt_spieler.anzahl_wuerfe < self.rdm.num_maximale_wuerfe:
            # check if ones were put aside
            if akt_spieler.einsen > 0:
                wurf = wuerfel.werfen(3 - akt_spieler.einsen)
                akt_spieler.augen = (1,) * akt_spieler.einsen + wurf
                akt_spieler.anzahl_wuerfe += 1
                akt_spieler.beiseite_gelegt = False
                aus_der_hand = False
            else:
                akt_spieler.augen = wuerfel.werfen(3)
                akt_spieler.anzahl_wuerfe += 1
                aus_der_hand = True
            letzter_wurf = self.rdm.wurf(spieler_name, akt_spieler.augen, aus_der_hand)
            if self.rdm.ist_lust_wurf(letzter_wurf):
                self.rdm.strafdeckel_verteilen(letzter_wurf.spieler)
                lust_wurf_geworfen = True
        else:
            # watch for semantics
            num_wurf = self.rdm.num_maximale_wuerfe
            plural_switch = "Wurf ist" if num_wurf == 1 else "Würfe sind"
            zahl_zu_wort = {1: "ein", 2: "zwei", 3: "drei"}
            meldung = (
                f"Maximal {zahl_zu_wort[num_wurf]} {plural_switch} erlaubt, "
                f"{akt_spieler.name}!"
            )
            raise ZuOftGeworfen(meldung)

        if akt_spieler.anzahl_wuerfe == self.rdm.num_maximale_wuerfe:
            self.weiter(akt_spieler)

        if lust_wurf_geworfen:
            raise LustWurf(letzter_wurf)

    def beiseite_legen_handler(self, state, event):
        akt_spieler = self.aktiver_spieler
        spieler_name = event.cargo["spieler_name"]

        if spieler_name != akt_spieler.name:
            raise FalscherSpieler(
                f"Das kannst du zur Zeit nicht tun, {spieler_name}. "
                f"{akt_spieler.name} ist an der Reihe!"
            )

        if akt_spieler.beiseite_gelegt:
            raise FalscheAktion(f"Du hast bereits beiseite gelegt!")
        elif not akt_spieler.beiseite_gelegt and 1 in akt_spieler.augen:
            akt_spieler.einsen += akt_spieler.augen.count(1) - akt_spieler.einsen
            akt_spieler.beiseite_gelegt = True
        else:
            raise FalscheAktion(
                f"Du hast keine Einsen gewürfelt die du zur Seite legen kannst!"
            )

    def naechster_spieler_handler(self, state, event):
        akt_spieler = self.aktiver_spieler
        spieler_name = event.cargo["spieler_name"]

        if spieler_name != akt_spieler.name:
            raise FalscherSpieler(
                f"Das kannst du zur Zeit nicht tun, {spieler_name}. "
                f"{akt_spieler.name} ist an der Reihe!"
            )

        if akt_spieler.anzahl_wuerfe == 0:
            raise NochNichtGeworfen("Es muss mindestens ein Mal gewürfelt werden!")
        else:
            self.weiter(akt_spieler)

    def sechsen_handler(self, state, event):
        akt_spieler = self.aktiver_spieler
        spieler_name = event.cargo["spieler_name"]

        if spieler_name != akt_spieler.name:
            raise FalscherSpieler(
                f"Das kannst du zur Zeit nicht tun, {spieler_name}. "
                f"{akt_spieler.name} ist an der Reihe!"
            )

        if 6 not in akt_spieler.augen:
            raise FalscheAktion("Du hast keine Sechsen zum Umdrehen!")
        elif akt_spieler.augen.count(6) == 1:
            raise FalscheAktion("Du hast nur eine Sechs gewürfelt!")
        elif akt_spieler.beiseite_gelegt:
            raise FalscheAktion(
                f"Du hast bereits deine Sechsen zu einer Eins umgewandelt!"
            )
        else:
            akt_spieler.einsen += 1
            akt_spieler.beiseite_gelegt = True

    def beendet(self):
        return len(self.spieler_liste) == 1

    def weiter(self, spieler):
        spieler.anzahl_wuerfe = 0
        spieler.einsen = 0
        try:
            self.rdm.weiter()
        except RundeVorbei:
            self.spielzeit_status = self.rdm.deckel_verteilen_restliche_spieler()
            if self.beendet():
                self.verlierende = self.spielzeit_status.spieler[0]
                self.root_machine.dispatch(pysm.Event(events.FERTIG_HALBZEIT))
            else:
                self.rdm = RundenDeckelManagement(self.spielzeit_status)


class SchockenSpiel(pysm.StateMachine):
    def __init__(self):
        super().__init__("SchockenSpiel")
        self.einwerfen = Einwerfen()
        self.halbzeit_erste = Halbzeit()
        self.halbzeit_zweite = Halbzeit()
        self.finale = Halbzeit()
        anstoßen = pysm.StateMachine("anstoßen!")

        # add states to machine
        self.add_state(self.einwerfen, initial=True)
        self.add_state(self.halbzeit_erste)
        self.add_state(self.halbzeit_zweite)
        self.add_state(self.finale)
        self.add_state(anstoßen)

        self.add_transition(
            self.einwerfen,
            self.halbzeit_erste,
            events=[events.WÜRFELN],
            after=self.halbzeit_erste.wuerfeln_handler,
        )

        self.add_transition(
            self.halbzeit_erste, self.halbzeit_zweite, events=[events.FERTIG_HALBZEIT],
        )
        self.add_transition(
            self.halbzeit_zweite,
            self.finale,
            events=[events.FERTIG_HALBZEIT],
            after=self.finale.kein_finale,
        )
        self.add_transition(
            self.finale, anstoßen, events=[events.FERTIG_HALBZEIT], after=self.anstoßen,
        )
        self.initialize()

    def command_to_event(self, spieler_name, command):
        # please stick to the convention that event identifiers are the same
        # as the command strings
        if command == "einwerfen":
            event = pysm.Event("einwerfen", spieler_name=spieler_name)
        elif command == "wuerfeln":
            event = pysm.Event("wuerfeln", spieler_name=spieler_name)
        elif command == "stechen":
            event = pysm.Event("stechen", spieler_name=spieler_name)
        elif command == "weiter":
            event = pysm.Event("weiter", spieler_name=spieler_name)
        elif command == "beiseite legen":
            event = pysm.Event("beiseite legen", spieler_name=spieler_name)
        elif command == "umdrehen":
            event = pysm.Event("umdrehen", spieler_name=spieler_name)
        else:
            raise FalscheAktion
        self.dispatch(event)

    def anstoßen(self, state, event):
        print("PROST!")
