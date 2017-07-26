import re
import requests
from errbot import BotPlugin, botcmd, re_botcmd


CHUCK_URL = 'http://api.icndb.com/jokes/random'


class ChuckNorrisPlugin(BotPlugin):
    def get_joke(self):
        response = requests.get(CHUCK_URL)
        if response.status_code == requests.codes.ok:
            return response.json()['value']['joke']

    @botcmd
    def chuck(self, msg, args):
        return self.get_joke()

    @re_botcmd(pattern=r"(^| )chuck norris( |$)", prefixed=False, flags=re.IGNORECASE)
    def listen_chuck_norris(self, msg, match):
        return self.get_joke()
