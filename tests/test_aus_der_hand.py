from schocken.wurf import welcher_wurf, SonderWurf, Gemüse


def test_aus_der_hand():
    Jule = SonderWurf.Jule
    assert welcher_wurf(Jule._value_, aus_der_hand=True) is Jule
    assert welcher_wurf(Jule._value_, aus_der_hand=False) is Gemüse.tiefes
