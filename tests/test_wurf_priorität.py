import numpy as np
from schocken import wurf


def test_wurf_priorität(N=100):
    aug = np.random.randint(1, 7, size=(N, 3))

    W = []
    for i, a in enumerate(aug):
        w = wurf.welcher_wurf(a)
        p = wurf.priorität(w)
        W.append((p, i, w))
    W.sort()
    assert False, W


def test_wurf_priorität_herrenwurf(N=100):
    p = wurf.priorität(wurf.SonderWurf.Herrenwurf)
    assert False, p
