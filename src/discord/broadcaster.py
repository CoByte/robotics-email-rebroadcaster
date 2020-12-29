import discord
from discord.ext.commands import *
from src.discord import activesender, passivesender, settingmanager


def run(emailer, clientSecret):
    broadcaster = Bot(
        command_prefix=when_mentioned,
        intents=discord.Intents.all()
    )

    @broadcaster.check
    async def globally_block_dms(ctx):
        return ctx.guild is not None

    broadcaster.add_cog(activesender.CommandSender(broadcaster, emailer))
    broadcaster.add_cog(passivesender.PassiveSender(broadcaster, emailer))
    broadcaster.add_cog(settingmanager.SettingManager(broadcaster))

    broadcaster.run(clientSecret)
