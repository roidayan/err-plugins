import os
from errbot import BotPlugin, botcmd


class ExampleUname(BotPlugin):

    @botcmd
    def uname(self, msg, args):
        return ' '.join(os.uname())
