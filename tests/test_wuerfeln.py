import pytest

from schocken.spiel import Einwerfen, SchockenSpiel
from schocken.spieler import Spieler
from schocken.exceptions import FalscheAktion, FalscherSpieler

from schocken import wuerfel


@pytest.fixture
def spieler(n=4):
    # testspieler
    return [Spieler(f"spieler_{i+1}") for i in range(n)]


def test_wuerfeln_uebergang_einwerfen_halbzeit(spieler):
    runde = SchockenSpiel()
    assert runde.leaf_state.name == "einwerfen"

    # Übergang von Einwerfen nach Halbzeit
    runde = SchockenSpiel()
    assert runde.leaf_state.name == "einwerfen"
    wuerfel.werfen = lambda n: (2,) * n
    runde.command_to_event(spieler[0].name, "einwerfen")
    wuerfel.werfen = lambda n: (3,) * n
    runde.command_to_event(spieler[1].name, "einwerfen")
    wuerfel.werfen = lambda n: (1,) * n
    runde.command_to_event(spieler[2].name, "einwerfen")

    wuerfel.werfen = lambda n: (1, 2, 3)
    runde.command_to_event(spieler[2].name, "wuerfeln")

    assert runde._leaf_state.name == "wuerfeln"


def test_wuerfeln_falscher_spieler_wuerfelt(spieler):
    runde = SchockenSpiel()
    runde.leaf_state.name = "wuerfeln"

    assert runde._leaf_state.name == "wuerfeln"
