import pytest

from schocken.spiel import Einwerfen, SchockenSpiel
from schocken.spieler import Spieler
from schocken.exceptions import FalscheAktion, FalscherSpieler, NochNichtGeworfen, LustWurf

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

    # Mehrmaliges umdrehen derselben Sechsen ist nicht erlaubt
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
    # zweimal zur Seite legen derselben Eins ist nicht!
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

    # Kombination aus Einsen beiseite legen und Sechsen umdrehen
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


def test_nachgeworfen(spieler, drei_spieler_eingeworfen_spieler_zwei_muss_werfen):
    runde = drei_spieler_eingeworfen_spieler_zwei_muss_werfen

    # Alle Spieler würfeln dasselbe, letzter Spieler verliert die Runde
    wuerfel.werfen = lambda n: (5, 6, 6)
    runde.command_to_event(spieler[1].name, "wuerfeln")
    runde.command_to_event(spieler[1].name, "weiter")
    runde.command_to_event(spieler[2].name, "wuerfeln")
    runde.command_to_event(spieler[0].name, "wuerfeln")

    runde.halbzeit_erste.spieler_liste[2].deckel == 1


def test_uebergang_erste_halbzeit_zweite_halbzeit(spieler, drei_spieler_eingeworfen_spieler_zwei_muss_werfen):
    runde = drei_spieler_eingeworfen_spieler_zwei_muss_werfen

    # Herrenwurf verliert nicht ;)
    wuerfel.werfen = lambda n: (5, 5, 6)
    runde.command_to_event(spieler[1].name, "wuerfeln")
    runde.command_to_event(spieler[1].name, "weiter")
    wuerfel.werfen = lambda n: (1, 1, 3)
    runde.command_to_event(spieler[2].name, "wuerfeln")
    wuerfel.werfen = lambda n: (1, 1, 1)
    runde.command_to_event(spieler[0].name, "wuerfeln")

    # Erste Halbzeit ist vorbei und befindet sich im state_stack der root_machine
    assert runde.state_stack.deque[1].name == "Halbzeit"
    # Startspieler ist Spieler 2
    assert runde.halbzeit_zweite.spieler_liste[0].name == spieler[1].name
    # Spielerreihenfolge ist nun Spieler 2, Spieler 3, Spieler 1
    assert runde.halbzeit_zweite.spieler_liste[1].name == spieler[2].name
    assert runde.halbzeit_zweite.spieler_liste[2].name == spieler[0].name
    # Alle Spieler haben wieder Null Deckel
    assert runde.halbzeit_zweite.spieler_liste[0].deckel == 0
    assert runde.halbzeit_zweite.spieler_liste[1].deckel == 0
    assert runde.halbzeit_zweite.spieler_liste[2].deckel == 0


@pytest.fixture
def erste_halbzeit_beendet(spieler, drei_spieler_eingeworfen_spieler_zwei_muss_werfen):
    runde = drei_spieler_eingeworfen_spieler_zwei_muss_werfen

    wuerfel.werfen = lambda n: (5, 5, 6)
    runde.command_to_event(spieler[1].name, "wuerfeln")
    runde.command_to_event(spieler[1].name, "weiter")
    wuerfel.werfen = lambda n: (1, 1, 3)
    runde.command_to_event(spieler[2].name, "wuerfeln")
    wuerfel.werfen = lambda n: (1, 1, 1)
    runde.command_to_event(spieler[0].name, "wuerfeln")

    return runde


def test_uebergang_zweite_halbzeit_finale_mit_zwei_spielern(spieler, erste_halbzeit_beendet):
    runde = erste_halbzeit_beendet

    # Erste Halbzeit verlor Spieler 2, diese wird Spieler 3 verlieren
    wuerfel.werfen = lambda n: (1, 1, 1)
    runde.command_to_event(spieler[1].name, "wuerfeln")
    runde.command_to_event(spieler[1].name, "weiter")
    wuerfel.werfen = lambda n: (2, 2, 3)
    runde.command_to_event(spieler[2].name, "wuerfeln")
    wuerfel.werfen = lambda n: (1, 2, 1)
    runde.command_to_event(spieler[0].name, "wuerfeln")

    # Zweite Halbzeit ist vorbei und befindet sich im state_stack der root_machine
    assert runde.state_stack.deque[2].name == "Halbzeit"
    # Startspieler ist Spieler 1
    assert runde.finale.spieler_liste[0].name == spieler[2].name
    # Zweiter Spieler ist Spieler 2
    assert runde.finale.spieler_liste[1].name == spieler[1].name
    # Finalisten haben wieder Null Deckel
    assert runde.finale.spieler_liste[0].deckel == 0
    assert runde.finale.spieler_liste[1].deckel == 0


def test_uebergang_zweite_halbzeit_finale_ein_spieler_verliert_beide_halbzeiten(spieler, erste_halbzeit_beendet):
    runde = erste_halbzeit_beendet

    # Erste Halbzeit verlor Spieler 2, diese wird er ebenso verlieren
    wuerfel.werfen = lambda n: (1, 2, 2)
    runde.command_to_event(spieler[1].name, "wuerfeln")
    runde.command_to_event(spieler[1].name, "weiter")
    wuerfel.werfen = lambda n: (2, 2, 3)
    runde.command_to_event(spieler[2].name, "wuerfeln")
    wuerfel.werfen = lambda n: (1, 1, 1)
    runde.command_to_event(spieler[0].name, "wuerfeln")

    # Zweite Halbzeit ist vorbei und befindet sich im state_stack der root_machine
    assert runde.state_stack.deque[2].name == "Halbzeit"
    # root_machine sollte sich nun im state "anstoßen!" befinden
    assert runde.state.name == "anstoßen!"


def test_lustwurf(spieler, erste_halbzeit_beendet):
    runde = erste_halbzeit_beendet

    # Erste Halbzeit verlor Spieler 2
    # Reihenfolge: Spieler 2, Spieler 3, Spieler 1
    # Spieler 2 würfelt Jule
    wuerfel.werfen = lambda n: (1, 2, 4)
    runde.command_to_event(spieler[1].name, "wuerfeln")
    runde.command_to_event(spieler[1].name, "weiter")
    wuerfel.werfen = lambda n: (2, 2, 3)
    runde.command_to_event(spieler[2].name, "wuerfeln")
    wuerfel.werfen = lambda n: (1, 2, 2)
    runde.command_to_event(spieler[0].name, "wuerfeln")

    # Spieler 1 hat verloren und demnach 7 Deckel
    # Reihenfolge: Spieler 1, Spieler 2, Spieler 3
    assert runde.halbzeit_zweite.spieler_liste[0].deckel == 7

    # Spieler 1 würfelt Jule
    wuerfel.werfen = lambda n: (1, 2, 4)
    runde.command_to_event(spieler[0].name, "wuerfeln")
    runde.command_to_event(spieler[0].name, "weiter")
    wuerfel.werfen = lambda n: (2, 2, 3)
    runde.command_to_event(spieler[1].name, "wuerfeln")
    wuerfel.werfen = lambda n: (1, 2, 2)
    runde.command_to_event(spieler[2].name, "wuerfeln")

    # Spieler 3 hat verloren und demnach 7 Deckel
    # Reihenfolge: Spieler 3, Spieler 2, Spieler 1
    assert runde.halbzeit_zweite.spieler_liste[0].deckel == 7

    # Spieler 3 würfelt Jule im 3. Wurf
    wuerfel.werfen = lambda n: (4, 3, 4)
    runde.command_to_event(spieler[2].name, "wuerfeln")
    wuerfel.werfen = lambda n: (3, 3, 4)
    runde.command_to_event(spieler[2].name, "wuerfeln")
    wuerfel.werfen = lambda n: (1, 2, 4)
    runde.command_to_event(spieler[2].name, "wuerfeln")
    # Spieler 1 lässt Ehrenwurf liegen
    wuerfel.werfen = lambda n: (2, 2, 1)
    runde.command_to_event(spieler[0].name, "wuerfeln")
    runde.command_to_event(spieler[0].name, "weiter")
    # Spieler 2 würfelt höher
    wuerfel.werfen = lambda n: (3, 2, 3)
    runde.command_to_event(spieler[1].name, "wuerfeln")
    # Spieler 2 macht Lustwurf
    with pytest.raises(LustWurf):
        wuerfel.werfen = lambda n: (6, 5, 3)
        runde.command_to_event(spieler[1].name, "wuerfeln")
        wuerfel.werfen = lambda n: (3, 2, 3)
        runde.command_to_event(spieler[1].name, "wuerfeln")

    assert runde.halbzeit_zweite.spieler_liste[2].deckel == 1
