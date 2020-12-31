from discord.ext.commands import *
from src.globalenvironment import globalEnvironment as env


def is_not_passive_channel():
    def predicate(ctx: Context):
        return not env.is_passive_channel(
            str(ctx.guild.id),
            ctx.channel.id
        )
    return check(predicate)


async def handle_generic_error(ctx, error):
    if isinstance(error, BadArgument):
        await ctx.send("Sorry, but your arguments for this command are invalid.")
    elif isinstance(error, MissingRequiredArgument):
        await ctx.send("Sorry, but you seem to be missing required arguments for this command")
    elif isinstance(error, CommandInvokeError):
        await ctx.send("Sorry, but you need to keep your broadcasts below 2000 characters")
    else:
        print(error)
        raise error
