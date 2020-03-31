from offline_test_helpers import MockBot, MockChannel, MockClient, MockMember, MockMessage
from schocken.exceptions import SpielLäuft
from schocken import wuerfel
import pytest, asyncio

@pytest.fixture
def member(n=4):
    return [MockMember(f"spieler_{i+1}") for i in range(n)]

@pytest.fixture
def bot():
    client = MockClient()
    bot = MockBot(client)
    return bot

pytestmark = pytest.mark.asyncio

async def test_start_game(capsys, member, bot):
    assert bot.game_running == False
    await bot.parse_input(MockMessage(member[0], "!schocken"))
    assert bot.game_running == True
    out, err = capsys.readouterr()
    # richtiger spieler:
    assert "spieler_1" in out
    # start message sollte !einwerfen drin haben:
    assert "!einwerfen" in out
    # anderer spieler will auch starten
    await bot.parse_input(MockMessage(member[1], "!schocken"))
    out, err = capsys.readouterr()
    assert "läuft" in out

async def test_einwerfen( member, bot):
    # spiel starten mit fixture ist schwierig wegen der coroutines
    # spiel manuell starten:
    await bot.parse_input(MockMessage(member[0], "!schocken"))
    assert bot.game_running == True

    print(bot.game.state)
    wuerfel.werfen = lambda n: (2,) * n
    await bot.parse_input(MockMessage(member[0], "!einwerfen"))

    wuerfel.werfen = lambda n: (2,) * n
    await bot.parse_input(MockMessage(member[0], "!einwerfen"))

    # out, _ = capsys.readouterr()
    # print(out)

async def main():
    client = MockClient()
    bot = MockBot(client)

    spieler_1 = MockMember("spieler_1")
    spieler_2 = MockMember("spieler_2")
    spieler_3 = MockMember("spieler_3")
    spieler_4 = MockMember("spieler_4")

    # spieler_1 starts game 
    await bot.parse_input(MockMessage(spieler_1, "!schocken"))

    wuerfel.werfen = lambda n: (2,) * n
    await bot.parse_input(MockMessage(spieler_1, "!einwerfen"))
    # einwerfen, stechen testen
    wuerfel.werfen = lambda n: (1,) * n
    await bot.parse_input(MockMessage(spieler_2, "!einwerfen"))
    await bot.parse_input(MockMessage(spieler_3, "!einwerfen"))
     
    wuerfel.werfen = lambda n: (3,) * n
    await bot.parse_input(MockMessage(spieler_2, "!stechen"))

    wuerfel.werfen = lambda n: (3,) * n
    await bot.parse_input(MockMessage(spieler_3, "!stechen"))

    wuerfel.werfen = lambda n: (2,) * n
    await bot.parse_input(MockMessage(spieler_3, "!stechen"))

    wuerfel.werfen = lambda n: (3,) * n
    await bot.parse_input(MockMessage(spieler_2, "!stechen"))

    # Einwerfen vorbei, jetzt würfeln.
    await bot.parse_input(MockMessage(spieler_3, "!wuerfeln"))
