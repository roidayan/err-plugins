__author__ = 'Roi Dayan'

import os
import re
import random
from errbot import BotPlugin, botcmd, re_botcmd
from tinydb import TinyDB, Query


curr_dir = os.path.dirname(os.path.realpath(__file__))
faq_db = os.path.join(curr_dir, 'faq.db')

DUP_RESPONSE = [
    'I know something else',
    'hmm, i know differently',
    'are you sure?',
    'already have something',
]

ADD_REM_RESPONSE = [
    'ok', 'sure', 'no problem', 'done', 'consider it done'
]

ADD_RESPONSE = [
    'great',
    'thanks',
    'good to know',
    'saved',
    "i'll remember that",
    'always happy to learn',
    'great stuff',
]
ADD_RESPONSE.extend(ADD_REM_RESPONSE)

REM_RESPONSE = [
    'removed',
    'forgot',
    'gone',
    'its gone',
]
REM_RESPONSE.extend(ADD_REM_RESPONSE)

NOT_FOUND_RESPONSE = [
    'no answer',
    'nothing',
    'no idea',
    'is it real?',
    'not here',
    'i only have an empty thought',
    'who knows?',
]

FOUND_RESPONSE = [
    "i think it's {a}",
    "pretty sure it's {a}",
    "probably {a}",
    "afaik it's {a}",
    "fyi, it's {a}",
]


class FaqPlugin(BotPlugin):

    def activate(self):
        super().activate();
        self.db = TinyDB(faq_db)

    def getfromdb(self, q):
        i = Query()
        return self.db.search(i.q == q)

    def addFAQ(self, q, a):
        if self.getfromdb(q):
            return random.choice(DUP_RESPONSE)
        self.db.insert({'q': q, 'a': a})
        return random.choice(ADD_RESPONSE)

    def remFAQ(self, q):
        if not self.getfromdb(q):
            return "Never knew it"
        i = Query()
        self.db.remove(i.q == q)
        return random.choice(REM_RESPONSE)

    def getFAQ(self, q):
        r = self.getfromdb(q)
        if not r:
            return random.choice(NOT_FOUND_RESPONSE)
        a = r[0]['a']
        t = random.choice(FOUND_RESPONSE)
        return t.format(q=q,a=a)

    @re_botcmd(pattern=r"(^| )what? is (the )?(?P<q>\w+)(\?| |$)", prefixed=False, flags=re.IGNORECASE)
    def look_whatis(self, msg, match):
        q = match.group('q')
        return self.getFAQ(q)
    
    @re_botcmd(pattern=r"^(?P<q>\w+)(\?| \?|$)", prefixed=True, flags=re.IGNORECASE)
    def look_for_word(self, msg, match):
        q = match.group('q')
        return self.getFAQ(q)

    @re_botcmd(pattern=r"^(?P<q>\w+) is (?P<a>[^$]+)$", prefixed=True, flags=re.IGNORECASE)
    def learn_definition(self, msg, match):
        q = match.group('q')
        a = match.group('a')
        if q.lower() in ['what', 'why', 'who', 'when', 'how']:
            return
        return self.addFAQ(q, a)

    @re_botcmd(pattern=r"^(forget|remove|clear|unset) (?P<q>\w+)", prefixed=True, flags=re.IGNORECASE)
    def forget_definition(self, msg, match):
        q = match.group('q')
        return self.remFAQ(q)
