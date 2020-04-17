import random
from collections import Counter

from schocken import wuerfel


def test_wurf_wahrscheinlichkeiten(N=1_000_000, tol=5e-4, expected=1 / 6):
    random.seed(420)
    augen = range(1, 7)
    zaehler = Counter()
    for _ in range(N):
        for auge in wuerfel.werfen(3):
            zaehler[auge] += 1

    assert set(zaehler) == set(augen)
    total = sum(zaehler.values())
    probs = {auge: zaehler[auge] / total for auge in augen}
    diff = [abs(prob - expected) for prob in probs.values()]
    all_expected = all([d < tol for d in diff])
    msg = f"Wuerfelwahrscheinlichkeiten sind unausgeglichen (tol={tol}): {diff}"
    assert all_expected, msg
