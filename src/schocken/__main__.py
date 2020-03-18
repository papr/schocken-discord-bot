from .wurf import welcher_wurf
from . import würfel


for _ in range(10):
    aus_der_hand = bool(würfel.randint(0, 1))
    würfel_augen = würfel.werfen()
    wurf = welcher_wurf(würfel_augen)
    print(würfel_augen, f"{aus_der_hand=}", wurf, wurf.deckel_wert)
