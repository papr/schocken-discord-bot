from schocken.bot import SchockenBot


class FakeGuild:
    def __init__(self, name):
        self.name = name
        self.emojis = []


class FakeClient:
    def __init__(self):
        self.guilds = [FakeGuild("Café A")]


class FakeMember:
    def __init__(self, name):
        self.name = name
        self.mention = f"MENTION:{name}"


class FakeChannel:
    def __init__(self, name):
        self.name = name

    def send(self, message):
        return f"MSG to channel {self.name}:\n {message}"


class FakeMessage:
    def __init__(self, author, content):
        self.content = content
        self.author = author
        self.channel = FakeChannel("schocktresen")


class TestBot(SchockenBot):
    # override methods that need a server connection
    def emoji_by_name(self, name):
        return f"EMOJI:{name}"

    def name_to_member(self, name):
        return FakeMember(name)

    async def print_to_channel(self, channel, text):
        msg = channel.send(text)
        print(msg + "\n" + "-" * 72)
