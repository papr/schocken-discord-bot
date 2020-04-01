class FalscheAktion(ValueError):
    pass


class FalscherServer(ValueError):
    pass


class FalscherSpielBefehl(ValueError):
    pass


class SpielLaeuft(ValueError):
    pass


class SpielLaeuftNicht(ValueError):
    pass


class ZuWenigSpieler(ValueError):
    pass


class FalscherSpieler(ValueError):
    pass


class NochNichtGeworfen(ValueError):
    pass


class ZuOftGeworfen(ValueError):
    pass


class UnbekannterSpieler(ValueError):
    pass


class KeineWuerfeVorhanden(ValueError):
    pass


class DuHastMistGebaut(RuntimeError):
    pass


class RundeVorbei(ValueError):
    pass


class PermissionError(ValueError):
    pass


class LustWurf(RuntimeError):
    def __init__(self, wurf):
        self.wurf = wurf
