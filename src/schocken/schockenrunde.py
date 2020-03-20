from random import randrange
from .wuerfel import werfen
from .spieler import Spieler
from .deckel_management import DeckelManagement


class SchockenRunde:
    def __init__(self):
        self.state = "Einwerfen"
        self.zulaessige_befehle = {"Einwerfen": ["einwerfen"], "Runde": ["würfeln"]}
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
            count = len(min_roll_players)

            # output
            out_str = f"{spieler.name} hat mit einer {einwurf} eingeworfen.\n"
            if len(self.spieler_liste) == 1:
                return out_str.rstrip("\n")
            elif count == 1:
                out_str += f"{self.spieler_liste[0].name} hat den niedrigsten Wurf. `!würfeln` um das Spiel zu beginnen."
                self.zulaessige_befehle.update({"einwerfen": ["einwerfen", "würfeln"]})
            elif count > 1:
                out_str += (
                    ", ".join([pl.name for pl in min_roll_players])
                    + " haben eine "
                    + str(min_roll)
                    + " geworfen\n"
                )
                out_str += "`!stechen` um zu stechen"
                self.zulaessige_befehle.update({"einwerfen": ["einwerfen", "stechen"]})
            return out_str

        elif command == "weiter":
            einwuerfe = [sp.einwurf for sp in self.spieler_liste]
            # implement logic if more than one player has the same lowest roll
            self.spieler_liste = sorted(self.spieler_liste, key=lambda sp: sp.einwurf)
            print("Erster Mitspieler: " + self.spieler_liste[0].name)
            self.state = "Runde"
            return "Now in state: " + str(self.state)

    def wuerfeln(self):
        command = self.message.content.split("!")[-1]
        if command == "würfeln":
            name = self.message.author.name
            spieler = Spieler(name)
            print("wurf..")
            wurf = werfen(3)
            print("wurf" + str(wurf))
            return str(wurf)
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
