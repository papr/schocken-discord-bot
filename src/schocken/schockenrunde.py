from pysm import StateMachine, State, Event
from .spieler import Spieler
from . import wuerfel
from .exceptions import FalscheAktion, FalscherSpieler, ZuOftGeworfen
from .deckel_management import RundenDeckelManagement, SpielzeitStatus


class Einwerfen(object):
    def __init__(self):
        self.sm = self.init_sm()
        self.spieler_liste = []
        self.stecher_count = 0
        self.stecher_liste = []
        self.gestochen_liste = []

    def init_sm(self):
        sm = StateMachine("Einwerfen")
        idle = State("einwerfen")
        stechen = State("stechen")

        sm.add_state(idle, initial=True)
        sm.add_state(stechen)

        idle.handlers = {
            "exit": self.idle_on_exit,
            "einwerfen": self.einwurf_handler,
            "wuerfeln": self.wuerfeln_handler,
        }

        stechen.handlers = {
            "stechen": self.stechen_handler,
            "einwerfen": self.raise_falsche_aktion,
            "wuerfeln": self.wuerfeln_handler,
        }

        sm.add_transition(
            idle,
            stechen,
            events=["stechen"],
            action=None,
            condition=self.stechen_possible,
            before=None,
            after=self.stechen_handler,
        )

        sm.initialize()
        return sm

    def einwurf_handler(self, state, event):
        """Called when event "einwerfen" is dispatched"""
        spieler_name = event.cargo["spieler_name"]
        if spieler_name in [sp.name for sp in self.spieler_liste]:
            raise FalscherSpieler

        spieler = Spieler(spieler_name)
        einwurf = wuerfel.werfen(1)[0]

        spieler.augen = einwurf
        self.spieler_liste.append(spieler)

        roll_list = [sp.augen for sp in self.spieler_liste]

        self.stecher_liste = [
            sp for sp in self.spieler_liste if sp.augen == min(roll_list)
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

        stich = wuerfel.werfen(1)[0]
        stecher = [sp for sp in self.spieler_liste if sp.name == spieler_name][0]
        stecher.augen = stich

        self.gestochen_liste.append(stecher)
        # if all stiche done, determine starting player or stech again
        if len(self.gestochen_liste) == self._init_stecher_count:
            stich_list = [st.augen for st in self.gestochen_liste]
            self.stecher_liste = [
                sp for sp in self.gestochen_liste if sp.augen == min(stich_list)
            ]
            self.gestochen_liste = []
            # sort stecher by stich
        elif len(self.gestochen_liste) < self._init_stecher_count:
            pass

        self.stecher_count = len(self.stecher_liste)

    def wuerfeln_handler(self, state, event):
        spieler_name = event.cargo["spieler_name"]
        if not self.wuerfeln_possible(state, event):
            raise FalscheAktion
        elif spieler_name != self.stecher_liste[0].name:
            raise FalscherSpieler

    def raise_falsche_aktion(self, state, event):
        raise FalscheAktion

    def idle_on_exit(self, state, event):
        pass

    def stechen_possible(self, state, event):
        if len(self.spieler_liste) > 1 and self.stecher_count > 1:
            return True
        else:
            raise FalscheAktion

    def wuerfeln_possible(self, state, event):
        if self.state == "stechen":
            # rotate spieler_liste according to lowest stecher
            spieler = self.stecher_liste[0]
            idx = self.spieler_liste.index(spieler)
            self.spieler_liste = self.spieler_liste[idx:] + self.spieler_liste[:idx]
        else:
            # rotate spieler_liste such that lowest roll is first element
            roll_list = [sp.augen for sp in self.spieler_liste]
            min_roll = min(roll_list)
            min_index = roll_list.index(min_roll)
            self.spieler_liste = (
                self.spieler_liste[min_index:] + self.spieler_liste[:min_index]
            )
        return len(self.spieler_liste) > 1 and self.stecher_count == 1

    @property
    def state(self):
        return self.sm.leaf_state.name


class Halbzeit(object):
    def __init__(self):
        self.sm = self.init_sm()
        self.spieler_liste = []
        self.aktiver_spieler = None
        self.spielzeit_status = None
        self.rdm = None
        self.letzter_wurf = [None, None, None]

    def init_sm(self):
        sm = StateMachine("Halbzeit")
        wuerfeln = State("wuerfeln")

        sm.add_state(wuerfeln, initial=True)

        wuerfeln.handlers = {
            "wuerfeln": self.wuerfeln_handler,
            "beiseite_legen": self.beiseite_legen_handler,
            "weiter": self.naechster_spieler_handler,
        }

        sm.initialize()
        return sm

    def wuerfeln_handler(self, state, event):
        spieler = self.aktiver_spieler
        spieler_name = event.cargo["spieler_name"]

        if spieler_name != spieler.name:
            raise FalscherSpieler(
                f"{spieler_name} hat geworfen, {self.aktiver_spieler.name} war aber dran!"
            )

        # first throw (always 3 dice)
        if spieler.anzahl_wuerfe == 0:
            spieler.augen = wuerfel.werfen(3)
            spieler.anzahl_wuerfe += 1
            self.rdm.wurf(spieler_name, spieler.augen, aus_der_hand=True)
        elif spieler.anzahl_wuerfe < self.rdm.num_maximale_würfe:
            spieler.augen = wuerfel.werfen(3)
            spieler.anzahl_wuerfe += 1
            self.rdm.wurf(spieler_name, spieler.augen, aus_der_hand=True)
        else:
            # AUF SEMANTIK ACHTEN (SPRECHT GUTES DEUTSCH IHR HURENSÖHNE)
            num_wurf = self.rdm.num_maximale_würfe
            plural_switch = "Wurf ist" if num_wurf == 1 else "Würfe sind"
            zahl_zu_wort = {1: "ein", 2: "zwei", 3: "drei"}
            meldung = f"Maximal {zahl_zu_wort[num_wurf]} {plural_switch} erlaubt, {spieler.name}!"
            raise ZuOftGeworfen(meldung)

    def beiseite_legen_handler(self, state, event):
        pass

    def naechster_spieler_handler(self, state, event):
        self.rdm.weiter()
        self.spieler_liste = self.spieler_liste[1:] + self.spieler_liste[:1]
        self.aktiver_spieler = self.spieler_liste[0]

    def beendet(self):
        return len(self.spieler_liste) == 1

    @property
    def state(self):
        return self.sm.leaf_state.name


class SchockenRunde(object):
    def __init__(self):
        self.spieler_liste = []
        self.sm = self._init_sm()

    def _init_sm(self):
        sm = StateMachine("SchockenRunde")

        self.einwerfen = Einwerfen()
        self.halbzeit = Halbzeit()

        # add states to machine
        sm.add_state(self.einwerfen.sm, initial=True)
        sm.add_state(self.halbzeit.sm)

        sm.add_transition(
            self.einwerfen.sm,
            self.halbzeit.sm,
            events=["wuerfeln"],
            action=self.start_halbzeit,
            condition=self.einwerfen.wuerfeln_possible,
            before=self.action_spieler_liste,
            after=self.halbzeit.wuerfeln_handler,
        )

        sm.initialize()
        return sm

    def action_spieler_liste(self, state, event):
        self.spieler_liste = self.einwerfen.spieler_liste

    def start_halbzeit(self, state, event):
        self.halbzeit.spieler_liste = self.spieler_liste
        self.halbzeit.aktiver_spieler = self.spieler_liste[0]
        self.halbzeit.spielzeit_status = SpielzeitStatus(15, self.spieler_liste)
        self.halbzeit.rdm = RundenDeckelManagement(self.halbzeit.spielzeit_status)

    def command_to_event(self, spieler_name, command):
        if command == "einwerfen":
            event = Event("einwerfen", spieler_name=spieler_name)
        elif command == "wuerfeln":
            event = Event("wuerfeln", spieler_name=spieler_name)
        elif command == "stechen":
            event = Event("stechen", spieler_name=spieler_name)
        elif command == "weiter":
            event = Event("weiter", spieler_name=spieler_name)
        elif command == "beiseite legen":
            event = Event("beiseite legen", spieler_name=spieler_name)
        else:
            raise FalscheAktion
        self.sm.dispatch(event)

    @property
    def state(self):
        return self.sm.leaf_state.name
