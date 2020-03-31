class FalscheAktion(ValueError):
    pass


class FalscherServer(ValueError):
    pass


class FalscherSpielBefehl(ValueError):
    pass


class SpielLäuft(ValueError):
    pass


class SpielLäuftNicht(ValueError):
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


class KeineWürfeVorhanden(ValueError):
    pass


class DuHastMistGebaut(RuntimeError):
    pass


class RundeVorbei(ValueError):
    pass
