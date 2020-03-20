from random import randrange
from wuerfel import werfen3W, werfen2W, werfen1W
from spieler import Spieler

class SchockenRunde():
    def __init__(self):
        self.state = "Einwerfen"
        self.zulaessige_befehle = {"Einwerfen": ["einwerfen", "weiter"], "Runde": ["würfeln"]}
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
            einwurf = werfen1W()[0]
            spieler.einwurf = einwurf
            self.spieler_liste.append(Spieler(name))
            return spieler.name + " hatt mit einer " + str(einwurf) + " eingeworfen"
        elif command == "weiter":
            einwuerfe = [sp.einwurf for sp in self.spieler_liste]
            # implement logic if more than one player has the same lowest roll
            self.spieler_liste = sorted(self.spieler_liste, key=lambda sp:sp.einwurf)
            print("Erster Mitspieler: " + self.spieler_liste[0].name)
            self.state = "Runde"
            return "Now in state: " + str(self.state)

    def wuerfeln(self):
        command = self.message.content.split("!")[-1]
        if command == "würfeln":
            name = self.message.author.name
            spieler = Spieler(name)
            print("wurf..")
            wurf = werfen3W()
            print("wurf" + str(wurf))
            return str(wurf) 
        elif command == "weiter":
            self.message = message
            return self.run()

    def parse_input(self, message):
        command = message.content.split("!")[-1]
        if command not in self.zulaessige_befehle[self.state]:
            return "Kein zulässiger Befehl während "+self.state+": "+command+\
                    "\n Zulässige Befehle: "+", ".join(self.zulaessige_befehle[self.state])
        else:
            self.message = message
            return self.run()

class Halbzeit():
    def __init__(self, num):
        self.num = num
        self.anzahl_deckel = 15
    
    # def runde(self, spieler):




if __name__ == "__main__":
    class Author():
        def __init__(self, name):
            self.name = name

    class Einwurf():
        def __init__(self, name):
            self.content = "!einwerfen"
            self.author = Author(name)

    class Wurf():
        def __init__(self, name):
            self.content = "!würfeln"
            self.author = Author(name)

    class Weiter():
        def __init__(self, name):
            self.content = "!weiter"
            self.author = Author(name)

    runde = SchockenRunde()
    message = Einwurf("Andre")
    print(runde.parse_input(message))
    message = Einwurf("Jasmin")
    print(runde.parse_input(message))
    message = Weiter("Andre") 
    print(runde.parse_input(message))
    message = Wurf("Andre")
    print(runde.parse_input(message))
    message = Wurf("Jasmin")
    print(runde.parse_input(message))
