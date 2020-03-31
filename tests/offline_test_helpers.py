from schocken.bot import SchockenBot


class MockGuild:
    def __init__(self, name):
        self.name = name
        self.emojis = []


class MockClient:
    def __init__(self):
        self.guilds = [MockGuild("Café A")]


class MockMember:
    def __init__(self, name):
        self.name = name
        self.mention = f"MENTION:{name}"


class MockChannel:
    def __init__(self, name):
        self.name = name

    def send(self, message):
        return f"MSG to channel {self.name}:\n {message}"


class MockMessage:
    def __init__(self, author, content, channel_name="schocktresen"):
        self.content = content
        self.author = author
        self.channel = MockChannel(channel_name)


class MockBot(SchockenBot):
    # override methods that need a server connection
    def emoji_by_name(self, name):
        return f"EMOJI:{name}"

    def name_to_member(self, name):
        return MockMember(name)

    async def print_to_channel(self, channel, text):
        msg = channel.send(text)
        print(msg + "\n" + "-" * 72)
