from random import randrange
from .wuerfel import werfen
from .spieler import Spieler
from .deckel_management import DeckelManagement


class SchockenRunde:
    def __init__(self):
        self.state = "Einwerfen"
        self.zulaessige_befehle = {
            "Einwerfen": ["einwerfen", "weiter"],
            "Runde": ["würfeln"],
        }
        self.spieler_liste = []

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
            self.spieler_liste.append(Spieler(name))
            # find smallest
            return spieler.name + " hat mit einer " + str(einwurf) + " eingeworfen"
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
