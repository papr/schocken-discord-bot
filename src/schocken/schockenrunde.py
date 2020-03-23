from random import randrange
from .wuerfel import werfen
from .spieler import Spieler
from .deckel_management import RundenDeckelManagement, DeckelManagement, FalscherSpieler
from .exceptions import FalscheAktion, FalscherSpielBefehl


class SchockenRunde:
    def __init__(self):
        self.state = "Einwerfen"
        self.zulaessige_befehle = ["einwerfen"]
        self.spieler_liste = []
        self.aktiver_spieler = None
        self._wuerfeln_possible = False
        self._stechen_possible = False
        self.letzter_wurf = [None, None, None]
        self.anzahl_wuerfe = 3

    def _spieler_from_name(self, name):
        # TODO hier weiter
        print("_spieler_from_name called")
        print("liste: ", self.spieler_liste)
        return [sp for sp in self.spieler_liste if sp.name == name][0]

    def perform_action(self, player, command):
        state_0 = self.state
        if state_0 == "Einwerfen":
            self.einwerfen(player,command)
        elif state_0  == "Stechen":
            return self.stechen(player, command)
        elif state_0  == "Runde":
            return self.wuerfeln(player, command)

        if self.state != state_0:
            self.perform_action(player, command)

    def einwerfen(self, player, command):
        if command == "einwerfen":
            name = player
            schon_eingeworfen = [sp.name for sp in self.spieler_liste]
            if name in schon_eingeworfen:
                raise FalscherSpieler
            spieler = Spieler(name)
            einwurf = werfen(1)[0]
            # einwurf = 1  # placeholder
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
            self.stecher_liste = [
                sp for sp in self.spieler_liste if sp.augen == min_roll
            ]
            stecher_count = len(self.stecher_liste)
            self._gestochen_liste = []

            # output
            self.letzter_wurf = einwurf
            # out_str = f"{spieler.name} hat mit einer {self.emoji_names[einwurf]} eingeworfen.\n"
            if len(self.spieler_liste) > 1:
                if stecher_count == 1:
                    # out_str += f"{self.spieler_liste[0].name} hat den niedrigsten Wurf. `!würfeln` um das Spiel zu beginnen."
                    self.zulaessige_befehle = ["einwerfen", "würfeln"]
                    self._wuerfeln_possible = True
                    self._stechen_possible = False
                    self.aktiver_spieler = self.stecher_liste[0]

                elif stecher_count > 1:
                    self.zulaessige_befehle = ["einwerfen", "stechen"]
                    self._wuerfeln_possible = False
                    self._stechen_possible = True
            # else:
            #     raise NichtGenugSpieler

        elif command == "würfeln":
            if not self._wuerfeln_possible:
                raise FalscheAktion
            first_player_name = self.spieler_liste[0].name
            if player != first_player_name:
                raise FalscherSpieler
            self.state = "Runde"
            # self.wuerfeln(player, command)

        elif command == "stechen":
            # if not self._stechen_possible:
            # raise FalscheAktion
            # self.state = "Stechen"
            self.stechen(player, command)

    def stechen(self, player, command):
        self.zulaessige_befehle = ["stechen", "würfeln"]
        # no stiche yet, init how many stiche are expected:
        if len(self._gestochen_liste) == 0:
            self._init_stecher_count = len(self.stecher_liste)

        # check if already gestochen
        if player in [pl.name for pl in self._gestochen_liste]:
            raise FalscherSpieler
        # check if eligible
        if player not in [st.name for st in self.stecher_liste]:
            raise FalscherSpieler

        stich = werfen(1)[0]
        self.letzter_wurf = stich
        stecher = self._spieler_from_name(player)
        stecher.augen = stich

        self._gestochen_liste.append(stecher)
        self.stecher_liste = [
            st for st in self.stecher_liste if st not in self._gestochen_liste
        ]

        # if all stiche done, determine starting player or stech again
        if len(self._gestochen_liste) == self._init_stecher_count:
            stich_list = [st.augen for st in self._gestochen_liste]
            min_stich = min(stich_list)
            self.stecher_liste = [
                sp for sp in self._gestochen_liste if sp.augen == min_stich
            ]

            min_index = stich_list.index(min_stich)
            self.aktiver_spieler = self.spieler_liste[min_index]
            self.state = "Runde"
            # sort stecher by stich
        elif len(self._gestochen_liste) < self._init_stecher_count:
            pass

        # if len(self._schon_gestochen) == 1:
        # if
        # out_str = f"{stecher} hat mit  gestochen"

    def wuerfeln(self, player, command):
        RDM = RundenDeckelManagement(15, self.spieler_liste)
        # erster Wurf (immer 3 Würfel)
        if self.aktiver_spieler.anzahl_wuerfe == 0:
            self.letzter_wurf = werfen(3)
            RDM.wurf(self.aktiver_spieler.name, self.letzter_wurf, aus_der_hand=True)
            self.aktiver_spieler.anzahl_wuerfe += 1
        else:
            raise ZuOftGeworfen(
                f"Maximal 3 Würfe sind erlaubt, {self.aktiver_spieler.name}!"
            )

    # def parse_input(self, message):
    # command = message.content.split("!")[-1]
    # if command not in self.zulaessige_befehle[self.state]:
    # return (
    # "Kein zulässiger Befehl während "
    # + self.state
    # + ": "
    # + command
    # + "\n Zulässige Befehle: "
    # + ", ".join(self.zulaessige_befehle[self.state])
    # )
    # else:
    # self.message = message
    # return self.run()
