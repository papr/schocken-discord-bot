import pytest

from schocken.spiel import Einwerfen, SchockenSpiel
from schocken.spieler import Spieler
from schocken.exceptions import FalscheAktion, FalscherSpieler

from schocken import wuerfel


@pytest.fixture
def spieler(n=4):
    # testspieler
    return [Spieler(f"spieler_{i+1}") for i in range(n)]


def test_wuerfeln(spieler):
    runde = SchockenSpiel()
    assert runde.leaf_state.name == "einwerfen"

    # Übergang von Einwerfen nach Halbzeit
    runde = SchockenSpiel()
    assert runde.leaf_state.name == "einwerfen"
    wuerfel.werfen = lambda n: (2,) * n
    runde.command_to_event(spieler[0].name, "einwerfen")
    wuerfel.werfen = lambda n: (3,) * n
    runde.command_to_event(spieler[1].name, "einwerfen")
    wuerfel.werfen = lambda n: (2,) * n
    runde.command_to_event(spieler[2].name, "einwerfen")

    wuerfel.werfen = lambda n: (6,) * n
    runde.command_to_event(spieler[0].name, "stechen")

    wuerfel.werfen = lambda n: (5,) * n
    runde.command_to_event(spieler[2].name, "stechen")

    runde.command_to_event(spieler[2].name, "wuerfeln")

    runde.command_to_event(spieler[2].name, "weiter")

    runde.command_to_event(spieler[0].name, "wuerfeln")
