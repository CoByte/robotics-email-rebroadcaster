from discord.ext.commands import *
from src.discord import activesender, passivesender


def run(emailer, clientSecret):
    broadcaster = Bot(
        command_prefix=when_mentioned
    )

    broadcaster.add_cog(activesender.CommandSender(broadcaster, emailer))
    # broadcaster.add_cog(passivesender.PassiveSender(broadcaster, emailer))

    broadcaster.run(clientSecret)
