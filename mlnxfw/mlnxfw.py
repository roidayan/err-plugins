import re
from subprocess import check_output, CalledProcessError
from errbot import BotPlugin, botcmd, re_botcmd


class MlnxFw(BotPlugin):
    def __exec(self, cmd):
        return check_output(cmd).decode()

    @botcmd
    def fw(self, msg, args):
        return self.__exec('/labhome/roid/scripts/mlxfwshow.py')

    @re_botcmd(pattern=r"(^| )(fw|firmware)\?( |$)", prefixed=True, flags=re.IGNORECASE)
    def re_fw(self, msg, match):
        return self.fw(msg, None)

    @re_botcmd(pattern=r"(^| )latest (fw|firmware)\?( |$)", prefixed=False, flags=re.IGNORECASE)
    def re_fw(self, msg, match):
        return self.fw(msg, None)

    @re_botcmd(pattern=r"(^| )synd?(rome)?( for )? (?P<syn>[^ ]+) ?\??( |$)", prefixed=False, flags=re.IGNORECASE)
    def syndrome(self, msg, match):
        syndrome = match.group('syn')
        cmd = '/labhome/roid/scripts/quick_syndrome.sh %s' % syndrome
        out = self.__exec(cmd.split())
        if not out:
            out = "Can't find a matching syndrome"
        return out
