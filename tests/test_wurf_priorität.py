from schocken import wurf


def test_wurf_priorität(N=100):
    würfe = [
        wurf.Schock.out,
        wurf.SonderWurf.Jule,
        wurf.Schock.sechs,
        wurf.Schock.fünf,
        wurf.Schock.vier,
        wurf.Schock.drei,
        wurf.Schock.doof,
        wurf.General.sechser,
        wurf.General.fünfer,
        wurf.General.vierer,
        wurf.General.dreier,
        wurf.General.zweier,
        wurf.Straße.vierer,
        wurf.Straße.dreier,
        wurf.Straße.zweier,
        wurf.Straße.einser,
    ]
    wurf_prio_soll = [wurf.priorität(W) for W in würfe]

    wurf_prio_ist = sorted(wurf_prio_soll)
    assert wurf_prio_soll == wurf_prio_ist
