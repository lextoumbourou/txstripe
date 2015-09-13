"""Test txstripe."""

from mock import patch, Mock

from twisted.trial.unittest import TestCase
from twisted.internet import defer

import txstripe
from txstripe.test import mocks


class BaseTest(TestCase):

    """Default settings for all tests."""

    def _json_mock(self):
        return self.mocked_resp

    def setUp(self):
        self._mocked_resp = {}

        self.resp_mock = Mock()
        self.resp_mock.json = self._json_mock

        treq_patch = patch('txstripe.treq')
        self.treq_mock = treq_patch.start()
        self.treq_mock.request.return_value = defer.succeed(self.resp_mock)

        self.txstripe = txstripe
        self.txstripe.api_key = 'ABC123'


class AccountTest(BaseTest):

    """Test txstripe.Account class."""

    @defer.inlineCallbacks
    def test_create_an_account_returns_deferred(self):
        """Method should return a deferred."""
        self.mocked_resp = mocks.Account_create_success
        self.resp_mock.code = 201

        d = self.txstripe.Account.create(
            managed=False, country='AU', email='bob@example.com')
        self.assertIsInstance(d, defer.Deferred)

        account = yield d
        self.assertEquals(account.id, mocks.Account_create_success['id'])

    @defer.inlineCallbacks
    def test_retrieve_an_account_returns_deferred(self):
        """Method should return a deferred."""
        self.mocked_resp = mocks.Account_retrieve_success
        self.resp_mock.code = 200

        d = self.txstripe.Account.retrieve('someid')
        self.assertIsInstance(d, defer.Deferred)

        account = yield d
        self.assertEquals(account.id, mocks.Account_retrieve_success['id'])

    @defer.inlineCallbacks
    def test_list_an_account_returns_deferred(self):
        """Method should return a deferred."""
        self.mocked_resp = mocks.Account_all_success
        self.resp_mock.code = 200

        d = self.txstripe.Account.all()
        self.assertIsInstance(d, defer.Deferred)

        account = yield d
        self.assertEquals(account.to_dict(), mocks.Account_all_success)
