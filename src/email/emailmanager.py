import yagmail
import re
from discord import *
from bs4 import BeautifulSoup, NavigableString


"""
raw messages are dicts, structured as follows:
{
author: "<name>",
author-color: "<color>",
text-content: "<content>"
}
"""


class EmailManager:

    def __init__(self, address, creds="oauth2_creds.json"):
        self.address = address
        self.creds = creds

    @staticmethod
    def create_raw_message(msg: Message):
        member = msg.author
        for user in msg.guild.members:
            if msg.author == user:
                break

        txtContent = msg.clean_content

        if isinstance(member, User):
            author = msg.author.name
        elif member.nick is None:
            author = msg.author.name
        else:
            author = member.nick

        return {
            "author": author,
            "color": msg.author.color,
            "text-content": txtContent
        }

    @staticmethod
    def parse_message_text(rawText):
        text = rawText.replace("<", "&lt").replace(">", "&gt")
        text = re.sub(
            r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s("
            r")<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))",
            lambda m: f"<a href={m.group(0)}>{m.group(0)}</a>", text
        )

        return text

    @staticmethod
    def parse_messages(messages):
        parsedMessages = []
        for message in messages:

            textContent = message['text-content']
            textContent = EmailManager.parse_message_text(textContent)

            if len(parsedMessages) > 0:
                if message['author'] == parsedMessages[-1]['author']:
                    parsedMessages[-1]['text-content'].append(textContent)
                    continue

            message['text-content'] = [textContent]
            parsedMessages.append(message)

        return parsedMessages

    @staticmethod
    def generate_email_html(parsedMessages):
        with open("../../data/templates/template.html", "r") as template:
            txt = template.read()
            soup = BeautifulSoup(txt)

        with open("../../data/templates/styles.css", "r") as stylesheet:
            styles = stylesheet.read()

        soup.head.append(styles)

        for block in parsedMessages:
            blockDiv = soup.new_tag("div", attrs={"class": "speaker"})

            color = block["author-color"]
            speaker = soup.new_tag(
                "h2", style=f"color: rgb({color.r},{color.g},{color.b})")
            speaker.string = block["author"]
            blockDiv.append(speaker)

            for msgText in block["message-text"]:
                content = soup.new_tag("p")
                content.string = msgText
                blockDiv.append(content)

            soup.body.append(blockDiv)
            soup.body.append(soup.new_tag("div", attrs={"class": "break"}))

        print(soup)

        return soup

    def send_email(self, messages):
        messages = self.parse_messages(messages)
        emailContent = self.generate_email_html(messages)

# test = EmailManager()
# genTest = test.parse_messages([
#     {
#         "author": "Jake",
#         "author-color": "e",
#         "text-content": "eat that pant gamers http://eat-my-pants/thisisfine.com"
#     },
#     {
#         "author": "Jake",
#         "author-color": "e",
#         "text-content": "<p>hackerman</p>"
#     },
#     {
#         "author": "Janette",
#         "author-color": "e",
#         "text-content": "excuse me"
#     },
#     {
#         "author": "Jake",
#         "author-color": "e",
#         "text-content": "you heard me"
#     }
# ])
#
# print(genTest)
