from random import randrange
from .wuerfel import werfen
from .spieler import Spieler
from .deckel_management import DeckelManagement, FalscherSpieler
from .exceptions import FalscheAktion

class SchockenRunde:
    def __init__(self):
        self.state = "Einwerfen"
        self.zulaessige_befehle = {
            "Einwerfen": ["einwerfen", "würfeln", "stechen"],
            "Runde": ["würfeln"],
            "Stechen": ["stechen"],

        }
        self.spieler_liste = []
        self.aktiver_spieler = 0
        self._wuerfeln_possible = False
        self._stechen_possible = False


    def run(self):
        if self.state == "Einwerfen":
            return self.einwerfen()
        elif self.state == "Runde":
            return self.wuerfeln()
        elif self.state == "Stechen":
            return self.stechen()

    def einwerfen(self):
        command = self.message.content.split("!")[-1]
        if command == "einwerfen":
            name = self.message.author.name
            schon_eingeworfen = [sp.name for sp in self.spieler_liste]
            if name in schon_eingeworfen:
                raise FalscherSpieler
            spieler = Spieler(name)
            # einwurf = werfen(1)[0]
            einwurf = 1
            spieler.einwurf = einwurf
            spieler.msg_author = self.message.author
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
            min_roll_players = [
                sp for sp in self.spieler_liste if sp.einwurf == min_roll
            ]
            self._stecher_liste = [pl for pl in min_roll_players]
            count = len(min_roll_players)

            # output
            out_str = f"{spieler.name} hat mit einer {self.emoji_names[einwurf]} eingeworfen.\n"
            if len(self.spieler_liste) == 1:
                return out_str.rstrip("\n")
            elif count == 1:
                out_str += f"{self.spieler_liste[0].name} hat den niedrigsten Wurf. `!würfeln` um das Spiel zu beginnen."
                self._wuerfeln_possible = True
                self._stechen_possible = False
            elif count > 1:
                out_str += (
                    ", ".join([pl.name for pl in min_roll_players])
                    + " haben eine "
                    + str(min_roll)
                    + " geworfen\n"
                )
                out_str += "`!stechen` um zu stechen"
                self._wuerfeln_possible = False
                self._stechen_possible = True
            return out_str

        elif command == "würfeln":
            out_str = ""
            if not self._wuerfeln_possible:
                raise FalscheAktion
            first_player_name = self.spieler_liste[0].name
            if self.message.author.name != first_player_name:
                raise FalscherSpieler

            raise NotImplementedError

        elif command == "stechen":
            if not self._stechen_possible:
                raise FalscheAktion
            stecher = [pl for pl in self.spieler_liste if pl.name == self.message.author.name][0]
            if stecher not in self._stecher_liste:
                raise FalscherSpieler
            self._gestochen_liste= []
            self.state = "Stechen"
            self.stechen()

    def stechen(self):
        # no stiche yet, init how many stiche are expected:
        if len(self._gestochen_liste) == 0:
            self._init_stecher_count = len(self._stecher_liste)

        stecher = [pl for pl in self.spieler_liste if pl.name == self.message.author.name][0]
        # check if already gestochen
        if stecher in self._gestochen_liste:
            raise FalscherSpieler
        # check if eligible
        if stecher not in self._stecher_liste:
            raise FalscherSpieler

        stich = werfen(1)[0]
        stecher.stich = stich
        self._gestochen_liste.append(stecher)
        self._stecher_liste = [st for st in self._stecher_liste if st not in self._gestochen_liste]

        out_str = f"{stecher.name} hat "
        # if all stiche done, determine starting player or stech again
        if len(self._gestochen_liste) == self._init_stecher_count:
            stich_list = [st.stich for st in self._gestochen_liste]
            min_stich = min(stich_list)
            self._stecher_liste = [
                sp for sp in self._gestochen_liste if sp.stich == min_stich
            ]

            min_index = stich_list.index(min_stich)
            #sort stecher by stich
            
    
        
        # if len(self._schon_gestochen) == 1:
            # if 
            # out_str = f"{stecher} hat mit  gestochen"

    def wuerfeln(self):
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

    def parse_input(self, message):
        command = message.content.split("!")[-1]
        if command not in self.zulaessige_befehle[self.state]:
            return (
                "Kein zulässiger Befehl während "
                + self.state
                + ": "
                + command
                + "\n Zulässige Befehle: "
                + ", ".join(self.zulaessige_befehle[self.state])
            )
        else:
            self.message = message
            return self.run()
