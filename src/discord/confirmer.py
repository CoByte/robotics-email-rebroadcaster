from discord.ext.commands import *
from discord import *
import asyncio


class Confirmer:
    waitTime = 15  # max is 99
    subSize = 500  # keep this reasonable, no more then 750 at max, but it will cause issues if it's too big.

    check = "\u2714"
    cross = "\u274C"

    timeout = "\n*this request will time out in **{}** seconds*"

    def __init__(self, ctx, payload, successMessage, successFunc, failedMessage, terminateOnCall=False):
        self.ctx: Context = ctx
        self.payload = payload
        self.successMessage = successMessage
        self.successFunc = successFunc
        self.failedMessage = failedMessage
        self.terminateOnCall = terminateOnCall

        self.countdown: asyncio.Task = None
        self.questionMessage: Message = None
        self.alive = True
        self.denied = True

    def generate_package(self, time=waitTime):
        return self.payload + self.timeout.format(time)

    async def start(self):
        self.questionMessage = await self.ctx.send(self.generate_package())
        await self.questionMessage.add_reaction(self.check)
        await self.questionMessage.add_reaction(self.cross)
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
            self.countdown.cancel()

    async def finish(self):
        self.alive = False

        if self.terminateOnCall:
            await self.ctx.message.delete()

        if self.denied:
            await self.questionMessage.edit(content=self.failedMessage)
            await self.questionMessage.delete()
        else:
            await self.questionMessage.edit(content=self.successMessage)
            await self.questionMessage.clear_reactions()

            self.successFunc()

    async def confirm_reactions(self, payload: RawReactionActionEvent):
        if payload.event_type == "REACTION_ADD" and \
                payload.message_id == self.questionMessage.id and \
                payload.user_id == self.ctx.author.id:
            if payload.emoji == self.check:
                await self.end(False)
            elif payload.emoji == self.cross:
                await self.end(True)
