from offline_test_helpers import TestBot, FakeClient, FakeMember, FakeMessage
from schocken.exceptions import SpielLäuft
import pytest

async def main():
    client = FakeClient()
    bot = TestBot(client)

    spieler_1 = FakeMember("spieler_1")
    spieler_2 = FakeMember("spieler_2")
    spieler_3 = FakeMember("spieler_3")
    spieler_4 = FakeMember("spieler_4")

    # spieler_1 starts game 
    await bot.parse_input(FakeMessage(spieler_1, "!schocken"))
    # another player also wants to start
    await bot.parse_input(FakeMessage(spieler_2, "!schocken"))

    # einwerfen
    await bot.parse_input(FakeMessage(spieler_1, "!einwerfen"))
    await bot.parse_input(FakeMessage(spieler_2, "!einwerfen"))
    await bot.parse_input(FakeMessage(spieler_3, "!einwerfen"))

    # stechen?
    await bot.parse_input(FakeMessage(spieler_2, "!stechen"))

    # Correct exception, 

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
