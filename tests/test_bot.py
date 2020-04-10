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
def member(n=4):
    return [MockMember(f"spieler_{i+1}") for i in range(n)]


@pytest.fixture
def bot():
    client = MockClient()
    bot = MockBot(client)
    return bot


@pytest.fixture
async def running_bot(member):
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
    await bot.parse_input(MockMessage(member[3], "!einwerfen"))
    return bot


async def test_start_game(event_loop, member, bot):
    assert not bot.game_running
    await bot.parse_input(MockMessage(member[0], "!schocken"))
    assert bot.game_running
    await bot.parse_input(MockMessage(member[0], "!einwerfen"))
    # richtiger spieler:
    assert "spieler_1 hat eine" in bot.msg
    # anderer spieler will auch starten
    await bot.parse_input(MockMessage(member[1], "!schocken"))
    assert "Es läuft bereits ein Spiel" in bot.msg


async def test_einwerfen(capsys, member, bot):
    await bot.parse_input(MockMessage(member[0], "!schocken"))
    await bot.parse_input(MockMessage(member[0], "!schocken"))
    wuerfel.werfen = lambda n: (1,)
    await bot.parse_input(MockMessage(member[0], "!einwerfen"))
    wuerfel.werfen = lambda n: (2,)
    await bot.parse_input(MockMessage(member[1], "!einwerfen"))
    await bot.parse_input(MockMessage(member[2], "!einwerfen"))
    await bot.parse_input(MockMessage(member[3], "!einwerfen"))
    expected = "spieler_1 hat mit einer EMOJI:wuerfel_1 den niedgristen Wurf."
    assert expected in bot.msg
