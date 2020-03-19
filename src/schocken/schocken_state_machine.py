# from statemachine import StateMachine, State

# class SchockenRunde(StateMachine):
    # einwerfen = State("Einwerfen", initial = True)
    # halbzeit = State("Halbzeit")
    # # runde = State("Runde")

    # eingeworfen = einwerfen.to(halbzeit)

    # def on_enter_halbzeit(self):
        

# game = SchockenRunde()
# SchockenRunde.current_state
from random import randrange
class SchockenRunde():
    def __init__(self):
        self.state = "Einwerfen"
        self.zulaessige_befehle = {"Einwerfen": ["einwerfen", "weiter"]}
        self.spieler_liste = []

    def run(self):
        if self.state == "Einwerfen":
            return self.einwerfen()

    def einwerfen(self):
        command = self.message.content.split("!")[-1]
        if command == "einwerfen":
            name = self.message.author.name
            spieler = Spieler(name)
            einwurf = randrange(1,7)
            spieler.einwurf = einwurf
            self.spieler_liste.append(Spieler(name))
            return str(einwurf) 
        elif command == "weiter":
            einwuerfe = [sp.einwurf for sp in self.spieler_liste]
            # implement logic if more than one player has the same lowest roll
            self.spieler_liste = sorted(self.spieler_liste, lambda sp: sp.einwurf)
            self.state = "Halbzeit"

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


class Spieler():
    def __init__(self, name):
        self.name = name
        self.deckel = 0

class Author():
    def __init__(self, name):
        self.name = name

class Message():
    def __init__(self, name):
        self.content = "!einwerfen"
        self.author = Author(name)

if __name__ == "__main__":
    runde = SchockenRunde()
    message = Message("Andre") 
    print(runde.parse_input(message))
    message2 = Message("Jasmin")
    print(runde.parse_input(message))
