import pytest

from schocken import events
from schocken.spiel import SchockenSpiel
from schocken.spieler import Spieler
from schocken.exceptions import FalscheAktion, FalscherSpieler

from schocken import wuerfel


@pytest.fixture
def spieler(n=4):
    # testspieler
    return [Spieler(f"spieler_{i+1}") for i in range(n)]


def test_einwerfen_trotz_stechen(spieler):
    runde = SchockenSpiel()
    assert runde.leaf_state.name == "einwerfen"

    # FALL: Zwei Spieler werfen dasselbe ein, einer versucht zu starten
    wuerfel.werfen = lambda n: (1,) * n
    runde.command_to_event(spieler[0].name, "einwerfen")
    runde.command_to_event(spieler[1].name, "einwerfen")

    with pytest.raises(FalscheAktion):
        runde.command_to_event(spieler[1].name, events.WÜRFELN)


@pytest.fixture
def drei_spieler_eingeworfen_spieler_zwei_muss_werfen(spieler):
    # FALL: spieler 2 würfelt eindeutig das niedrigste
    runde = SchockenSpiel()
    assert runde.leaf_state.name == "einwerfen"
    wuerfel.werfen = lambda n: (2,) * n
    runde.command_to_event(spieler[0].name, "einwerfen")
    wuerfel.werfen = lambda n: (1,) * n
    runde.command_to_event(spieler[1].name, "einwerfen")
    wuerfel.werfen = lambda n: (3,) * n
    runde.command_to_event(spieler[2].name, "einwerfen")
    return runde


def test_falscher_spieler(spieler, drei_spieler_eingeworfen_spieler_zwei_muss_werfen):
    runde = drei_spieler_eingeworfen_spieler_zwei_muss_werfen
    # Richtige exception, wenn jemand anders anfangen will?
    with pytest.raises(FalscherSpieler):
        runde.command_to_event(spieler[0].name, events.WÜRFELN)


def test_falsche_aktion(spieler, drei_spieler_eingeworfen_spieler_zwei_muss_werfen):
    runde = drei_spieler_eingeworfen_spieler_zwei_muss_werfen
    # Richtige exception, wenn jemand stechen will.
    with pytest.raises(FalscheAktion):
        runde.command_to_event(spieler[1].name, "stechen")


def test_korrekter_start(spieler, drei_spieler_eingeworfen_spieler_zwei_muss_werfen):
    runde = drei_spieler_eingeworfen_spieler_zwei_muss_werfen
    # momentaner state ist einwerfen
    assert runde.leaf_state.name == "einwerfen"

    # spieler[1] wuerfelt, danach muss einwerfen fertig sein
    runde.command_to_event(spieler[1].name, events.WÜRFELN)
    assert runde.leaf_state.name == events.WÜRFELN


@pytest.fixture
def vierfach_stechen(spieler):
    runde = SchockenSpiel()
    assert runde.leaf_state.name == "einwerfen"
    wuerfel.werfen = lambda n: (1,) * n
    for S in spieler:
        runde.command_to_event(S.name, "einwerfen")
    return runde


def test_mehrfaches_stechen(spieler, vierfach_stechen):
    # FALL mehrfaches stechen, erst 4, dann 3, dann 2 spieler, dann beginn
    runde = vierfach_stechen

    # alle stecher in der liste?
    stecher = [st.name for st in runde.einwerfen.stecher_liste]
    assert stecher == [S.name for S in spieler]

    # neues stechen, 3 spieler werfen 1, spieler_4 wirft 2
    runde.command_to_event(spieler[0].name, "stechen")
    assert runde.leaf_state.name == "stechen"
    runde.command_to_event(spieler[1].name, "stechen")
    runde.command_to_event(spieler[2].name, "stechen")
    wuerfel.werfen = lambda n: (2,) * n
    runde.command_to_event(spieler[3].name, "stechen")
    # spieler 4 versucht unerlaubterweise zu stechen
    with pytest.raises(FalscherSpieler):
        runde.command_to_event(spieler[3].name, "stechen")

    # die anderen spieler stechen
    wuerfel.werfen = lambda n: (1,) * n
    runde.command_to_event(spieler[0].name, "stechen")
    runde.command_to_event(spieler[1].name, "stechen")
    wuerfel.werfen = lambda n: (2,) * n
    runde.command_to_event(spieler[2].name, "stechen")
    # nur noch 1 und 2 in der stecherliste
    stecher = [st.name for st in runde.einwerfen.stecher_liste]
    assert stecher == [S.name for S in spieler[:2]]

    # 1 und 2 stechen
    wuerfel.werfen = lambda n: (2,) * n
    runde.command_to_event(spieler[0].name, "stechen")
    wuerfel.werfen = lambda n: (1,) * n
    runde.command_to_event(spieler[1].name, "stechen")

    # spieler 1 versucht unerlaubterweise anzufangen
    with pytest.raises(FalscherSpieler):
        runde.command_to_event(spieler[0].name, events.WÜRFELN)

    # spieler 2 faengt an
    runde.command_to_event(spieler[1].name, events.WÜRFELN)
    assert runde.leaf_state.name == events.WÜRFELN
    assert runde.einwerfen.sortierte_spieler_liste()[0].name == spieler[1].name


def test_einwerfen_während_stechen(spieler):
    # FALL einwerfen wenn stechen im gange ist
    runde = SchockenSpiel()

    wuerfel.werfen = lambda n: (1,) * n
    runde.command_to_event(spieler[0].name, "einwerfen")
    runde.command_to_event(spieler[1].name, "einwerfen")

    # spieler 2 will nochmal einwerfen
    with pytest.raises(FalscherSpieler):
        runde.command_to_event(spieler[1].name, "einwerfen")

    runde.command_to_event(spieler[0].name, "stechen")
    # weiterer spieler will noch einwerfen, obwohl gestochen wird
    with pytest.raises(FalscheAktion):
        runde.command_to_event(spieler[2].name, "einwerfen")


def test_stiche_höher_einwurf_augen(spieler):
    # FALL Stiche sind größer als nächstkleinere Einwurf Augenzahlen
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

    # spieler 3 muss anfangen zu würfeln
    with pytest.raises(FalscherSpieler):
        runde.command_to_event(spieler[0].name, events.WÜRFELN)

    with pytest.raises(FalscherSpieler):
        runde.command_to_event(spieler[1].name, events.WÜRFELN)
