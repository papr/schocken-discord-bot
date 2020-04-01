import pytest

from schocken.spiel import Einwerfen, SchockenSpiel
from schocken.spieler import Spieler
from schocken.exceptions import FalscheAktion, FalscherSpieler, NochNichtGeworfen

from schocken import wuerfel


@pytest.fixture
def spieler(n=4):
    # testspieler
    return [Spieler(f"spieler_{i+1}") for i in range(n)]


def test_uebergang_einwerfen_halbzeit(spieler):
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

    wuerfel.werfen = lambda n: (4, 6, 2)
    runde.command_to_event(spieler[2].name, "wuerfeln")

    assert runde._leaf_state.name == "wuerfeln"


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

    wuerfel.werfen = lambda n: (3, 1, 6) * n
    runde.command_to_event(spieler[1].name, "wuerfeln")

    # Spieler 1 führt mehrere Argumente aus
    with pytest.raises(FalscherSpieler):
        runde.command_to_event(spieler[0].name, "wuerfeln")

    with pytest.raises(FalscherSpieler):
        runde.command_to_event(spieler[0].name, "beiseite legen")

    with pytest.raises(FalscherSpieler):
        runde.command_to_event(spieler[0].name, "weiter")

    with pytest.raises(FalscherSpieler):
        runde.command_to_event(spieler[0].name, "umdrehen")


def test_falsche_aktion(spieler, drei_spieler_eingeworfen_spieler_zwei_muss_werfen):
    runde = drei_spieler_eingeworfen_spieler_zwei_muss_werfen

    wuerfel.werfen = lambda n: (3, 2, 6)
    runde.command_to_event(spieler[1].name, "wuerfeln")

    # Spieler 2 führt falsche Aktionen aus
    with pytest.raises(FalscheAktion):
        # keine Eins gewürfelt
        runde.command_to_event(spieler[1].name, "beiseite legen")

    with pytest.raises(FalscheAktion):
        # nur eine Sechs gewürfelt
        runde.command_to_event(spieler[1].name, "umdrehen")


def test_sechsen_umdrehen(spieler, drei_spieler_eingeworfen_spieler_zwei_muss_werfen):
    runde = drei_spieler_eingeworfen_spieler_zwei_muss_werfen

    # Spieler 2 würfelt zweimal zwei Sechsen und dreht diese um
    wuerfel.werfen = lambda n: (3, 6, 6)
    runde.command_to_event(spieler[1].name, "wuerfeln")
    runde.command_to_event(spieler[1].name, "umdrehen")

    # Mehrmaliges umdrehen ist nicht erlaubt
    with pytest.raises(FalscheAktion):
        runde.command_to_event(spieler[1].name, "umdrehen")

    wuerfel.werfen = lambda n: (6, 6,)
    runde.command_to_event(spieler[1].name, "wuerfeln")

    assert runde.halbzeit_erste.spieler_liste[0].augen == (1, 6, 6)

    runde.command_to_event(spieler[1].name, "umdrehen")
    wuerfel.werfen = lambda n: (2,)
    runde.command_to_event(spieler[1].name, "wuerfeln")

    assert runde.halbzeit_erste.spieler_liste[0].augen == (1, 1, 2)

    # Spieler 2 will noch mehr machen
    with pytest.raises(FalscherSpieler):
        runde.command_to_event(spieler[1].name, "weiter")

    with pytest.raises(FalscherSpieler):
        runde.command_to_event(spieler[1].name, "wuerfeln")

    with pytest.raises(FalscherSpieler):
        runde.command_to_event(spieler[1].name, "beiseite legen")

    with pytest.raises(FalscherSpieler):
        runde.command_to_event(spieler[1].name, "umdrehen")


def test_einsen_beiseite_legen(
    spieler, drei_spieler_eingeworfen_spieler_zwei_muss_werfen
):
    runde = drei_spieler_eingeworfen_spieler_zwei_muss_werfen

    # Spieler 2 würfelt zweimal zwei Einsen und legt diese nacheinander zur Seite
    wuerfel.werfen = lambda n: (1, 2, 6)
    runde.command_to_event(spieler[1].name, "wuerfeln")
    runde.command_to_event(spieler[1].name, "beiseite legen")
    # zweimal zur Seite legen ist nicht!
    with pytest.raises(FalscheAktion):
        runde.command_to_event(spieler[1].name, "beiseite legen")

    wuerfel.werfen = lambda n: (1, 2,)
    runde.command_to_event(spieler[1].name, "wuerfeln")
    runde.command_to_event(spieler[1].name, "beiseite legen")

    wuerfel.werfen = lambda n: (6,)
    runde.command_to_event(spieler[1].name, "wuerfeln")

    assert runde.halbzeit_erste.spieler_liste[0].augen == (1, 1, 6)


def test_einsen_und_sechsen(spieler, drei_spieler_eingeworfen_spieler_zwei_muss_werfen):
    runde = drei_spieler_eingeworfen_spieler_zwei_muss_werfen

    # Spieler 2 würfelt zweimal zwei Einsen und legt diese nacheinander zur Seite
    wuerfel.werfen = lambda n: (5, 6, 6)
    runde.command_to_event(spieler[1].name, "wuerfeln")
    runde.command_to_event(spieler[1].name, "umdrehen")

    wuerfel.werfen = lambda n: (2, 1,)
    runde.command_to_event(spieler[1].name, "wuerfeln")
    runde.command_to_event(spieler[1].name, "beiseite legen")

    wuerfel.werfen = lambda n: (3,)
    runde.command_to_event(spieler[1].name, "wuerfeln")

    assert runde.halbzeit_erste.spieler_liste[0].augen == (1, 1, 3)

    assert runde.halbzeit_erste.aktiver_spieler.name == "spieler_3"


def test_gluecksrunde(spieler, drei_spieler_eingeworfen_spieler_zwei_muss_werfen):
    runde = drei_spieler_eingeworfen_spieler_zwei_muss_werfen

    wuerfel.werfen = lambda n: (5, 5, 6)
    runde.command_to_event(spieler[1].name, "wuerfeln")
    runde.command_to_event(spieler[1].name, "weiter")

    wuerfel.werfen = lambda n: (3, 3, 2)
    runde.command_to_event(spieler[2].name, "wuerfeln")

    wuerfel.werfen = lambda n: (2, 3, 6)
    runde.command_to_event(spieler[0].name, "wuerfeln")

    # Spieler 3 hat verloren und muss als nächstes beginnen
    assert runde.halbzeit_erste.sortierte_spieler_liste()[0].name == spieler[2].name
    # Spieler 3 hat einen Deckel bekommen
    assert runde.halbzeit_erste.sortierte_spieler_liste()[0].deckel == 1
    # Die anderen Spieler haben keine Deckel bekommen
    assert runde.halbzeit_erste.sortierte_spieler_liste()[1].deckel == 0
    assert runde.halbzeit_erste.sortierte_spieler_liste()[2].deckel == 0

    # Spieler 1 will anfangen, darf er aber nicht
    with pytest.raises(FalscherSpieler):
        runde.command_to_event(spieler[0].name, "wuerfeln")

    # Spieler 3 will direkt weiter geben ohne zu würfeln
    with pytest.raises(NochNichtGeworfen):
        runde.command_to_event(spieler[2].name, "weiter")

    wuerfel.werfen = lambda n: (1, 1, 1)
    runde.command_to_event(spieler[2].name, "wuerfeln")
    runde.command_to_event(spieler[2].name, "weiter")

    wuerfel.werfen = lambda n: (1, 2, 2)
    runde.command_to_event(spieler[0].name, "wuerfeln")

    wuerfel.werfen = lambda n: (3, 3, 3)
    runde.command_to_event(spieler[1].name, "wuerfeln")

    # Spieler 1 muss alle Deckel haben
    assert runde.halbzeit_erste.sortierte_spieler_liste()[0].deckel == 15

    # Startspieler der zweiten Halbzeit ist Spieler 1
    assert runde.halbzeit_zweite.aktiver_spieler.name == spieler[0].name
