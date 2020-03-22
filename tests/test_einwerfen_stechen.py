from offline_test_helpers import TestBot, FakeClient, FakeMember, FakeMessage

async def main():
    client = FakeClient()
    bot = TestBot(client)

    jasmin = FakeMember("Jasmin")
    pablo = FakeMember("Pablo")
    chris = FakeMember("Chris")

    start = FakeMessage(jasmin, "!schocken")
    einwurf_j = FakeMessage(jasmin, "!einwerfen")
    
    await bot.parse_input(start)
    await bot.parse_input(einwurf_j)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
