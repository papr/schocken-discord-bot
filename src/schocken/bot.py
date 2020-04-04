import os
import signal

from .exceptions import (
    SpielLaeuft,
    SpielLaeuftNicht,
    FalscherSpielBefehl,
    FalscheAktion,
    PermissionError,
    FalscherSpieler,
    ZuOftGeworfen,
)
from .spiel import SchockenSpiel
from . import wurf
from discord.utils import get
from copy import deepcopy
import random


class SchockenBot:
    def __init__(self, client):
        self.client = client
        # bot will never run on any other server than Café A
        self.guild = client.guilds[0]
        self.schock_channel_name = "schocktresen"
        self.valid_guild_name = "Café A"
        self.game_running = False
        self._all_member_names = [member.name for member in self.guild.members]
        self._start_game_cmd = "schocken"
        self._end_game_cmd = "beenden"
        self._restart_cmd = "neustart"
        self._wuerfel_emoji_names = dict(
            [
                (1, "wuerfel_1"),
                (2, "wuerfel_2"),
                (3, "wuerfel_3"),
                (4, "wuerfel_4"),
                (5, "wuerfel_5"),
                (6, "wuerfel_6"),
            ]
        )
        self.discord_to_game_cmd_dict = {
            "einwerfen": "einwerfen",
            "wuerfeln": "wuerfeln",
            "stechen": "stechen",
            "weiter": "weiter",
            "beiseite": "beiseite legen",
            "umdrehen": "umdrehen",
        }

        self.game_to_discord_cmd_dict = {
            v: k for k, v in self.discord_to_game_cmd_dict.items()
        }

        self._halbzeit_state_names = {
            1: "halbzeit_erste",
            2: "halbzeit_zweite",
            3: "finale",
        }

        self._num_halbzeit_old_old = -1

    def emoji_by_name(self, name):
        emoji = get(self.guild.emojis, name=name)
        return str(emoji)

    def name_to_member(self, name):
        member = get(self.guild.members, name=name)
        return member

    def wurf_to_emoji(self, wuerfe):
        emoji_names = [self._wuerfel_emoji_names[w] for w in wuerfe]
        out = " ".join([self.emoji_by_name(n) for n in emoji_names])
        return out

    def discord_to_game_cmd(self, discord_cmd):
        try:
            game_cmd = self.discord_to_game_cmd_dict[discord_cmd]
            return game_cmd
        except KeyError:
            raise FalscherSpielBefehl

    def spieler_by_name(self, name, spielerliste):
        spieler = next(sp for sp in spielerliste if sp.name == name)
        return spieler

    def replace_names_by_mentions(self, string):
        for name in self._all_member_names:
            member = self.name_to_member(name)
            string = string.replace(name, member.mention)
        return string

    def command_in_schock_channel(self, message):
        msg_text = message.content
        channel = message.channel
        correct_channel = channel.name == self.schock_channel_name
        is_command = msg_text.startswith("!")
        is_not_restart = self._restart_cmd not in msg_text
        return correct_channel and is_command and is_not_restart

    def restart_issued(self, message):
        msg_text = message.content
        return msg_text == f"!{self._restart_cmd}"

    async def parse_input(self, message):
        # all messages from channels with read permissions are read
        msg_text = message.content
        channel = message.channel
        try:
            if self.command_in_schock_channel(message):
                command = msg_text.split("!")[-1]
                if command == self._start_game_cmd:
                    # TODO Status auf Spiel läuft setzten
                    if self.game_running:
                        raise SpielLaeuft
                    else:
                        self.game_running = True
                        self.game = SchockenSpiel()
                        msg = f"{message.author.mention} will schocken. "
                        msg += "`!einwerfen` zum mitmachen"
                        await self.print_to_channel(channel, msg)

                elif command == self._end_game_cmd:
                    # TODO Status auf Spiel beendet setzten
                    if self.game_running:
                        msg = f"{message.author.mention} hat das Spiel beendet"
                        self.game_running = False
                        await self.print_to_channel(channel, msg)
                    else:
                        raise SpielLaeuftNicht

                elif command == "ICH WILL UNREAL TOURNAMENT SPIELEN":
                    msg = "Dann geh doch"
                    await self.print_to_channel(channel, msg)
                    link = "https://tenor.com/view/unreal-tournament"
                    link += "-kid-unreal-unreal-kid-rage-gif-16110833"
                    await self.print_to_channel(channel, link)

                else:
                    if not self.game_running:
                        raise SpielLaeuftNicht
                    # actual game
                    await self.handle_game(message)

            elif self.restart_issued(message):
                role_strs = [str(role) for role in message.author.roles]
                if "developer" not in role_strs:
                    raise PermissionError
                msg = f"👋 Bis gleich! :wave:"
                await self.print_to_channel(channel, msg)
                await self.client.logout()
                os.kill(os.getpid(), signal.SIGINT)

        except NotImplementedError:
            msg = "Das geht leider noch nicht. (Nicht implementiert)"
            msg += "\n Spiel wird beendet."
            await self.print_to_channel(channel, msg)
            self.game_running = False
            del self.game

        except PermissionError:
            msg = "Das darfst du nicht, DU HURENSOHN!"
            msg += f"{self.emoji_by_name('king')}"
            await self.print_to_channel(channel, msg)

        except SpielLaeuftNicht:
            msg = f"Gerade läuft kein Spiel. "
            msg += "`!{self._start_game_cmd}` zum starten"
            await self.print_to_channel(channel, msg)

        except SpielLaeuft:
            msg = f"Es läuft bereits ein Spiel. "
            msg += "Versuch's mal mit `!einwerfen`."
            await self.print_to_channel(channel, msg)

        except FalscherSpielBefehl:
            msg = "Diesen Befehl gibt es nicht. "
            await self.print_to_channel(channel, msg)

        except FalscherSpieler as e:
            if str(e):
                msg = self.replace_names_by_mentions(str(e))
            else:
                msg = "Das darfst du gerade nicht (Falsche Spielerin)."
            await self.print_to_channel(channel, msg)

        except ZuOftGeworfen as e:
            if str(e):
                msg = self.replace_names_by_mentions(str(e))
            else:
                msg = "Du darfst nicht nochmal!"
            await self.print_to_channel(channel, msg)

        except FalscheAktion as e:
            if str(e):
                msg = self.replace_names_by_mentions(str(e))
            else:
                msg = "Das darfst du gerade nicht. (Falsche Aktion)"
            await self.print_to_channel(channel, msg)

    async def print_to_channel(self, channel, text):
        return await channel.send(text)

    async def handle_game(self, message):
        msg_text = message.content
        msg_channel = message.channel
        msg_author = message.author
        command = msg_text.split("!")[-1]
        msg_author_name = msg_author.name

        # freeze old game state. some properties are needed for the bot
        self.game_old = deepcopy(self.game)

        # run game state machine
        game_cmd = self.discord_to_game_cmd(command)
        self.game.command_to_event(msg_author_name, game_cmd)

        root_state_str = str(self.game.state).split()[1]
        leaf_state_str = self.game.state.leaf_state.name

        spieler = self.spieler_by_name(
            msg_author_name, self.game.einwerfen.spieler_liste
        )
        if leaf_state_str == "einwerfen":
            if command == "einwerfen":
                # wurf darstellen nach !einwerfen
                wurf_emoji = self.wurf_to_emoji(spieler.augen)
                out_str = f"{message.author.mention} hat eine "
                out_str += f"{wurf_emoji} geworfen."
                await self.print_to_channel(msg_channel, out_str)

            if self.game.einwerfen.stecher_count > 1:
                # bei keinem weiteren einwerfen muss gestochen werden
                stecher_wurf = self.game.einwerfen.stecher_liste[0].augen
                wurf_emoji = self.wurf_to_emoji(stecher_wurf)

                out_str = ", ".join(
                    [
                        self.name_to_member(pl.name).mention
                        for pl in self.game.einwerfen.stecher_liste
                    ]
                )
                out_str += f" haben eine {wurf_emoji} geworfen.\n"
                out_str += "`!stechen` um zu stechen oder auf"
                out_str += "weiteres `!einwerfen` warten"
                await self.print_to_channel(msg_channel, out_str)

            else:
                # es muss momentan nicht gestochen werden,
                # spiel kann anfangen
                if len(self.game.einwerfen.spieler_liste) > 1:
                    # spiel faengt erst an, wenn mehr als ein spieler
                    # eingeworfen hat
                    anfaenger = self.game.einwerfen.stecher_liste[0]
                    anf_member = self.name_to_member(anfaenger.name)
                    anf_wurf = anfaenger.augen
                    wurf_emoji = self.wurf_to_emoji(anf_wurf)

                    out_str = f"{anf_member.mention} hat mit einer "
                    out_str += f"{wurf_emoji} den niedgristen Wurf. "
                    out_str += "\n`!wuerfeln` um das Spiel zu beginnen "
                    out_str += "oder auf weiteres `!einwerfen` warten."
                    await self.print_to_channel(msg_channel, out_str)
                else:
                    pass

        elif leaf_state_str == "stechen":
            if command == "stechen":
                # wurf darstellen
                out_str = f"{message.author.mention} sticht mit einer "
                out_str += f"{self.wurf_to_emoji(spieler.augen)}."
                await self.print_to_channel(msg_channel, out_str)

                stecher = self.game.einwerfen.stecher_liste
                gestochen = self.game.einwerfen.gestochen_liste
                noch_stechen = [s for s in stecher if s not in gestochen]

                if len(stecher) > 1:
                    noch_st_members = [
                        self.name_to_member(pl.name) for pl in noch_stechen
                    ]
                    noch_st_mentions = [m.mention for m in noch_st_members]
                    out_str = ", ".join(noch_st_mentions)
                    muss = "muss" if len(noch_stechen) == 1 else "müssen"
                    out_str += f" {muss} `!stechen`."

                else:
                    anfaenger = self.game.einwerfen.stecher_liste[0]
                    anf_wurf = anfaenger.augen
                    wurf_emoji = self.wurf_to_emoji(anf_wurf)
                    out_str = f"{self.name_to_member(anfaenger.name).mention} "
                    out_str += f"hat mit einer {wurf_emoji} den niedrigsten Wurf. "
                    out_str += "`!wuerfeln` um das Spiel zu beginnen."

                await self.print_to_channel(msg_channel, out_str)

        elif leaf_state_str == "wuerfeln":
            # Vorbereitungen
            # in welcher halbzeit sind wir gerade?
            stack_list = list(self.game.state_stack.deque)
            stack_names = [st.name for st in stack_list]
            num_halbzeit = stack_names.count("Halbzeit") + 1
            # entsprechend halbzeit_erste oder halbzeit_zweite oder finale aus
            # game holen
            halbzeit = getattr(self.game, self._halbzeit_state_names[num_halbzeit])

            # rotierte spieler_liste
            # sp_liste = halbzeit.spieler_liste[1:] + halbzeit.spieler_liste[:1]
            sp_liste = halbzeit.spieler_liste
            # first check, kommen wir aus einwerfen?
            aus_einwerfen = self.game_old.state.leaf_state.name in [
                "einwerfen",
                "stechen",
            ]
            old_state_str = str(self.game_old.state).split()[1]

            # erfordern besondere outputs nach der aktion
            max_wuerfe = halbzeit.rdm.num_maximale_wuerfe
            is_zug_vorbei = max_wuerfe == 1 or spieler.anzahl_wuerfe == max_wuerfe

            if spieler == halbzeit.spieler_liste[-1]:
                deckel_vorher = self.game_old.state.rdm.zahl_deckel_im_topf
                deckel_neu = halbzeit.rdm.zahl_deckel_im_topf
                # deckel wurden verteilt, also ist runde vorbei
                is_runde_vorbei = deckel_vorher != deckel_neu
            else:
                is_runde_vorbei = False

            is_verteilen_vorbei = False

            # print(aus_einwerfen)
            if command == "wuerfeln":
                # ggf output vor eigentlichem wurf
                if old_state_str == "Einwerfen":
                    # erster output fuer erste halbzeit TODO erste zu zweite
                    num_halbzeit = 1
                    pre_output = self.gen_enter_halbzeit_output(sp_liste, num_halbzeit)
                    await self.print_to_channel(msg_channel, pre_output)
                    reicht_comment = False
                elif is_runde_vorbei:
                    # wenn mit dieser aktion runde vorbei ist, kein reicht printen.
                    # da kein zugriff mehr auf hoch und tief
                    reicht_comment = False
                else:
                    reicht_comment = True

                # Wuerfeloutput
                out_str = self.gen_wuerfel_output(
                    message, spieler, halbzeit, reicht_comment=reicht_comment
                )
                await self.print_to_channel(msg_channel, out_str)

                # Output nach dem wuerfeln
                if is_runde_vorbei:
                    out_str = self.gen_runde_vorbei_output(halbzeit)
                    await self.print_to_channel(msg_channel, out_str)
                elif is_zug_vorbei:
                    out_str = self.gen_nach_zug_output(halbzeit)
                    await self.print_to_channel(msg_channel, out_str)

            elif command == "weiter":
                out_str = self.gen_nach_zug_output(halbzeit)
                await self.print_to_channel(msg_channel, out_str)

            elif command == "umdrehen":
                raise NotImplementedError

            elif command == "beiseite":
                raise NotImplementedError

    def mention_mit_deckel(self, spieler):
        name = spieler.name
        deckel = spieler.deckel
        deckel_emoji = self.emoji_by_name("kronkorken")
        out = f"{self.name_to_member(name).mention} ({deckel} {deckel_emoji})"
        return out

    def gen_nach_zug_output(self, halbzeit):
        hoch, tief = halbzeit.rdm.hoch_und_tief()
        naechster = halbzeit.aktiver_spieler
        deckel_emoji = self.emoji_by_name("kronkorken")
        out_str = (
            f"{deckel_emoji} *in der Mitte: {halbzeit.rdm._zahl_deckel_im_topf}.*\n"
        )
        out_str += f"High: {self.mention_mit_deckel(hoch.spieler)} "
        out_str += f"mit: {self.wurf_to_emoji(hoch.spieler.augen)}\n"
        out_str += f"Low: {self.mention_mit_deckel(tief.spieler)} "
        out_str += f"mit: {self.wurf_to_emoji(tief.spieler.augen)}\n"
        out_str += f"Als nächstes ist {self.mention_mit_deckel(naechster)} "
        out_str += "mit `!wuerfeln` dran. "
        return out_str

    def gen_enter_halbzeit_output(self, spieler_liste, num_halbzeit):
        out_str0 = f"Halbzeit {num_halbzeit} beginnt. Die Reihenfolge ist:\n"
        out_str0 += ", ".join([self.mention_mit_deckel(pl) for pl in spieler_liste])
        return out_str0

    def gen_runde_vorbei_output(self, halbzeit):
        verlierer = halbzeit.spieler_liste[0]
        verlierer_old = next(
            s for s in self.game_old.state.spieler_liste if s.name == verlierer.name
        )
        deckel = verlierer.deckel - verlierer_old.deckel
        verl_member = self.name_to_member(verlierer.name)
        deckel_emoji = self.emoji_by_name("kronkorken")
        deckel_mitte = halbzeit.rdm.zahl_deckel_im_topf
        out_str = f"{verl_member.mention} verliert die Runde und bekommt "
        out_str += f"{deckel} {deckel_emoji}.\n"
        out_str += f"{deckel_emoji} *in der Mitte: {deckel_mitte}.* "
        out_str += f"Du bist mit `!wuerfeln` an der Reihe, "
        out_str += f"{self.mention_mit_deckel(verlierer)}."
        return out_str

    def gen_wuerfel_output(self, message, spieler, halbzeit, reicht_comment=False):
        augen = spieler.augen
        wurf_emoji = self.wurf_to_emoji(augen)
        # besonderer wurf?
        augen_name = str(wurf.welcher_wurf(augen))
        out_str = f"{self.mention_mit_deckel(spieler)} wirft "
        out_str += wurf_emoji + "."

        comment_choices = [" "]
        if "Gemuese" in augen_name:
            if augen[0] < 5:
                comment_choices = [
                    "Gar nicht mal so gut...",
                    "Schlechtes Gemüse...",
                    "Das kannst du besser!",
                    "Wow.",
                ]
                reicht_choices = {
                    "reicht": [" Aber reicht sogar.",],
                    "reichtnicht": [" Und reicht nicht mal.",],
                }

            elif augen[0] == 5:
                comment_choices = [
                    "Das kann man noch schlagen.",
                    "Ausbaufähig...",
                ]
                reicht_choices = {
                    "reicht": [" Aber reicht sogar.",],
                    "reichtnicht": [" Und reicht nichtmal.",],
                }

            elif augen[0] == 6:
                comment_choices = [
                    "Hohes Gemüse.",
                    "Nicht schlecht!",
                ]
                reicht_choices = {
                    "reicht": [" Und reicht sogar.",],
                    "reichtnicht": [" Aber reicht gar nicht.",],
                }

        elif "General" in augen_name:
            comment_choices = ["Kann man liegen lassen.", "General."]
            reicht_choices = {
                "reicht": [" Reicht ja.",],
                "reichtnicht": [" Aber reicht gar nicht.",],
            }

        elif "Straße" in augen_name:
            if augen[-1] == 1:
                comment_choices = [
                    "Da is' ne 1 dabei.",
                    "Keine schöne Straße.",
                ]
                reicht_choices = {
                    "reicht": [" Aber würde reichen.",],
                    "reichtnicht": [" Reicht ja nicht mal"],
                }

            else:
                comment_choices = [
                    "Straße.",
                ]
                reicht_choices = {
                    "reicht": [" Reicht.",],
                    "reichtnicht": [" Reicht ja nicht mal"],
                }

        elif "Schock" in augen_name:
            if "out" in augen_name:
                comment_choices = [
                    "Nice.",
                    "Random Schock Out.",
                    "Würde ich liegen lassen.",
                ]
                reicht_choices = {
                    "reicht": [" Reicht.",],
                    "reichtnicht": [" Aber reicht ja nicht mal.",],
                }
            else:
                comment_choices = ["Schöner Schock."]
                reicht_choices = {
                    "reicht": [" Reicht auch.",],
                    "reichtnicht": [" Aber reicht gar nicht.",],
                }

        elif "Herrenwurf" in augen_name:
            comment_choices = ["Herrenwurf. Verliert nicht."]
            reicht_choices = {
                "reicht": [" Und reicht sogar.",],
                "reichtnicht": [" ...aber diesmal vielleicht schon.",],
            }

        elif "Jule" in augen_name:
            comment_choices = ["Schöne Jule."]
            reicht_choices = {
                "reicht": [" Und sie reicht.",],
                "reichtnicht": [" Aber reicht leider nicht.",],
            }

        out_str += "\n" + random.choice(comment_choices)

        if reicht_comment:
            hoch, tief = halbzeit.rdm.hoch_und_tief()
            reicht = tief.spieler.name != spieler.name
            if reicht:
                out_str += random.choice(reicht_choices["reicht"])
            else:
                out_str += random.choice(reicht_choices["reichtnicht"])

        return out_str
