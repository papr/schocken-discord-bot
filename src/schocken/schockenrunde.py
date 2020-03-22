from random import randrange
from .wuerfel import werfen
from .spieler import Spieler
from .deckel_management import DeckelManagement, FalscherSpieler
from .exceptions import FalscheAktion, FalscherSpielBefehl


class SchockenRunde:
    def __init__(self):
        self.state = "Einwerfen"
        self.zulaessige_befehle = ["einwerfen"]
        self.spieler_liste = []
        self.aktiver_spieler = 0
        self._wuerfeln_possible = False
        self._stechen_possible = False
        self._letzter_wurf = [None, None, None]
        self._anzahl_wuerfe = 3

    def _spieler_from_name(self, name):
        # TODO hier weiter
        print("_spieler_from_name called")
        print("liste: ", self.spieler_liste)
        return [sp for sp in self.spieler_liste if sp.name == name][0]

    def perform_action(self, player, command):
        print(
            f"perform_action called with args {player}, {command} with state={self.state}"
        )
        if self.state == "Einwerfen":
            return self.einwerfen(player, command)
        elif self.state == "Stechen":
            return self.stechen(player, command)
        elif self.state == "Runde":
            return self.wuerfeln()

    def einwerfen(self, player, command):
        if command == "einwerfen":
            self.zulaessige_befehle = ["einwerfen"]
            name = player
            schon_eingeworfen = [sp.name for sp in self.spieler_liste]
            if name in schon_eingeworfen:
                raise FalscherSpieler
            spieler = Spieler(name)
            # einwurf = werfen(1)[0]
            einwurf = 1
            spieler.einwurf = einwurf
            self.spieler_liste.append(spieler)
            # find smallest roll
            roll_list = [sp.einwurf for sp in self.spieler_liste]
            min_roll = min(roll_list)
            min_index = roll_list.index(min_roll)
            # rotate list such that lowest roll is first element
            self.spieler_liste = (
                self.spieler_liste[min_index:] + self.spieler_liste[:min_index]
            )
            # check if lowest roll only occurs once
            self.stecher_liste = [
                sp for sp in self.spieler_liste if sp.einwurf == min_roll
            ]
            stecher_count = len(self.stecher_liste)
            self._gestochen_liste = []

            # output
            self.last_roll = einwurf
            # out_str = f"{spieler.name} hat mit einer {self.emoji_names[einwurf]} eingeworfen.\n"
            if len(self.spieler_liste) > 1:
                if stecher_count == 1:
                    # out_str += f"{self.spieler_liste[0].name} hat den niedrigsten Wurf. `!würfeln` um das Spiel zu beginnen."
                    self._wuerfeln_possible = True
                    self._stechen_possible = False

                elif stecher_count > 1:
                    self.zulaessige_befehle = ["einwerfen", "stechen"]
                    self._wuerfeln_possible = False
                    self._stechen_possible = True

        elif command == "würfeln":
            out_str = ""
            if not self._wuerfeln_possible:
                raise FalscheAktion
            first_player_name = self.spieler_liste[0].name
            if player != first_player_name:
                raise FalscherSpieler

            raise NotImplementedError

        elif command == "stechen":
            # if not self._stechen_possible:
            # raise FalscheAktion
            self.state = "Stechen"
            self.stechen(player, command)

    def stechen(self, player, command):
        self.zulaessige_befehle = ["stechen"]
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
        stecher = self._spieler_from_name(player)
        stecher.stich = stich

        self._gestochen_liste.append(stecher)
        self.stecher_liste = [
            st for st in self.stecher_liste if st not in self._gestochen_liste
        ]

        # if all stiche done, determine starting player or stech again
        if len(self._gestochen_liste) == self._init_stecher_count:
            stich_list = [st.stich for st in self._gestochen_liste]
            min_stich = min(stich_list)
            self.stecher_liste = [
                sp for sp in self._gestochen_liste if sp.stich == min_stich
            ]

            min_index = stich_list.index(min_stich)
            # sort stecher by stich
        elif len(self._gestochen_liste) < self._init_stecher_count:
            pass

        # if len(self._schon_gestochen) == 1:
        # if
        # out_str = f"{stecher} hat mit  gestochen"

    def wuerfeln(self, player, command):
        RDM = RundenDeckelManagement(15, self.spieler_liste)
        command = self.message.content.split("!")[-1]
        zuruecklegen = []
        if command == "würfeln":
            # erster Wurf (immer 3 Würfel)
            if self.aktiver_spieler.anzahl_wuerfe == 0:
                augen = werfen(3)
                RDM.wurf(self.aktiver_spieler.name, augen, aus_der_hand=True)
                self.aktiver_spieler.anzahl_wuerfe += 1
                print(str(RDM.num_maximale_würfe))
                return str(augen)
            else:
                raise ZuOftGeworfen(
                    f"Maximal 3 Würfe sind erlaubt, {self.aktiver_spieler.name}!"
                )

        elif command == "weiter":
            self.message = message
            return self.run()

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
