from discord.ext.commands import *
from discord import *
from src.globalenvironment import globalEnvironment as env
import asyncio
from src.email import emailmanager as emm


class Chain:

    def __init__(self, startMessage, emailer: emm.EmailManager):
        self.startMessage = startMessage
        self.emailer = emailer
        self.alive = True

        self.countdown = None

    def start_countdown(self):

        async def count():
            await asyncio.sleep(PassiveSender.countdownTime)
            self.alive = False
            self.countdown = None

            msgs = [self.startMessage] + await self.startMessage.channel.history(after=self.startMessage).flatten()
            txtContent = [self.emailer.create_raw_message(msg) for msg in msgs]
            self.emailer.send_email(txtContent, self.startMessage.guild.id,
                                    subject="DO NOT REPLY - passive broadcast from " + self.startMessage.channel.name)

        self.countdown = asyncio.create_task(count())

    def reset_countdown(self):
        if self.countdown is not None and self.alive:
            self.countdown.cancel()
            self.start_countdown()


class PassiveSender(Cog):

    countdownTime = 5 * 60  # make 5 minutes when out of production

    def __init__(self, bot: Bot, emailer: emm.EmailManager):
        self.bot = bot
        self.emailer = emailer

        self.chains: dict = {}

    @command(hidden=True)
    async def scream(self, ctx):
        await ctx.send("***oh my lord why is this so hard?***")

    @Cog.listener("on_ready")
    async def on_ready(self):
        print("passive is loaded")

    @Cog.listener("on_message")
    async def on_message(self, msg: Message):
        if env.is_passive_channel(
            str(msg.guild.id),
            msg.channel.id
        ):
            chainKey = str(msg.guild.id)
            if chainKey not in self.chains or not self.chains[chainKey].alive:
                chain = Chain(msg, self.emailer)
                chain.start_countdown()
                self.chains[chainKey] = chain
            else:
                self.chains[chainKey].reset_countdown()
