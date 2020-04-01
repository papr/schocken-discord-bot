from schocken import wurf


def test_wurf_prioritaet(N=100):
    wuerfe = [
        wurf.Schock.out,
        wurf.SonderWurf.Jule,
        wurf.Schock.sechs,
        wurf.Schock.fuenf,
        wurf.Schock.vier,
        wurf.Schock.drei,
        wurf.Schock.doof,
        wurf.General.sechser,
        wurf.General.fuenfer,
        wurf.General.vierer,
        wurf.General.dreier,
        wurf.General.zweier,
        wurf.Straße.vierer,
        wurf.Straße.dreier,
        wurf.Straße.zweier,
        wurf.Straße.einser,
    ]
    wurf_prio_soll = [wurf.prioritaet(W) for W in wuerfe]

    wurf_prio_ist = sorted(wurf_prio_soll)
    assert wurf_prio_soll == wurf_prio_ist
