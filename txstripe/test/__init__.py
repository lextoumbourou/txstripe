"""Test txstripe."""

from mock import patch, Mock

from twisted.trial.unittest import TestCase
from twisted.internet import defer


class BaseTest(TestCase):

    """Default settings for all tests."""

    def _json_mock(self):
        return self.mocked_resp

    def _request_mock(self, *args, **kwargs):
        return defer.succeed(self.resp_mock)

    def setUp(self):
        self._mocked_resp = {}

        self.resp_mock = Mock()
        self.resp_mock.json = self._json_mock

        treq_patch = patch('txstripe.resource.treq')
        self.treq_mock = treq_patch.start()
        self.treq_mock.request.side_effect = self._request_mock

        import txstripe
        txstripe.api_key = 'ABC123'
        self.txstripe = txstripe
