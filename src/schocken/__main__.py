from .wurf import welcher_wurf
from . import wuerfel


for _ in range(10):
    aus_der_hand = bool(wuerfel.randint(0, 1))
    wuerfel_augen = wuerfel.werfen()
    wurf = welcher_wurf(wuerfel_augen)
    print(wuerfel_augen, f"{aus_der_hand=}", wurf, wurf.deckel_wert)
