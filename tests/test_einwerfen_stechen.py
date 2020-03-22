from offline_test_helpers import TestBot, FakeClient, FakeMember, FakeMessage

async def main():
    client = FakeClient()
    bot = TestBot(client)

    jasmin = FakeMember("Jasmin")
    pablo = FakeMember("Pablo")
    chris = FakeMember("Chris")

    start = FakeMessage(jasmin, "!schocken")
    await bot.parse_input(start)

    einwurf_j = FakeMessage(jasmin, "!einwerfen")
    await bot.parse_input(einwurf_j)

    einwurf_c = FakeMessage(chris, "!einwerfen")
    await bot.parse_input(einwurf_c)

    stechen_j = FakeMessage(jasmin, "!stechen")
    await bot.parse_input(stechen_j)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
