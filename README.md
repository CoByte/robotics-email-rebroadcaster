# robotics-email-rebroadcaster

Discord bot that takes messages and sends them out to a mailing list. Links to email via OAuth2 for security.

#### Broadcasts
The bot supports a variety of user triggered broadcasts, to allow for any variety of messages to be sent over email.

#### Passive Channels
When a channel is set as passive, it will automatically broadcast any message sent in it to the email list. This is done with a 5 minute timer, to allow for multiple messages to be combined into one email, to reduce spam. 

#### Emails
The bot formats emails using basic HTML, to allow for discord-like stylization that makes them easier to read and understand.

### Commands
| Command name                    | Action                                                                                                         |
|---------------------------------|----------------------------------------------------------------------------------------------------------------|
| echo < STR >                 | Broadcasts <STRING> to everyone on the email list                                                              |
| re-echo < INT >                 | Broadcasts previously sent message <INT>, where the last sent message is 1, the second to last is 2, et cetera |
| re-echo-range < INT_1, INT_2 >  | Broadcasts multiple previously sent messages, between <INT_1> and <INT_2> inclusively                          |
| add-email-address < STR >    | Adds <STRING> to the server email list                                                                         |
| remove-email-address < STR > | Removes <STRING> from the email list, if present                                                               |
| add-passive-channel             | Sets the channel this message was sent in to a passive channel                                                 |
| remove-passive-channel          | If the channel this message is sent in is a passive channel, unpassifies it                                    |
| help                            | Shows all commands                                                                                             |
