import json
from discord.ext.commands import *
import inspect
import pickle
import os


class GlobalEnvironment(object):

    guildSettingsPath = "../data/userdata/guildsettings.pkl"

    def __init__(self):
        if os.stat(self.guildSettingsPath).st_size == 0:
            print("empty :(")
            self._guildSettings = {}
            self.save_guild_settings()
        else:
            with open(self.guildSettingsPath, 'rb') as infile:
                self._guildSettings = pickle.load(infile)

    def save_guild_settings(self):
        with open(self.guildSettingsPath, 'wb') as outfile:
            pickle.dump(self._guildSettings, outfile)

    def run_later(func):
        def inner(*args):
            return lambda: func(*args)
        return inner

    def ctx_arg(func):
        params = inspect.getfullargspec(func).args[2:]

        def inner(self, ctx: Context, *args):
            targetGuild = str(ctx.guild.id)

            payload = [self, targetGuild]

            for param in params:
                if param == "targetChannel":
                    payload.append(ctx.channel.id)

            payload.extend(args)

            func(*payload)
        return inner

    def add_new_guild(self, targetGuild: str):
        if targetGuild not in self._guildSettings:
            self._guildSettings[targetGuild] = {
                "passive-channels": set(),
                "email-list": set()
            }

    def is_passive_channel(self, targetGuild: str, targetChannel: int):
        if targetGuild in self._guildSettings:
            return targetChannel in self._guildSettings[targetGuild]["passive-channels"]
        return False

    def get_email_list(self, targetGuild: str):
        if targetGuild in self._guildSettings:
            return self._guildSettings[targetGuild]["email-list"]
        else:
            return []

    @ctx_arg
    def add_passive_channel(self, targetGuild: str, targetChannel: int):
        self.add_new_guild(targetGuild)
        self._guildSettings[targetGuild]["passive-channels"].add(targetChannel)
        self.save_guild_settings()

    @ctx_arg
    def remove_passive_channel(self, targetGuild: str, targetChannel: int):
        if targetGuild in self._guildSettings:
            self._guildSettings[targetGuild]["passive-channels"].discard(targetChannel)
            self.save_guild_settings()

    @run_later
    @ctx_arg
    def add_email_address(self, targetGuild: str, address: str):
        self.add_new_guild(targetGuild)
        self._guildSettings[targetGuild]["email-list"].add(address)
        self.save_guild_settings()

    @run_later
    @ctx_arg
    def remove_email_address(self, targetGuild: str, address: str):
        if targetGuild in self._guildSettings:
            self._guildSettings[targetGuild]["email-list"].discard(address)
            self.save_guild_settings()


globalEnvironment = GlobalEnvironment()
