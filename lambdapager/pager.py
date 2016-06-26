"""
pager module

LambdaPager class and any required helper functions
"""
from ConfigParser import ConfigParser

import requests
from twilio.rest import TwilioRestClient


class LambdaPager(object):
    """
    _LambdaPager_

    """
    def __init__(self):
        """
        Set up config
        """
        self.get_config()

    def get_config(self, filename='lambdapager.conf'):
        """
        Generate a configuration an ini file and return
        it as a dict of section dicts

        TODO: Find the least hacky way to alternatively
        load the config from a generated python module
        if uploaded to AWS - probably create a config module
        that just has a single var that is the dict.
        """
        conf = ConfigParser()
        conf.read(filename)
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
                             if sec.startswith('test-')
        ]
        for test in tests:
            self.check_site(test)
