import json


class GlobalEnvironment(object):

    guildsettingsPath = "../data/userdata/guildsettings.json"

    def __init__(self):
        with open(GlobalEnvironment.guildsettingsPath) as file:
            self._guildsettings = json.loads(file.read())

    @property
    def guildSettings(self):
        return self._guildsettings

    @guildSettings.setter
    def guildSettings(self, value):
        if not isinstance(value, dict):
            raise TypeError("value must be a dictionary")
        self._guildsettings = value
        with open(GlobalEnvironment.guildsettingsPath, "w") as file:
            json.dump(self._guildsettings, file, indent=4)


globalEnvironment = GlobalEnvironment()
