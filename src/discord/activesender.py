from discord import *
from src.email import emailmanager as emm
from src.discord.confirmer import Confirmer
from src.discord.utilityfunctions import *


class CommandSender(Cog):

    def __init__(self, bot: Bot, emailer: emm.EmailManager):
        self.bot = bot
        self.emailer = emailer

        self.confirmers = []
        self.confirmMessage = "Are you sure you want to broadcast \n{}\n to everyone in the mail list?"

    @Cog.listener()
    async def on_ready(self):
        Confirmer.check = utils.get(self.bot.emojis, id=783816021889777694)
        Confirmer.cross = utils.get(self.bot.emojis, id=783816021802352640)
        print("active sender is loaded")

    def process_payload(self, content: list):
        payload = "\n".join(msg["text-content"] for msg in content)
        predictedTotal = payload.count("\n") * 2 + len(payload) + len(self.confirmMessage) - 2

        if predictedTotal > 2000:
            startString = payload[:Confirmer.subSize].strip("\n ")
            endString = payload[-Confirmer.subSize:].strip("\n ")

            payload = startString + "...\n\n..." + endString

        return self.confirmMessage.format(("> " + payload).replace("\n", "\n> "))

    @staticmethod
    async def get_single_history(ctx, msgTarget):
        if msgTarget <= 0:
            raise BadArgument("no negative numbers allowed")
        rangedHistory = await ctx.history(limit=msgTarget, oldest_first=False).flatten()
        msg = rangedHistory[-1]
        return msg

    # The re-echo command broadcasts a message msgTarget messages in the past
    @command(
        name="re-echo",
        help="Broadcasts a previously sent message. It needs the number of the message",
        brief="Broadcasts a previously sent message."
    )
    @is_not_passive_channel()
    async def re_echo(self, ctx, msgTarget: int):
        msgTarget += 1
        msg = await self.get_single_history(ctx, msgTarget)
        await self.broadcast_confirm(ctx, msg)

    @re_echo.error
    async def re_echo_error(self, ctx, error):
        await handle_generic_error(ctx, error)

    # The re-echo-range command broadcasts a group of messages in the past between msgRangeA and msgRangeB
    @command(
        name="re-echo-range",
        help="Broadcasts a group of previously sent messages. It needs the start of the group and the end of the group",
        brief="Broadcasts a group of previously sent messages."
    )
    @is_not_passive_channel()
    async def re_echo_range(self, ctx, msgRangeA: int, msgRangeB: int):
        high = max(msgRangeA, msgRangeB) + 1
        low = min(msgRangeA, msgRangeB)

        if msgRangeB < 0 or msgRangeA < 0:
            raise BadArgument("No negative numbers allowed")

        if msgRangeA == msgRangeB:
            msg = await self.get_single_history(ctx, high)
            msgs = [msg]

        else:
            rangedHistory = await ctx.history(limit=high, oldest_first=False).flatten()
            msgs = rangedHistory[low:]
            msgs.reverse()

        await self.broadcast_confirm(ctx, *msgs)

    @re_echo_range.error
    async def re_echo_range_error(self, ctx, error):
        await handle_generic_error(ctx, error)

    @command(
        help="Broadcasts whatever you say!",
        brief="Broadcasts whatever you say!"
    )
    @is_not_passive_channel()
    async def echo(self, ctx, *, content):
        txtContent = self.emailer.create_raw_message(ctx.message)
        txtContent["text-content"] = txtContent["text-content"].replace("@Broadcaster echo ", "", 1)

        await self.broadcast_confirm(ctx, ctx, txtContent=[txtContent])

    async def broadcast_confirm(self, ctx, *msgs, txtContent=None):
        if txtContent is None:
            txtContent = [self.emailer.create_raw_message(msg) for msg in msgs]
        payload = self.process_payload(txtContent)

        self.confirmers.append(await Confirmer(
            ctx, payload,
            "Message has been broadcast!",
            lambda: self.emailer.send_email(txtContent, ctx.guild.id),
            "Message has been cancelled, terminating..."
        ).start())

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        for confirmer in self.confirmers:
            await confirmer.confirm_reactions(payload)
