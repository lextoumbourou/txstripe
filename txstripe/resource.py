"""Override all the things."""

import warnings

from twisted.internet import defer
import treq
import stripe
from stripe.resource import (
    Reversal as StripeReversal,
    ApplicationFeeRefund as StripeApplicationFeeRefund,
    populate_headers
)
from stripe.api_requestor import _api_encode

import txstripe

from txstripe import util, api_key, error


def convert_to_stripe_object(resp, api_key, account):
    types = {'account': Account, 'charge': Charge, 'customer': Customer,
             'invoice': Invoice, 'invoiceitem': InvoiceItem,
             'plan': Plan, 'coupon': Coupon, 'token': Token, 'event': Event,
             'transfer': Transfer, 'list': ListObject, 'recipient': Recipient,
             'bank_account': BankAccount,
             'card': Card, 'application_fee': ApplicationFee,
             'subscription': Subscription, 'refund': Refund,
             'file_upload': FileUpload,
             'fee_refund': ApplicationFeeRefund,
             'bitcoin_receiver': BitcoinReceiver,
             'bitcoin_transaction': BitcoinTransaction,
             'transfer_reversal': Reversal}

    if isinstance(resp, list):
        return [convert_to_stripe_object(i, api_key, account) for i in resp]
    elif isinstance(resp, dict) and not isinstance(resp, StripeObject):
        resp = resp.copy()
        klass_name = resp.get('object')
        if isinstance(klass_name, basestring):
            klass = types.get(klass_name, StripeObject)
        else:
            klass = StripeObject
        return klass.construct_from(resp, api_key, stripe_account=account)
    else:
        return resp


stripe.resource.convert_to_stripe_object = convert_to_stripe_object


@defer.inlineCallbacks
def make_request(
    ins, method, url, stripe_account=None, params=None, headers=None, **kwargs
):
    """
    Return a deferred or handle error.

    For overriding in various classes.
    """
    if txstripe.api_key is None:
        raise error.AuthenticationError(
            'No API key provided. (HINT: set your API key using '
            '"stripe.api_key = <API-KEY>"). You can generate API keys '
            'from the Stripe web interface.  See https://stripe.com/api '
            'for details, or email support@stripe.com if you have any '
            'questions.')

    abs_url = '{}{}'.format(txstripe.api_base, url)

    ua = {
        'lang': 'python',
        'publisher': 'lextoumbourou',
        'httplib': 'Twisted',
    }

    headers = headers or {}
    headers.update({
        'X-Stripe-Client-User-Agent': util.json.dumps(ua),
        'User-Agent': 'txstripe',
        'Authorization': 'Bearer %s' % (txstripe.api_key,)
    })

    if stripe_account:
        headers['Stripe-Account'] = stripe_account

    if txstripe.api_version is not None:
        headers['Stripe-Version'] = txstripe.api_version

    if method == 'get' or method == 'delete':
        data = None
    elif method == 'post':
        data = {k: v for (k, v) in _api_encode(params)}
        params = None
    else:
        raise error.APIConnectionError(
            'Unrecognized HTTP method %r.  This may indicate a bug in the '
            'Stripe bindings.' % (method,))

    resp = yield treq.request(
        method, abs_url, params=params, data=data, headers=headers, **kwargs)

    if resp.code >= 400:
        yield util.handle_api_error(resp)
        return

    body = yield resp.json()

    defer.returnValue(
        convert_to_stripe_object(
            body, txstripe.api_key, stripe_account))


class StripeObject(stripe.StripeObject):

    """Override blocking method."""

    def request(self, method, url, params=None, headers=None):
        """Return a deferred."""
        if params is None:
            params = self._retrieve_params

        return make_request(
            self, method, url, stripe_account=self.stripe_account,
            params=params, headers=headers)


class APIResource(StripeObject, stripe.APIResource):

    """Override blocking methods."""

    @classmethod
    def retrieve(cls, id, api_key=None, **params):
        """Return a deferred."""
        instance = cls(id, api_key, **params)
        d = instance.refresh()
        return d.addCallback(lambda _: instance)

    def refresh(self):
        """Return a deferred."""
        d = self.request('get', self.instance_url())
        return d.addCallback(self.refresh_from).addCallback(lambda _: self)

    @classmethod
    def class_name(cls):
        """Return parent's instance."""
        return super(APIResource, cls).class_name()

    @classmethod
    def class_url(cls):
        """Return parent's instance."""
        return super(APIResource, cls).class_url()

    def instance_url(self):
        """Return parent's instance."""
        return super(APIResource, self).instance_url()


class ListObject(StripeObject, stripe.ListObject):

    """Mixin overrides request."""

    pass


class SingletonAPIResource(APIResource):

    """Mixin overrides request."""

    @classmethod
    def retrieve(cls, **params):
        return super(SingletonAPIResource, cls).retrieve(None, **params)

    @classmethod
    def class_url(cls):
        cls_name = cls.class_name()
        return "/v1/%s" % (cls_name,)

    def instance_url(self):
        return self.class_url()


class ListableAPIResource(APIResource):

    """Override blocking methods."""

    @classmethod
    def all(cls, api_key=None, idempotency_key=None,
            stripe_account=None, **params):
        """Return a deferred."""
        url = cls.class_url()
        return make_request(
            cls, 'get', url, stripe_acconut=None, params=params)


class CreateableAPIResource(APIResource):

    """Override blocking methods."""

    @classmethod
    def create(
        cls, api_key=None, idempotency_key=None, stripe_account=None, **params
    ):
        """Return a deferred."""
        url = cls.class_url()
        headers = populate_headers(idempotency_key)
        return make_request(
            cls, 'post', url, stripe_account=stripe_account,
            headers=headers, params=params)


class UpdateableAPIResource(APIResource):

    """Override blocking methods."""

    def save(self, idempotency_key=None):
        """Return a deferred."""
        updated_params = self.serialize(None)
        headers = populate_headers(idempotency_key)

        if not updated_params:
            util.logger.debug("Trying to save already saved object %r", self)
            return defer.succeed(self)

        d = self.request('post', self.instance_url(), updated_params, headers)
        return d.addCallback(self.refresh_from).addCallback(lambda _: self)


class DeletableAPIResource(APIResource):

    """Override blocking methods."""

    def delete(self, **params):
        """Return a deferred."""
        d = self.request('delete', self.instance_url(), params)
        return d.addCallback(self.refresh_from).addCallback(lambda _: self)


class Account(CreateableAPIResource, ListableAPIResource,
              UpdateableAPIResource, DeletableAPIResource, stripe.Account):

    """Override blocking methods."""

    @classmethod
    def retrieve(cls, id=None, api_key=None, **params):
        """Return a deferred."""
        instance = cls(id, api_key, **params)
        d = instance.refresh()
        return d.addCallback(lambda _: instance)

    def instance_url(self):
        return super(Account, self).instance_url()


class Balance(SingletonAPIResource):

    """Override blocking methods."""

    pass


class Card(UpdateableAPIResource, DeletableAPIResource, stripe.Card):

    """Override blocking methods."""

    def instance_url(self):
        """Return parent method."""
        return super(Card, self).instance_url()

    @classmethod
    def retrieve(cls, *args, **kwargs):
        """Return parent method."""
        return super(Card, cls).retrieve(*args, **kwargs)


class BankAccount(UpdateableAPIResource, DeletableAPIResource):

    """Override blocking methods."""

    def instance_url(self):
        """Return parent method."""
        return super(BankAccount, self).instance_url()

    @classmethod
    def retrieve(cls, *args, **kwargs):
        """Return parent method."""
        return super(BankAccount, cls).retrieve(*args, **kwargs)


class Charge(
    CreateableAPIResource, ListableAPIResource, UpdateableAPIResource
):

    """Override blocking methods."""

    def refund(self, idempotency_key=None, **params):
        """Return a deferred."""
        url = self.instance_url() + '/refund'
        headers = populate_headers(idempotency_key)
        d = self.request('post', url, params, headers)
        return d.addCallback(self.refresh_from).addCallback(lambda _: self)

    def capture(self, idempotency_key=None, **params):
        """Return a deferred."""
        url = self.instance_url() + '/capture'
        headers = populate_headers(idempotency_key)
        d = self.request('post', url, params, headers)
        return d.addCallback(self.refresh_from).addCallback(lambda _: self)

    def update_dispute(self, idempotency_key=None, **params):
        """Return a deferred."""
        url = self.instance_url() + '/dispute'
        headers = populate_headers(idempotency_key)
        d = self.request('post', url, params, headers)
        d.addCallback(lambda response: self.refresh_from(
            {'dispute': response}, api_key, True))
        return d.addCallback(lambda _: self.dispute)

    def close_dispute(self, idempotency_key=None):
        """Return a deferred."""
        url = self.instance_url() + '/dispute/close'
        headers = populate_headers(idempotency_key)
        d = self.request('post', url, {}, headers)
        d.addCallback(lambda response: self.refresh_from(
            {'dispute': response}, api_key, True))
        return d.addCallback(lambda _: self.dispute)

    def mark_as_fraudulent(self, idempotency_key=None):
        """Return a deferred."""
        params = {'fraud_details': {'user_report': 'fraudulent'}}
        url = self.instance_url()
        headers = populate_headers(idempotency_key)
        d = self.request('post', url, params, headers)
        return d.addCallback(self.refresh_from).addCallback(lambda _: self)

    def mark_as_safe(self, idempotency_key=None):
        """Return a deferred."""
        params = {'fraud_details': {'user_report': 'safe'}}
        url = self.instance_url()
        headers = populate_headers(idempotency_key)
        d = self.request('post', url, params, headers)
        return d.addCallback(self.refresh_from).addCallback(lambda _: self)


class Dispute(
    CreateableAPIResource, ListableAPIResource, UpdateableAPIResource
):

    """Override blocking methods."""

    def close(self, idempotency_key=None):
        """Return a deferred."""
        url = self.instance_url() + '/close'
        headers = populate_headers(idempotency_key)
        d = self.request('post', url, {}, headers)
        return d.addCallback(self.refresh_from).addCallback(lambda _: self)


class Customer(CreateableAPIResource, UpdateableAPIResource,
               ListableAPIResource, DeletableAPIResource):

    """Override blocking methods."""

    def add_invoice_item(self, idempotency_key=None, **params):
        """Return a deferred."""
        params['customer'] = self.id
        return InvoiceItem.create(
            self.api_key, idempotency_key=idempotency_key, **params)

    def invoices(self, **params):
        """Return a deferred."""
        params['customer'] = self.id
        return Invoice.all(self.api_key, **params)

    def invoice_items(self, **params):
        """Return a deferred."""
        params['customer'] = self.id
        return InvoiceItem.all(self.api_key, **params)

    def charges(self, **params):
        """Return a deferred."""
        params['customer'] = self.id
        return Charge.all(self.api_key, **params)

    def update_subscription(self, idempotency_key=None, **params):
        """Return a deferred."""
        warnings.warn(
            'The `update_subscription` method is deprecated. Instead, use the '
            '`subscriptions` resource on the customer object to update a '
            'subscription',
            DeprecationWarning)
        url = self.instance_url() + '/subscription'
        headers = populate_headers(idempotency_key)
        d = self.request('post', url, params, headers)
        d.addCallback(lambda response: self.refresh_from(
            {'subscription': response}, api_key, True))
        return d.addCallback(lambda _: self.subscription)

    def cancel_subscription(self, idempotency_key=None, **params):
        """Return a deferred."""
        warnings.warn(
            'The `cancel_subscription` method is deprecated. Instead, use the '
            '`subscriptions` resource on the customer object to cancel a '
            'subscription',
            DeprecationWarning)
        url = self.instance_url() + '/subscription'
        headers = populate_headers(idempotency_key)
        d = self.request('delete', url, params, headers)
        d.addCallback(lambda response: self.refresh_from(
            {'subscription': response}, api_key, True))
        return d.addCallback(lambda _: self.subscription)

    def delete_discount(self, **params):
        """Return a deferred."""
        url = self.instance_url() + '/discount'
        d = self.request('delete', url)
        d.addCallback(lambda response: self.refresh_from(
            {'discount': None}, api_key, True))
        return d.addCallback(lambda _: self.subscription)


class Invoice(
    CreateableAPIResource, ListableAPIResource, UpdateableAPIResource
):

    """Override blocking methods."""

    def pay(self, idempotency_key=None):
        """Return a deferred."""
        headers = populate_headers(idempotency_key)
        return self.request('post', self.instance_url() + '/pay', {}, headers)

    @classmethod
    def upcoming(cls, api_key=None, stripe_account=None, **params):
        """Return a deferred."""
        url = cls.class_url() + '/upcoming'
        return cls.request('get', url, params)


class InvoiceItem(
    CreateableAPIResource, UpdateableAPIResource,
    ListableAPIResource, DeletableAPIResource
):

    """Override blocking methods."""

    pass


class Plan(
    CreateableAPIResource, DeletableAPIResource,
    UpdateableAPIResource, ListableAPIResource
):

    """Override blocking methods."""

    pass


class Subscription(
    UpdateableAPIResource, DeletableAPIResource, stripe.Subscription
):

    """Override blocking methods."""

    def instance_url(self):
        """Return parent method."""
        return super(Subscription, self).instance_url()

    @classmethod
    def retrieve(cls, *args, **kwargs):
        """Return parent method."""
        return super(Subscription, cls).retrieve(*args, **kwargs)

    def delete_discount(self, **params):
        """Return a deferred."""
        url = self.instance_url() + '/discount'
        d = self.request('delete', url)
        return d.addCallback(
            lambda _: self.refresh_from({'discount': None}, api_key, True))


class Refund(
    CreateableAPIResource, ListableAPIResource, UpdateableAPIResource
):

    """Override blocking methods."""

    pass


class Token(CreateableAPIResource):

    """Override blocking methods."""

    pass


class Coupon(
    CreateableAPIResource, UpdateableAPIResource,
    DeletableAPIResource, ListableAPIResource
):

    """Override blocking methods."""

    pass


class Event(ListableAPIResource):

    """Override blocking methods."""

    pass


class Transfer(
    CreateableAPIResource, UpdateableAPIResource, ListableAPIResource
):

    """Override blocking methods."""

    def cancel(self):
        """Return a deferred."""
        d = self.request('post', self.instance_url() + '/cancel')
        return d.addCallback(self.refresh_from)


class Reversal(UpdateableAPIResource, StripeReversal):

    """Override blocking methods."""

    def instance_url(self):
        """Return parent method."""
        return super(Reversal, self).instance_url()

    @classmethod
    def retrieve(cls, *args, **kwargs):
        """Return parent method."""
        return super(Reversal, cls).retrieve(*args, **kwargs)


class Recipient(
    CreateableAPIResource, UpdateableAPIResource,
    ListableAPIResource, DeletableAPIResource
):

    """Override blocking methods."""

    def transfers(self, **params):
        """Return a deferred."""
        params['recipient'] = self.id
        return Transfer.all(self.api_key, **params)


class FileUpload(ListableAPIResource, stripe.FileUpload):

    """Override blocking methods."""

    @classmethod
    def api_base(cls):
        """Return parent method."""
        return super(FileUpload, cls).api_base()

    @classmethod
    def class_name(cls):
        """Return parent method."""
        return super(FileUpload, cls).class_name()

    @classmethod
    def create(cls, *args, **kwargs):
        raise NotImplementedError((
            "Haven't got to implementing this yet."
            'Please add an issue on Github if you need it.'))


class ApplicationFee(ListableAPIResource, stripe.ApplicationFee):

    """Override blocking methods."""

    @classmethod
    def class_name(cls):
        """Return parent method."""
        return super(ApplicationFee, cls).class_name()

    def refund(self, idempotency_key=None, **params):
        """Return a deferred."""
        headers = populate_headers(idempotency_key)
        url = self.instance_url() + '/refund'
        d = self.request('post', url, params, headers)
        return d.addCallback(self.refresh_from).addCallback(lambda _: self)


class ApplicationFeeRefund(UpdateableAPIResource, StripeApplicationFeeRefund):

    """Override blocking methods."""

    def instance_url(self):
        """Return parent method."""
        return super(ApplicationFeeRefund, self).instance_url()

    @classmethod
    def retrieve(cls, *args, **kwargs):
        """Return parent method."""
        return super(ApplicationFeeRefund, cls).retrieve(*args, **kwargs)


class BitcoinReceiver(
    CreateableAPIResource, UpdateableAPIResource,
    DeletableAPIResource, ListableAPIResource, stripe.BitcoinReceiver
):

    def instance_url(self):
        """Return parent method."""
        return super(BitcoinReceiver, self).instance_url()

    @classmethod
    def class_url(cls):
        return super(BitcoinReceiver, cls).class_url()


class BitcoinTransaction(StripeObject):

    """Override blocking methods."""

    pass
