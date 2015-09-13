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


class CustomerTest(BaseTest):

    """Test txstripe.Customer class."""

    @defer.inlineCallbacks
    def test_customer_retrieve(self):
        """Method should return a deferred and correct JSON response."""
        self.mocked_resp = mocks.Customer.retrieve_success
        self.resp_mock.code = 200

        d = self.txstripe.Customer.retrieve('something_123')
        self.assertIsInstance(d, defer.Deferred)

        customer = yield d
        self.assertEquals(customer.id, mocks.Customer.retrieve_success['id'])

    @defer.inlineCallbacks
    def test_customer_delete(self):
        """Method should return a deferred and correct JSON response."""
        self.mocked_resp = mocks.Customer.retrieve_success
        self.resp_mock.code = 200

        customer = yield self.txstripe.Customer.retrieve('something_123')

        self.mocked_resp = mocks.Customer.delete_success
        self.resp_mock.code = 200
        d = customer.delete()
        self.assertIsInstance(d, defer.Deferred)

        result = yield d
        self.assertEquals(result.deleted, True)
        self.assertEquals(result.id, mocks.Customer.delete_success['id'])


class PlanTest(BaseTest):

    """Test txstripe.Plan class."""

    def test_plan_create(self):
        """Method should return a deferred."""
        self.mocked_resp = mocks.Plan.create_success
        self.resp_mock.code = 200

        d = self.txstripe.Plan.create(
            amount=2000,
            interval='month',
            name='Amazing Gold Plan',
            currency='aud',
            id='gold'
        )
        self.assertIsInstance(d, defer.Deferred)

    @defer.inlineCallbacks
    def test_plan_update(self):
        """Method should return a deferred."""
        self.mocked_resp = mocks.Plan.create_success
        self.resp_mock.code = 200

        plan = yield self.txstripe.Plan.create(
            amount=2000,
            interval='month',
            name='Gold Special',
            currency='aud',
            id='gold'
        )
        plan.name = 'Test!'
        self.mocked_resp = mocks.Plan.retrieve_success
        self.resp_mock.code = 200

        d = plan.save()
        self.assertIsInstance(d, defer.Deferred)

        yield d
        self.assertEquals(plan.name, 'Test!')
