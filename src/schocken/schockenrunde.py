from random import randrange
from .wuerfel import werfen
from .spieler import Spieler
from .deckel_management import DeckelManagement, FalscherSpieler


class FalscheAktion(ValueError):
    pass

class SchockenRunde:
    def __init__(self):
        self.state = "Einwerfen"
        self.zulaessige_befehle = {"Einwerfen": ["einwerfen", "würfeln", "stechen"], "Runde": ["würfeln"]}
        self.spieler_liste = []
        self.aktiver_spieler = 0

    def run(self):
        if self.state == "Einwerfen":
            return self.einwerfen()
        elif self.state == "Runde":
            return self.wuerfeln()

    def einwerfen(self):
        command = self.message.content.split("!")[-1]
        if command == "einwerfen":
            name = self.message.author.name
            schon_eingeworfen = [sp.name for sp in self.spieler_liste] 
            if name in schon_eingeworfen:
                raise FalscherSpieler
            spieler = Spieler(name)
            einwurf = werfen(1)[0]
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
            min_roll_players = [
                sp for sp in self.spieler_liste if sp.einwurf == min_roll
            ]
            self._stecher_liste = min_roll_players
            count = len(min_roll_players)

            # output
            out_str = f"{spieler.name} hat mit einer {einwurf} eingeworfen.\n"
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

        elif command == "stechen":
            if not self._stechen_possible:
                raise FalscheAktion
            if self.message.author.name not in self._stecher_liste:
                raise FalscherSpieler                      

    def stechen(self):
        pass

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

    def beiseite_legen(self, augen)

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
