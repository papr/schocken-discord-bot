import pytest

from schocken.schockenrunde import Einwerfen, SchockenRunde
from schocken.spieler import Spieler
from schocken.exceptions import FalscheAktion, FalscherSpieler

from schocken import wuerfel

runde = SchockenRunde()
assert runde.state == "einwerfen"
# testspieler
spieler_1 = Spieler("spieler_1")
spieler_2 = Spieler("spieler_2")
spieler_3 = Spieler("spieler_3")
spieler_4 = Spieler("spieler_4")

# FALL: Zwei Spieler werfen dasselbe ein, einer versucht zu starten
wuerfel.werfen = lambda n: (1,) * n
runde.command_to_event(spieler_1.name, "einwerfen")
runde.command_to_event(spieler_2.name, "einwerfen")

with pytest.raises(FalscheAktion):
    runde.command_to_event(spieler_1.name, "wuerfeln")

# FALL: spieler 2 würfelt eindeutig das niedrigste
runde = SchockenRunde()
assert runde.state == "einwerfen"
wuerfel.werfen = lambda n: (2,) * n
runde.command_to_event(spieler_1.name, "einwerfen")
wuerfel.werfen = lambda n: (1,) * n
runde.command_to_event(spieler_2.name, "einwerfen")
wuerfel.werfen = lambda n: (3,) * n
runde.command_to_event(spieler_3.name, "einwerfen")

# Ist Spieler_2 erster?
spieler_liste = runde.einwerfen.spieler_liste
assert spieler_liste[0].name == "spieler_2"

# Richtige exception, wenn jemand anders anfangen will?
with pytest.raises(FalscherSpieler):
    runde.command_to_event(spieler_1.name, "wuerfeln")

# Richtige exception, wenn jemand stechen will.
with pytest.raises(FalscheAktion):
    runde.command_to_event(spieler_2.name, "stechen")

# momentaner state ist einwerfen
assert runde.state == "einwerfen"

# spieler_2 wuerfelt, danach muss einwerfen fertig sein
runde.command_to_event(spieler_2.name, "wuerfeln")
assert runde.state == "wuerfeln"


# FALL mehrfaches stechen, erst 4, dann 3, dann 2 spieler, dann beginn
runde = SchockenRunde()
assert runde.state == "einwerfen"
wuerfel.werfen = lambda n: (1,) * n
runde.command_to_event(spieler_1.name, "einwerfen")
runde.command_to_event(spieler_2.name, "einwerfen")
runde.command_to_event(spieler_3.name, "einwerfen")
runde.command_to_event(spieler_4.name, "einwerfen")
# alle stecher in der liste?
assert [st.name for st in runde.einwerfen.stecher_liste] == [
    "spieler_1",
    "spieler_2",
    "spieler_3",
    "spieler_4",
]
# neues stechen, 3 spieler werfen 1, spieler_4 wirft 2
runde.command_to_event(spieler_1.name, "stechen")
assert runde.state == "stechen"
runde.command_to_event(spieler_2.name, "stechen")
runde.command_to_event(spieler_3.name, "stechen")
wuerfel.werfen = lambda n: (2,) * n
runde.command_to_event(spieler_4.name, "stechen")
# spieler 4 versucht unerlaubterweise zu stechen
with pytest.raises(FalscherSpieler):
    runde.command_to_event(spieler_4.name, "stechen")

# die anderen spieler stechen
wuerfel.werfen = lambda n: (1,) * n
runde.command_to_event(spieler_1.name, "stechen")
runde.command_to_event(spieler_2.name, "stechen")
wuerfel.werfen = lambda n: (2,) * n
runde.command_to_event(spieler_3.name, "stechen")
# nur noch 1 und 2 in der stecherliste
assert [st.name for st in runde.einwerfen.stecher_liste] == ["spieler_1", "spieler_2"]

# 1 und 2 stechen
wuerfel.werfen = lambda n: (1,) * n
runde.command_to_event(spieler_1.name, "stechen")
wuerfel.werfen = lambda n: (2,) * n
runde.command_to_event(spieler_2.name, "stechen")

# spieler 2 versucht unerlaubterweise anzufangen
with pytest.raises(FalscherSpieler):
    runde.command_to_event(spieler_2.name, "wuerfeln")

# spieler 1 faengt an
runde.command_to_event(spieler_1.name, "wuerfeln")
assert runde.state == "wuerfeln"
assert runde.einwerfen.spieler_liste[0].name == spieler_1.name

# FALL einwerfen wenn stechen im gange ist
runde = SchockenRunde()

wuerfel.werfen = lambda n: (1,) * n
runde.command_to_event(spieler_1.name, "einwerfen")
runde.command_to_event(spieler_2.name, "einwerfen")

# spieler 2 will nochmal einwerfen
with pytest.raises(FalscherSpieler):
    runde.command_to_event(spieler_2.name, "einwerfen")

runde.command_to_event(spieler_1.name, "stechen")
# weiterer spieler will noch einwerfen, obwohl gestochen wird
with pytest.raises(FalscheAktion):
    runde.command_to_event(spieler_3.name, "einwerfen")
