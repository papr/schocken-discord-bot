class Spieler:
    def __init__(self, name):
        self.name = name
        self.deckel = 0
        self.beiseite_gelegt = False
        self.einsen = 0
        self.augen = (None, None, None)
        self.anzahl_wuerfe = 0

    def __str__(self):
        return f"Spieler {self.name}\n\tDeckel: {self.deckel}\n\tAugen: {self.augen}\n"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, Spieler):
            return self.name == other.name
        return NotImplemented
