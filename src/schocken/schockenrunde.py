from pysm import StateMachine, State, Event
from .spieler import Spieler
from . import wuerfel
from .exceptions import FalscheAktion, FalscherSpieler
from .deckel_management import RundenDeckelManagement, SpielzeitStatus


class Einwerfen(object):
    def __init__(self):
        self.sm = self.init_sm()
        self.spieler_liste = []
        self.stecher_count = 0
        self.stecher_liste = []
        self._gestochen_liste = []

    def init_sm(self):
        sm = StateMachine("Einwerfen")
        idle = State("einwerfen")
        stechen = State("stechen")
        fertig = State("einwerfen_fertig")

        sm.add_state(idle, initial=True)
        sm.add_state(stechen)
        sm.add_state(fertig)

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

        sm.add_transition(
            idle,
            fertig,
            events=["wuerfeln"],
            action=None,
            condition=self.wuerfeln_possible,
            before=None,
            after=None,
        )

        sm.add_transition(
            stechen,
            fertig,
            events=["wuerfeln"],
            action=None,
            condition=self.wuerfeln_possible,
            before=None,
            after=None,
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
        # find smallest roll
        roll_list = [sp.augen for sp in self.spieler_liste]
        min_roll = min(roll_list)
        min_index = roll_list.index(min_roll)
        # rotate list such that lowest roll is first element
        self.spieler_liste = (
            self.spieler_liste[min_index:] + self.spieler_liste[:min_index]
        )
        # check if lowest roll only occurs once
        self.stecher_liste = [sp for sp in self.spieler_liste if sp.augen == min_roll]
        self.stecher_count = len(self.stecher_liste)
        # print(f"Spieler {spieler_name} wirft mit {spieler.augen} ein.")

    def stechen_handler(self, state, event):
        spieler_name = event.cargo["spieler_name"]
        if len(self._gestochen_liste) == 0:
            self._init_stecher_count = len(self.stecher_liste)

        # check if already gestochen
        if spieler_name in [pl.name for pl in self._gestochen_liste]:
            raise FalscherSpieler

        # check if eligible
        if spieler_name not in [st.name for st in self.stecher_liste]:
            raise FalscherSpieler

        stich = wuerfel.werfen(1)[0]
        stecher = [sp for sp in self.spieler_liste if sp.name == spieler_name][0]
        stecher.augen = stich

        self._gestochen_liste.append(stecher)
        # if all stiche done, determine starting player or stech again
        if len(self._gestochen_liste) == self._init_stecher_count:
            stich_list = [st.augen for st in self._gestochen_liste]
            min_stich = min(stich_list)
            self.stecher_liste = [
                sp for sp in self._gestochen_liste if sp.augen == min_stich
            ]
            min_index = stich_list.index(min_stich)
            self.aktiver_spieler = self.spieler_liste[min_index]
            self._gestochen_liste = []
            # sort stecher by stich
        elif len(self._gestochen_liste) < self._init_stecher_count:
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
        return len(self.spieler_liste) > 1 and self.stecher_count > 1

    def wuerfeln_possible(self, state, event):
        return len(self.spieler_liste) > 1 and self.stecher_count == 1

    @property
    def state(self):
        return self.sm.leaf_state.name


class Halbzeit(object):
    def __init__(self, spieler_liste):
        self.sm = self.init_sm()
        self.spieler_liste = spieler_liste
        self.aktiver_spieler = None
        self.spielzeit_status = SpielzeitStatus(15, spieler_liste)
        self.rdm = RundenDeckelManagement(self.spielzeit_status)

    def init_sm(self):
        sm = StateMachine("Halbzeit")
        wuerfeln = State("wuerfeln")
        fertig = State("halbzeit_fertig")

        sm.add_state(wuerfeln, initial=True)
        sm.add_state(fertig)

        wuerfeln.handlers = {
            "wuerfeln": self.wuerfeln_handler,
            "beiseite_legen": self.beiseite_legen_handler,
            "weiter": self.naechster_spieler_handler,
        }

        sm.add_transition(
            wuerfeln,
            fertig,
            events=["würfeln"],
            action=None,
            condition=self.beendet,
            before=None,
            after=None,
        )

        sm.initialize()
        return sm

    def wuerfeln_handler(self, state, event):
        print(self.spieler_liste)

    def beiseite_legen_handler(self):
        pass

    def naechster_spieler_handler(self):
        pass

    def beendet(self):
        return len(self.spieler_liste == 1)

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

        wuerfeln = State("wuerfeln")

        # add states to machine
        sm.add_state(self.einwerfen.sm, initial=True)
        sm.add_state(wuerfeln)

        sm.add_transition(
            self.einwerfen.sm,
            wuerfeln,
            events=["wuerfeln"],
            action=None,
            condition=self.einwerfen.wuerfeln_possible,
            before=None,
            after=self.action_spieler_liste,
        )

        sm.initialize()
        return sm

    def action_spieler_liste(self, state, event):
        print("entering")
        self.spieler_liste = self.einwerfen.spieler_liste

    def command_to_event(self, spieler_name, command):
        if command == "einwerfen":
            event = Event("einwerfen", spieler_name=spieler_name)
        elif command == "wuerfeln":
            event = Event("wuerfeln", spieler_name=spieler_name)
        elif command == "stechen":
            event = Event("stechen", spieler_name=spieler_name)
        else:
            raise FalscheAktion
        self.sm.dispatch(event)

    @property
    def state(self):
        return self.sm.leaf_state.name
