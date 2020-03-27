from offline_test_helpers import TestBot, FakeClient, FakeMember, FakeMessage
from schocken.exceptions import SpielLäuft
from schocken import wuerfel
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

    wuerfel.werfen = lambda n: (2,) * n
    await bot.parse_input(FakeMessage(spieler_1, "!einwerfen"))
    # einwerfen, stechen testen
    wuerfel.werfen = lambda n: (1,) * n
    await bot.parse_input(FakeMessage(spieler_2, "!einwerfen"))
    await bot.parse_input(FakeMessage(spieler_3, "!einwerfen"))
     
    wuerfel.werfen = lambda n: (3,) * n
    await bot.parse_input(FakeMessage(spieler_2, "!stechen"))

    wuerfel.werfen = lambda n: (3,) * n
    await bot.parse_input(FakeMessage(spieler_3, "!stechen"))

    wuerfel.werfen = lambda n: (2,) * n
    await bot.parse_input(FakeMessage(spieler_3, "!stechen"))

    wuerfel.werfen = lambda n: (3,) * n
    await bot.parse_input(FakeMessage(spieler_2, "!stechen"))

    # Einwerfen vorbei, jetzt würfeln.
    await bot.parse_input(FakeMessage(spieler_3, "!wuerfeln"))

    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
