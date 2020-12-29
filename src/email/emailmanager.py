import yagmail
import re
from discord import *
from bs4 import BeautifulSoup
from globalenvironment import globalEnvironment as env
import random


"""
raw messages are dicts, structured as follows:
{
author: "name",
author-color: "color",
text-content: "content",
message-link: "link"
}
"""


htmlFooter = r"""This was an automatically generated message to keep you updated on the Summit High School robotics team discord server.
A direct link to this chat can be found here: {}.
If you believe you've received this message in error, if you have any questions on this program, or you've encountered a bug, please don't hesitate to contact the developer at owen356wh@gmail.com, and I'll do my best to help you as soon as possible."""


class EmailManager:

    def __init__(self, address, creds="../data/credentials/oauth2_creds.json"):
        self.yag = yagmail.SMTP(address, oauth2_file=creds)

    @staticmethod
    def create_raw_message(msg: Message):
        author = msg.author.display_name
        txtContent = msg.clean_content

        return {
            "author": author,
            "author-color": msg.author.color,
            "text-content": txtContent,
            "message-link": msg.jump_url
        }

    @staticmethod
    def parse_message_text(rawText):
        parsedText = re.split(r"(https?:\/\/\S{2,})", rawText)
        return parsedText

    @staticmethod
    def parse_messages(messages):
        parsedMessages = []
        for message in messages:

            textContent = message['text-content']
            textContent = textContent.split("\n")

            if len(parsedMessages) > 0:
                if message['author'] == parsedMessages[-1]['author']:
                    parsedMessages[-1]['text-content'].extend(textContent)
                    continue

            message['text-content'] = textContent
            parsedMessages.append(message)

        return parsedMessages

    @staticmethod
    def generate_email_html(parsedMessages):
        try:
            soup = BeautifulSoup()

            for block in parsedMessages:
                color = block["author-color"]
                speaker = soup.new_tag(
                    "b", style=f"color: rgb({color.r},{color.g},{color.b}); font-size: 1.25em;")
                speaker.string = block["author"]
                soup.append(speaker)

                rawContent = "\n".join(block["text-content"])

                content = soup.new_tag("div", style="color: black; font-size: 1.25em;")
                content.append(rawContent)
                soup.append(content)

                soup.append(soup.new_tag("hr"))

            footer = soup.new_tag("div", style="color: black; font-size: 1em;")
            footerText = "".join(map(lambda i: i + "\u200c" if random.randint(0, 1) and i != "{" else i, htmlFooter))
            footerText = footerText.format(parsedMessages[0]["message-link"])
            footer.append(footerText)
            soup.append(footer)

            return str(soup)
        except Exception as e:
            print(e)

    def send_email(self, messages, targetGuild, subject="AUTOMATED MESSAGE DO NOT REPLY"):
        messages = self.parse_messages(messages)
        emailContent = self.generate_email_html(messages)

        self.yag.send(
            to=list(env.get_email_list(str(targetGuild))),
            subject=subject,
            contents=emailContent
        )
