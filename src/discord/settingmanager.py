from src.discord.confirmer import Confirmer
from src.discord.utilityfunctions import *


class SettingManager(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

        self.confirmers = []

    @Cog.listener("on_ready")
    async def on_ready(self):
        print("setting manager is loaded")

    @command(
        name="add-passive-channel",
        help="Turns whatever channel you've submitted this message in into a passive channel.\nThis will cause all messages sent in this channel to be broadcasted to the email list.",
        brief="Turns this channel into a passive channel"
    )
    @is_not_passive_channel()
    async def add_channel(self, ctx: Context):
        env.add_passive_channel(ctx)
        await ctx.send("Passive channel added!")

    @add_channel.error
    async def add_channel_error(self, ctx, error):
        await handle_generic_error(ctx, error)

    @command(
        name="remove-passive-channel",
        help="If the channel this message has been submitted in is a passive channel, then it becomes no longer passive.",
        brief="Makes this channel not passive"
    )
    async def remove_channel(self, ctx: Context):
        env.remove_passive_channel(ctx)
        await ctx.send("Passive channel removed!")

    @remove_channel.error
    async def remove_channel_error(self, ctx, error):
        await handle_generic_error(ctx, error)

    @command(
        name="add-email-address",
        help="Adds an email address to the mailing list. Takes one address. Using this command with an email you do not have permission to add is prohibited",
        brief="Adds an email address to the mailing list"
    )
    @is_not_passive_channel()
    async def add_email_address(self, ctx: Context, address: str):
        self.confirmers.append(await Confirmer(
            ctx,
            f"Are you sure you want to add `{address}` to the email list?",
            "Address has been added!",
            env.add_email_address(ctx, address),
            "Addition has been cancelled, terminating...",
            terminateOnCall=True
        ).start())

    @add_email_address.error
    async def add_email_address_error(self, ctx, error):
        await handle_generic_error(ctx, error)

    @command(
        name="remove-email-address",
        help="Removes an email address to the mailing list. Takes one address. Using this command with an email you do not have permission to remove is prohibited",
        brief="Removes an email address from the mailing list"
    )
    @is_not_passive_channel()
    async def remove_email_address(self, ctx: Context, address: str):
        self.confirmers.append(await Confirmer(
            ctx,
            f"Are you sure you want to remove `{address}` to the email list (if it exists)?",
            "Address has been removed!",
            env.remove_email_address(ctx, address),
            "Addition has been cancelled, terminating...",
            terminateOnCall=True
        ).start())

    @command(
        name="gimme-environ",
        hidden=True
    )
    @is_owner()
    async def gimme_environment(self, ctx: Context):
        tempSettings = repr(env._guildSettings)
        while True:
            await ctx.author.send(tempSettings[:1900])
            tempSettings = tempSettings[1900:]
            if len(tempSettings) == 0:
                break

    @add_email_address.error
    async def remove_email_address_error(self, ctx, error):
        await handle_generic_error(ctx, error)

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        for confirmer in self.confirmers:
            await confirmer.confirm_reactions(payload)
