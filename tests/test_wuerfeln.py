import pytest

from schocken.schockenrunde import Einwerfen, SchockenRunde
from schocken.spieler import Spieler
from schocken.exceptions import FalscheAktion, FalscherSpieler

from schocken import wuerfel

runde = SchockenRunde()
assert runde.leaf_state.name == "einwerfen"
# Testspieler
spieler_1 = Spieler("spieler_1")
spieler_2 = Spieler("spieler_2")
spieler_3 = Spieler("spieler_3")
spieler_4 = Spieler("spieler_4")

# Übergang von Einwerfen nach Halbzeit
runde = SchockenRunde()
assert runde.leaf_state.name == "einwerfen"
wuerfel.werfen = lambda n: (2,) * n
runde.command_to_event(spieler_1.name, "einwerfen")
wuerfel.werfen = lambda n: (3,) * n
runde.command_to_event(spieler_2.name, "einwerfen")
wuerfel.werfen = lambda n: (2,) * n
runde.command_to_event(spieler_3.name, "einwerfen")

wuerfel.werfen = lambda n: (6,) * n
runde.command_to_event(spieler_1.name, "stechen")

wuerfel.werfen = lambda n: (5,) * n
runde.command_to_event(spieler_3.name, "stechen")

runde.command_to_event(spieler_3.name, "wuerfeln")

runde.command_to_event(spieler_3.name, "weiter")

runde.command_to_event(spieler_1.name, "wuerfeln")
