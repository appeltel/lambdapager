"""
pager module

LambdaPager class and any required helper functions
"""
import shlex
from ConfigParser import ConfigParser

import requests
from twilio.rest import TwilioRestClient


class LambdaPager(object):
    """
    _LambdaPager_

    """
    def __init__(self, configfile='lambdapager.conf', config_dict=None):
        """
        Set up config
        """
        if config_dict is not None:
            self.config = config_dict
            return

        conf = ConfigParser()
        conf.read(configfile)
        self.config =  {sec:dict(conf.items(sec)) for sec in conf.sections()}

    def check_site(self, settings):
        """
        Check site for status code and response string,
        page on failure.
        """
        url = settings.get('url')
        method = settings.get('method', 'GET')

        status_string = settings.get('status_codes', '200,201,202')
        status_codes = [int(code) for code in status_string.split(',')]
        response_reqs_raw = settings.get('response_contains', None)
        if response_reqs_raw is not None:
            splitter = shlex.shlex(response_reqs_raw, posix=True)
            splitter.whitespace = ','
            response_reqs = [item for item in splitter if item.strip()]
        else:
            response_reqs = []

        error = None

        session = requests.Session()
        try:
            resp = session.request(method, url)
        except Exception:
            error = 'Error: {0} to {1} failed'.format(method, url)
        else:
            if resp.status_code not in status_codes:
                error = (
                    'Error: {0} to {1} resulted in status code {2}' 
                    .format(method, url, resp.status_code)
                )
            for req in response_reqs:
                if req not in resp.text:
                    error = (
                        'Error: {0} to {1} is missing the string: {2}' 
                        .format(method, url, req)
                    )

        if error is not None:
            self.page(error)

    def page(self, msg):
        """
        Send texts to everyone on duty with message
        """
        client = TwilioRestClient(
            self.config['twilio']['sid'],
            self.config['twilio']['token'],
        )

        operators = self.config['pager']['onduty'].split(',')
        for op in operators:
            client.messages.create(
                body=msg,
                to=op.strip(),
                from_=self.config['twilio']['number']
            ) 

    def run(self):
        """
        Check sites and page!
        """
        tests = [
            self.config[sec] for sec in self.config.keys() 
                             if sec.startswith('site-')
        ]
        for test in tests:
            self.check_site(test)
