import os
import re
import time
from subprocess import check_output, CalledProcessError
import sys
sys.path.append('/labhome/roid/scripts/mars')
from mlxmars import get_sessions, parse_session_details

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
font = {
    'weight' : 'normal',
    'size'   : 14
}
mpl.rc('font', **font)

from errbot import BotPlugin, botcmd, re_botcmd, webhook


MARS_REPORT_CHANNEL = "#ovs-regression"


class MarsPlugin(BotPlugin):
    def __exec(self, cmd):
        return check_output(cmd.split()).decode()

    def get_last_session_details(self):
        s = get_sessions()
        last_s = s[0]
        return parse_session_details(last_s['session_id'])

    def generate_pie_chart(self, pie, qs):
        self.__exec('rm -f '+pie)
        #out = self.__exec('/labhome/roid/scripts/mars/pie_demo.py --out '+pie)

        data = {
            'Passed': qs['passed'],
            'Failed': qs['failed'],
            'Ignored': qs['ignored'],
            'Not Executed': qs['notexecuted'],
        }

        labels = ['Passed %s' % qs['passed'],
                  'Failed %s' % qs['failed'],
                  'Ignored %s' % qs['ignored'],
                  'Not Executed %s' % qs['notexecuted'],
                  ]
        colors = ['lightgreen', 'lightcoral', 'gold', 'lightgray']
        sizes = [qs['passed'], qs['failed'], qs['ignored'], qs['notexecuted']]

        r = plt.pie(sizes, colors=colors, shadow=True, startangle=90)

        patches = r[0]
        texts = r[-1]

        for pie_wedge in patches:
            pie_wedge.set_edgecolor('black')

        plt.legend(patches, labels, loc="best")
        plt.tight_layout()
        plt.axis('equal')

        plt.savefig(pie)

        return os.path.exists(pie)

    @botcmd
    def mars(self, msg, args):
        yield 'on it..'
        session_details = self.get_last_session_details()
        return self.send_report(session_details, msg.frm)

    def send_report(self, session_details, to):
        r = session_details
        qs = r['quick_summary']
        # prep ahead in case something is missing
        session_id = r['session_id']
        setup = r['setup']['name']
        conf = r['setup']['conf_file_short']
        final_result = r['final_result']
        status = r['session_setup_info']['STATUS']
        start_time = r['start_time']
        end_time = r['end_time']

        pie = '/tmp/pie.png'
        pie_created = self.generate_pie_chart(pie, qs)
        if not pie_created:
            return 'failed creating pie chart'

        pie_posted = self.post_pie(to, pie)
        if not pie_posted:
            return 'failed posting pie chart'

        color = 'green' if final_result == 'Passed' else 'red'

        fields = [
            ('Session id', session_id),
            ('Result', final_result),
            ('Start time', start_time),
            ('End time', end_time),
        ]

        body = ''

        failed_cases = [x['test']+'/'+x['case'] for x in r['quick_case_result'] if x['result'] == 'Failed']
        if len(failed_cases) > 10:
            failed_cases = failed_cases[:10]
            failed_cases.append('...')

        if failed_cases:
            body = '*Failed cases*\n' + '\n'.join(failed_cases)

        self.send_card(title='Mars result for %s/%s' % (setup, conf),
                       body=body,
                       fields=fields,
                       color=color,
                       to=to)

        return 'ok'

    def _wait_for_success(self, stream):
        _timeout = 6
        _wait = 1
        while True:
            if stream.status == 'success':
                return True
            time.sleep(1)
            _wait += 1
            if _wait >= _timeout:
                break
        return False

    def post_pie(self, to, pie):
        stream = self.send_stream_request(to, open(pie, 'rb'),
                                          name=os.path.basename(pie),
                                          stream_type='image/png')

        return self._wait_for_success(stream)

    @webhook('/mars_session_end/<session>/')
    def mars_session_end(self, request, session):
        try:
            session = int(session)
        except ValueError:
            return 'bad session'

        self.log.info('Fetching session details %s' % session)
        details = parse_session_details(session)
        if not details:
            return 'no such session'

        self.log.info('Sending report to %s' % MARS_REPORT_CHANNEL)
        to = self.build_identifier(MARS_REPORT_CHANNEL)
        self.send(to, 'Mars session %s completed, fetching report' % session)
        return self.send_report(details, to)
