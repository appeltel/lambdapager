"""
_test_pager_

Tests for the pager module and LambdaPager class.

Here I don't provide full integration testing or individual unit tests,
but due to the nature and simplicity of the pager, test that for a given
configuration the pager makes the correct requests and twilio API calls
through mocks.
"""
import os
import unittest
from StringIO import StringIO

import mock
import requests
import requests.exceptions

from lambdapager import LambdaPager


class MockRequest(mock.Mock):
    """
    This Mock subclass is used to handle requests and return a
    requests.Response object whose properties depend on the
    specific request. By default all requests will raise a
    ConnectionError.

    Valid urls can be added as keys to the urls attribute of the
    object:

    mr = MockRequest()
    mr.urls['http://www.foo.com/index.html'] = {
        'methods': ['GET'],
        'status': 200,
        'data': 'Hello World!'
    }        
    """
    def __init__(self, *args, **kwargs):
        super(MockRequest, self).__init__(*args, **kwargs)
        self.side_effect = self.handle
        self.urls = {}

    def handle(self, method, url, **kwargs):
        """
        return a response to an incoming request or raise ConnectionError
        """
        if url not in self.urls:
            raise requests.exceptions.ConnectionError()

        resp = requests.Response()
        conf = self.urls[url]

        if method not in conf['methods']:
            resp.status_code = 403
            resp.raw = StringIO('Method Forbidden')
            return resp

        resp.status_code = conf.get('status', 200)
        resp.raw = StringIO(conf.get('data', ''))
        return resp


class PagerTests(unittest.TestCase):
    """
    Tests for the LambdaPager
    """
    def setUp(self):
        """
        Mock out lambdapager.pager.Session and provide a
        MockRequest object. Also mock TwilioRestClient.
        """
        self.session_patcher = mock.patch('requests.Session')
        self.mock_session_cons = self.session_patcher.start()
        self.mock_session = mock.Mock()
        self.mock_requests = MockRequest()
        self.mock_session.request.side_effect = self.mock_requests
        self.mock_session_cons.return_value = self.mock_session

        self.twilio_patcher = mock.patch('lambdapager.pager.TwilioRestClient')
        self.mock_twilio = self.twilio_patcher.start()
        self.mock_client = mock.Mock()
        self.mock_twilio.return_value = self.mock_client

    def tearDown(self):
        self.session_patcher.stop()
        self.twilio_patcher.stop()

    def test_pager_basicconfig_success(self):
        """
        Test that the 'basic' test scenario checks the configured sites
        and does not page when all sites succeed.
        """
        self.mock_requests.urls['https://www.basic.com/'] = {
            'methods': ['GET'],
            'status': 200,
            'data': '{"ok": true}'
        }
        self.mock_requests.urls['https://www.basic.com/fish/'] = {
            'methods': ['PUT'],
            'status': 201,
            'data': '{"ok": "created"}'
        }
        
        lp = LambdaPager(configfile='data/basic.conf')
        lp.run()

        self.mock_requests.assert_any_call(
            'GET',
            'https://www.basic.com/'
        )
        self.mock_requests.assert_any_call(
            'PUT',
            'https://www.basic.com/fish/'
        )
        self.assertFalse(self.mock_client.messages.create.called)

    def test_pager_basicconfig_connection_failure(self):
        """
        Test that the 'basic' test scenario checks the configured sites
        and pages all numbers once when a single test fails
        due to a connection error
        """
        self.mock_requests.urls['https://www.basic.com/'] = {
            'methods': ['GET'],
            'status': 200,
            'data': '{"ok": true}'
        }
        
        lp = LambdaPager(configfile='data/basic.conf')
        lp.run()

        self.mock_requests.assert_any_call(
            'GET',
            'https://www.basic.com/'
        )
        self.mock_requests.assert_any_call(
            'PUT',
            'https://www.basic.com/fish/'
        )
        self.mock_client.messages.create.assert_any_call(
            body=mock.ANY,
            to='+12025550001',
            from_='+12025559999'
        )
        self.mock_client.messages.create.assert_any_call(
            body=mock.ANY,
            to='+12025550002',
            from_='+12025559999'
        )

    def test_pager_text_config_success(self):
        """
        Test that the 'text' test scenario checks the configured sites
        and does not page when all sites succeed and return the required
        text strings "cat dog" and "bird2"
        """
        self.mock_requests.urls['https://www.text.com/'] = {
            'methods': ['GET'],
            'status': 200,
            'data': '{"pets": "cat dog pig", "else": "bird2"}'
        }
        
        lp = LambdaPager(configfile='data/text.conf')
        lp.run()

        self.mock_requests.assert_called_once_with(
            'GET',
            'https://www.text.com/'
        )
        self.assertFalse(self.mock_client.messages.create.called)

    def test_pager_text_config_missing_string(self):
        """
        Test that the 'text' test scenario checks the configured sites
        and pages when all sites succeed but don't return the required
        text string "bird2"
        """
        self.mock_requests.urls['https://www.text.com/'] = {
            'methods': ['GET'],
            'status': 200,
            'data': '{"pets": "cat dog pig", "else": "bird7"}'
        }
        
        lp = LambdaPager(configfile='data/text.conf')
        lp.run()

        self.mock_requests.assert_called_once_with(
            'GET',
            'https://www.text.com/'
        )
        self.mock_client.messages.create.assert_called_once_with(
            body=mock.ANY,
            to='+12025550001',
            from_='+12025559999'
        )

    def test_pager_text_config_missing_string_quoted(self):
        """
        Test that the 'text' test scenario checks the configured sites
        and pages when all sites succeed but don't return the required
        text string in quotes "cat dog" although both "cat" and "dog"
        are in the response.
        """
        self.mock_requests.urls['https://www.text.com/'] = {
            'methods': ['GET'],
            'status': 200,
            'data': '{"pets": "dog pig cat", "else": "bird2"}'
        }
        
        lp = LambdaPager(configfile='data/text.conf')
        lp.run()

        self.mock_requests.assert_called_once_with(
            'GET',
            'https://www.text.com/'
        )
        self.mock_client.messages.create.assert_called_once_with(
            body=mock.ANY,
            to='+12025550001',
            from_='+12025559999'
        )
