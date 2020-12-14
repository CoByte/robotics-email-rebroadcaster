from discord.ext.commands import *
from discord import *
import asyncio
from src.email import emailmanager as emm


def get_list_middles(data: list):
    middle = len(data) // 2
    if len(data) % 2 == 0:
        return data[middle - 1], data[middle]
    return data[middle]


class Confirmer:
    confirmMessage = "Are you sure you want to broadcast \n{}\n to everyone in the mail list?\n" \
                     "*this request will time out in **{}** seconds*"
    waitTime = 15  # max is 99
    subSize = 500  # keep this reasonable, no more then 750 at max, but it will cause issues if it's too big.

    def __init__(self, ctx, content, sender):
        self.ctx: Context = ctx
        self.content = content
        self.sender = sender

        self.countdown: asyncio.Task = None
        self.questionMessage: Message = None
        self.payload = self.process_payload(content)
        self.alive = True
        self.denied = True

    @staticmethod
    def process_payload(content: list):
        payload = "\n".join(msg["text-content"] for msg in content)
        predictedTotal = payload.count("\n") * 2 + len(payload) + len(Confirmer.confirmMessage) - 2

        if predictedTotal > 2000:
            startString = payload[:Confirmer.subSize].strip("\n ")
            endString = payload[-Confirmer.subSize:].strip("\n ")

            payload = startString + "...\n\n..." + endString

        return ("> " + payload).replace("\n", "\n> ")

    def generate_package(self, time=waitTime):
        return Confirmer.confirmMessage.format(self.payload, time)

    async def start(self):
        self.questionMessage = await self.ctx.send(self.generate_package())
        await self.questionMessage.add_reaction(self.sender.check)
        await self.questionMessage.add_reaction(self.sender.cross)
        await self.message_confirm_countdown()

        return self

    async def message_confirm_countdown(self):
        async def counter():
            try:
                for count in range(Confirmer.waitTime - 1, -1, -1):
                    await asyncio.sleep(1)
                    if self.alive:
                        await self.questionMessage.edit(content=self.generate_package(time=count))
            except asyncio.CancelledError:
                return
            finally:
                await self.finish()

        self.countdown = asyncio.create_task(counter())

    async def end(self, denied):
        self.denied = denied

        if self.countdown is not None:
            await self.countdown.cancel()

    async def finish(self):
        self.alive = False

        if self.denied:
            await self.questionMessage.edit(content="Message has been cancelled, terminating...")
            await self.questionMessage.delete()
        else:
            await self.questionMessage.edit(content="Message has been broadcast!")
            await self.questionMessage.clear_reactions()

            self.sender.emailer.send_email(self.content)

    async def confirm_reactions(self, payload: RawReactionActionEvent):
        print("not stalled ig?")
        if payload.event_type == "REACTION_ADD" and \
                payload.message_id == self.questionMessage.id and \
                payload.user_id == self.ctx.author.id:
            if payload.emoji == self.sender.check:
                await self.end(False)
            elif payload.emoji == self.sender.cross:
                await self.end(True)


class CommandSender(Cog):

    def __init__(self, bot: Bot, emailer: emm.EmailManager):
        self.bot = bot
        self.emailer = emailer

        self.check = "\u2714"
        self.cross = "\u274C"

        self.confirmers = []

    @Cog.listener()
    async def on_ready(self):
        self.check = utils.get(self.bot.emojis, id=783816021889777694)
        self.cross = utils.get(self.bot.emojis, id=783816021802352640)
        print("bot is active")

    @staticmethod
    async def get_single_history(ctx, msgTarget):
        if msgTarget <= 0:
            raise BadArgument("no negative numbers allowed")
        rangedHistory = await ctx.history(limit=msgTarget, oldest_first=False).flatten()
        msg = rangedHistory[-1]
        return msg

    # The re-echo command broadcasts a message msgTarget messages in the past
    @command(name="re-echo")
    async def re_echo(self, ctx, msgTarget: int):
        msgTarget += 1
        msg = await self.get_single_history(ctx, msgTarget)
        await self.broadcast_confirm(ctx, msg)

    @re_echo.error
    async def re_echo_error(self, ctx, error):
        await self.handle_generic_error(ctx, error)

    # The re-echo-range command broadcasts a group of messages in the past between msgRangeA and msgRangeB
    @command(name="re-echo-range")
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
        await self.handle_generic_error(ctx, error)

    @staticmethod
    async def handle_generic_error(ctx, error):
        if isinstance(error, BadArgument):
            await ctx.send("Sorry, but your arguments for this command are invalid.")
        elif isinstance(error, MissingRequiredArgument):
            await ctx.send("Sorry, but you seem to be missing required arguments for this command")
        elif isinstance(error, CommandInvokeError):
            await ctx.send("Sorry, but you need to keep your broadcasts below 2000 characters")
        else:
            raise error

    @command()
    async def echo(self, ctx, *, content):
        txtContent = self.emailer.create_raw_message(ctx.message)
        txtContent["text-content"] = txtContent["text-content"].replace("@Broadcaster echo ", "", 1)

        await self.broadcast_confirm(ctx, ctx, txtContent=[txtContent])

    async def broadcast_confirm(self, ctx, *msgs, txtContent=None):
        if txtContent is None:
            txtContent = [self.emailer.create_raw_message(msg) for msg in msgs]

        self.confirmers.append(await Confirmer(ctx, txtContent, self).start())

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        for confirmer in self.confirmers:
            await confirmer.confirm_reactions(payload)
