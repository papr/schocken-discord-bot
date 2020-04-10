from offline_test_helpers import (
    MockBot,
    MockClient,
    MockMember,
    MockMessage,
)

# from schocken.exceptions import SpielLaeuft
from schocken import wuerfel
import pytest


pytestmark = pytest.mark.asyncio


@pytest.fixture
def member(n=3):
    return [MockMember(f"spieler_{i+1}") for i in range(n)]


@pytest.fixture
def bot():
    client = MockClient()
    bot = MockBot(client)
    return bot


@pytest.fixture
async def halbzeit_bot(member):
    # spiel läuft, spieler 1 darf anfangen
    client = MockClient()
    bot = MockBot(client)
    await bot.parse_input(MockMessage(member[0], "!schocken"))
    await bot.parse_input(MockMessage(member[0], "!schocken"))
    wuerfel.werfen = lambda n: (1,)
    await bot.parse_input(MockMessage(member[0], "!einwerfen"))
    wuerfel.werfen = lambda n: (2,)
    await bot.parse_input(MockMessage(member[1], "!einwerfen"))
    await bot.parse_input(MockMessage(member[2], "!einwerfen"))
    assert bot.game.state.stecher_liste[0].name == "spieler_1"
    return bot


async def test_start_game(member, bot):
    assert not bot.game_running
    await bot.parse_input(MockMessage(member[0], "!schocken"))
    assert bot.game_running
    await bot.parse_input(MockMessage(member[0], "!einwerfen"))
    # richtiger spieler:
    assert "spieler_1 hat eine" in bot.msg
    # anderer spieler will auch starten
    await bot.parse_input(MockMessage(member[1], "!schocken"))
    assert "Es läuft bereits ein Spiel" in bot.msg


async def test_einwerfen(member, bot):
    await bot.parse_input(MockMessage(member[0], "!schocken"))
    await bot.parse_input(MockMessage(member[0], "!schocken"))
    wuerfel.werfen = lambda n: (1,)
    await bot.parse_input(MockMessage(member[0], "!einwerfen"))
    wuerfel.werfen = lambda n: (2,)
    await bot.parse_input(MockMessage(member[1], "!einwerfen"))
    await bot.parse_input(MockMessage(member[2], "!einwerfen"))
    expected = "spieler_1 hat mit einer EMOJI:wuerfel_1 den niedgristen Wurf."
    assert expected in bot.msg


async def test_weiter(member, halbzeit_bot):
    wuerfel.werfen = lambda n: (4, 2, 1)
    await halbzeit_bot.parse_input(MockMessage(member[0], "!wuerfeln"))
    await halbzeit_bot.parse_input(MockMessage(member[0], "!weiter"))
    assert "High: MENTION:spieler_1" in halbzeit_bot.msg
    assert "Low: MENTION:spieler_1" in halbzeit_bot.msg
    assert "Als nächstes ist MENTION:spieler_2 (0 EMOJI:kronkorken)" in halbzeit_bot.msg


async def test_runde(member, halbzeit_bot):
    wuerfel.werfen = lambda n: (4, 2, 1)
    await halbzeit_bot.parse_input(MockMessage(member[0], "!wuerfeln"))
    await halbzeit_bot.parse_input(MockMessage(member[0], "!weiter"))

    wuerfel.werfen = lambda n: (2, 2, 1)
    await halbzeit_bot.parse_input(MockMessage(member[1], "!wuerfeln"))
    low_msg = "Low: MENTION:spieler_2 (0 EMOJI:kronkorken) mit: "
    low_msg += "EMOJI:wuerfel_2 EMOJI:wuerfel_2 EMOJI:wuerfel_1"
    # spieler zwei ist low
    assert low_msg in halbzeit_bot.msg
    # hat nur einen Wurf
    assert "Als nächstes ist MENTION:spieler_3" in halbzeit_bot.msg

    wuerfel.werfen = lambda n: (3, 2, 2)
    await halbzeit_bot.parse_input(MockMessage(member[2], "!wuerfeln"))
    # spieler 2 verliert!
    verl_msg = "MENTION:spieler_2 verliert die Runde und bekommt 7 EMOJI:kronkorken."
    assert verl_msg in halbzeit_bot.msg
    # spieler 2 fängt nächste runde an
    naechste_runde_msg = "Du bist mit `!wuerfeln` an der Reihe, "
    naechste_runde_msg += "MENTION:spieler_2 (7 EMOJI:kronkorken)."
    assert naechste_runde_msg in halbzeit_bot.msg
    # 8 deckel noch in der mitte:
    assert "Mitte: 8 EMOJI:kronkorken." in halbzeit_bot.msg


async def test_verteilen_vorbei(member, halbzeit_bot):
    wuerfel.werfen = lambda n: (4, 2, 1)
    await halbzeit_bot.parse_input(MockMessage(member[0], "!wuerfeln"))
    await halbzeit_bot.parse_input(MockMessage(member[0], "!weiter"))
    await halbzeit_bot.parse_input(MockMessage(member[1], "!wuerfeln"))

    # spieler 3 bekommt 7
    wuerfel.werfen = lambda n: (2, 2, 1)
    await halbzeit_bot.parse_input(MockMessage(member[2], "!wuerfeln"))
    wuerfel.werfen = lambda n: (4, 2, 1)
    await halbzeit_bot.parse_input(MockMessage(member[2], "!wuerfeln"))
    await halbzeit_bot.parse_input(MockMessage(member[2], "!weiter"))
    await halbzeit_bot.parse_input(MockMessage(member[0], "!wuerfeln"))

    # spieler 2 bekommt 7
    wuerfel.werfen = lambda n: (2, 2, 1)
    await halbzeit_bot.parse_input(MockMessage(member[1], "!wuerfeln"))

    # spieler 2 bekommt den letzten in der mitte
    await halbzeit_bot.parse_input(MockMessage(member[1], "!wuerfeln"))
    await halbzeit_bot.parse_input(MockMessage(member[1], "!weiter"))
    wuerfel.werfen = lambda n: (3, 3, 1)
    await halbzeit_bot.parse_input(MockMessage(member[2], "!wuerfeln"))
    await halbzeit_bot.parse_input(MockMessage(member[0], "!wuerfeln"))


async def test_halbzeit_vorbei(member, halbzeit_bot):
    wuerfel.werfen = lambda n: (4, 2, 1)
    await halbzeit_bot.parse_input(MockMessage(member[0], "!wuerfeln"))
    await halbzeit_bot.parse_input(MockMessage(member[0], "!weiter"))
    await halbzeit_bot.parse_input(MockMessage(member[1], "!wuerfeln"))
    wuerfel.werfen = lambda n: (2, 2, 1)
    await halbzeit_bot.parse_input(MockMessage(member[2], "!wuerfeln"))
    await halbzeit_bot.parse_input(MockMessage(member[2], "!wuerfeln"))
    await halbzeit_bot.parse_input(MockMessage(member[2], "!weiter"))
    wuerfel.werfen = lambda n: (4, 2, 1)
    await halbzeit_bot.parse_input(MockMessage(member[0], "!wuerfeln"))
    await halbzeit_bot.parse_input(MockMessage(member[1], "!wuerfeln"))
    wuerfel.werfen = lambda n: (2, 2, 1)
    await halbzeit_bot.parse_input(MockMessage(member[2], "!wuerfeln"))
    await halbzeit_bot.parse_input(MockMessage(member[2], "!weiter"))
    wuerfel.werfen = lambda n: (4, 2, 1)
    await halbzeit_bot.parse_input(MockMessage(member[0], "!wuerfeln"))
    await halbzeit_bot.parse_input(MockMessage(member[1], "!wuerfeln"))
    # fertigmachen
