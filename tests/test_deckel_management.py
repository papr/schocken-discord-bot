from schocken import wurf
from schocken.spieler import Spieler
from schocken.deckel_management import RundenDeckelManagement, SpielzeitStatus


def test_simulate_game():
    A = Spieler("A")
    B = Spieler("B")

    spielzeit_status = SpielzeitStatus(15, [A, B])
    while len(spielzeit_status.spieler) > 1:
        print(f"Status bei Rundenbeginn: {spielzeit_status}")
        spielzeit_status = _runde_spielen(spielzeit_status)
        print(f"Status bei Rundenende: {spielzeit_status}")
    print(f"{spielzeit_status.spieler[0]} hat verloren!")


def _runde_spielen(status: RSpielzeitStatusundenStatus) -> RSpielzeitStatusundenStatus:
    jules_augen = wurf.SonderWurf.Jule._value_
    rdm = RundenDeckelManagement(status)

    aktueller_spieler = 0
    rdm.wurf(status.spieler[aktueller_spieler].name, jules_augen, aus_der_hand=True)
    aktueller_spieler = rdm.weiter()
    rdm.wurf(status.spieler[aktueller_spieler].name, jules_augen, aus_der_hand=True)
    return rdm.deckel_verteilen()


if __name__ == "__main__":
    test_simulate_game()
