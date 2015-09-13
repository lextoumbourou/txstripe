"""Test txstripe resources."""

from twisted.internet import defer

from txstripe.test import BaseTest, mocks


class AccountTest(BaseTest):

    """Test txstripe.Account class."""

    @defer.inlineCallbacks
    def test_create_an_account_returns_deferred(self):
        """Method should return a deferred."""
        self.mocked_resp = mocks.Account.create_success
        self.resp_mock.code = 201

        d = self.txstripe.Account.create(
            managed=False, country='AU', email='bob@example.com')
        self.assertIsInstance(d, defer.Deferred)

        account = yield d
        self.assertEquals(account.id, mocks.Account.create_success['id'])

    @defer.inlineCallbacks
    def test_retrieve_an_account_returns_deferred(self):
        """Method should return a deferred."""
        self.mocked_resp = mocks.Account.retrieve_success
        self.resp_mock.code = 200

        d = self.txstripe.Account.retrieve('someid')
        self.assertIsInstance(d, defer.Deferred)

        account = yield d
        self.assertEquals(account.id, mocks.Account.retrieve_success['id'])

    @defer.inlineCallbacks
    def test_list_an_account_returns_deferred(self):
        """Method should return a deferred."""
        self.mocked_resp = mocks.account.all_success
        self.resp_mock.code = 200

        d = self.txstripe.Account.all()
        self.assertIsInstance(d, defer.Deferred)

        account = yield d
        self.assertEquals(account.to_dict(), mocks.Account.all_success)


class BalanceTest(BaseTest):

    """Test txstripe.Balance class."""

    @defer.inlineCallbacks
    def test_retrieve_returns_deferred(self):
        """Method should return a deferred."""
        self.mocked_resp = mocks.Balance.retrieve_success
        self.resp_mock.code = 200

        d = self.txstripe.Balance.retrieve()
        self.assertIsInstance(d, defer.Deferred)

        balance = yield d
        self.assertEquals(balance.available[1].amount, 497771)
