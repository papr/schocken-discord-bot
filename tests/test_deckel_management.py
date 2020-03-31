from schocken import wurf
from schocken.spieler import Spieler
from schocken.deckel_management import RundenDeckelManagement, SpielzeitStatus


def test_simulate_spielzeit_naive():
    A = Spieler("A")
    B = Spieler("B")

    spielzeit_status = SpielzeitStatus(15, [A, B])
    while len(spielzeit_status.spieler) > 1:
        print(f"Status bei Rundenbeginn: {spielzeit_status}")
        spielzeit_status = _runde_spielen_jule_im_dritten(spielzeit_status)
        print(f"Status bei Rundenende: {spielzeit_status}")
    print(f"{spielzeit_status.spieler[0]} hat verloren!")


def _runde_spielen_schockout_im_ersten(status: SpielzeitStatus) -> SpielzeitStatus:
    jules_augen = wurf.SonderWurf.Jule._value_
    schockout_augen = wurf.Schock.out._value_
    rdm = RundenDeckelManagement(status)

    aktueller_spieler = 0
    rdm.wurf(status.spieler[aktueller_spieler].name, jules_augen, aus_der_hand=True)
    aktueller_spieler = rdm.weiter()
    rdm.wurf(status.spieler[aktueller_spieler].name, schockout_augen, aus_der_hand=True)
    return rdm.deckel_verteilen_restliche_spieler()


def _runde_spielen_jule_im_dritten(status: SpielzeitStatus) -> SpielzeitStatus:
    jules_augen = wurf.SonderWurf.Jule._value_
    rdm = RundenDeckelManagement(status)

    aktueller_spieler = 0
    for _ in range(3):
        rdm.wurf(status.spieler[aktueller_spieler].name, jules_augen, aus_der_hand=True)
    aktueller_spieler = rdm.weiter()
    # zweiter spieler muss gewinnen, da er/sie sonst anfaengt
    # und es zu einer Endlos-Schleife kommt
    for _ in range(2):
        rdm.wurf(status.spieler[aktueller_spieler].name, jules_augen, aus_der_hand=True)
    return rdm.deckel_verteilen_restliche_spieler()
