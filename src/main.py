import src.discord.broadcaster as bot
from src.email import emailmanager as emm

# why do i exist?

with open("data/credentials/tokens.env") as rawTokens:
    rawTokens = rawTokens.readlines()
    tokens = dict([i.split("=") for i in rawTokens])

emailer = emm.EmailManager(tokens["emailaddress"])

bot.run(emailer, tokens["clientsecret"])
