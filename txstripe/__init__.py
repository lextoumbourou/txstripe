"""
Stripe Twisted Bindings.

A bunch of monkey patching to make the stripe-python library play nice with Twisted.
"""

import warnings

from twisted.internet import defer
import treq

from stripe import (  # noqa
    api_key, api_base, upload_api_base,
    api_version, verify_ssl_certs)
from stripe.resource import populate_headers

import stripe
from stripe.resource import Reversal as StripeReversal
from stripe.resource import ApplicationFeeRefund as StripeApplicationFeeRefund

from txstripe import error, util


@defer.inlineCallbacks
def _handle_api_error(resp):
    """Stolen straight from the Stripe Python source."""
    content = yield resp.json()

    headers = util.HeaderWrapper(resp.headers)

    try:
        err = content['error']
    except (KeyError, TypeError):
        raise error.APIError(
            "Invalid response object from API: %r (HTTP response code "
            "was %d)" % (content, resp.code),
            resp, resp.code, content, headers)

    if resp.code in [400, 404]:
        raise error.InvalidRequestError(
            err.get('message'), err.get('param'),
            resp, resp.code, content, headers)
    elif resp.code == 401:
        raise error.AuthenticationError(
            err.get('message'),
            resp, resp.code, content, headers)
    elif resp.code == 402:
        raise error.CardError(
            err.get('message'), err.get('param'), err.get('code'),
            content, resp.code, resp, headers)
    else:
        raise error.APIError(
            err.get('message'), content, resp.code, resp, headers)


@defer.inlineCallbacks
def _request(
    ins, method, url, stripe_account=None, params=None, headers=None, **kwargs
):
    """
    Return a deferred or handle error.

    For overriding in various classes.
    """
    if api_key is None:
        raise error.AuthenticationError(
            'No API key provided. (HINT: set your API key using '
            '"stripe.api_key = <API-KEY>"). You can generate API keys '
            'from the Stripe web interface.  See https://stripe.com/api '
            'for details, or email support@stripe.com if you have any '
            'questions.')

    abs_url = '%s%s' % (api_base, url)

    ua = {
        'lang': 'python',
        'publisher': 'lextoumbourou',
        'httplib': 'Twisted',
    }

    headers = headers or {}
    headers.update({
        'X-Stripe-Client-User-Agent': util.json.dumps(ua),
        'User-Agent': 'txstripe',
        'Authorization': 'Bearer %s' % (api_key,)
    })

    if stripe_account:
        headers['Stripe-Account'] = stripe_account

    if api_version is not None:
        headers['Stripe-Version'] = api_version

    resp = yield treq.request(
        method, abs_url, params=params, headers=headers, **kwargs)

    if resp.code >= 400:
        yield _handle_api_error(resp)
        return

    body = yield resp.json()

    defer.returnValue(
        stripe.convert_to_stripe_object(body, api_key, stripe_account))


class StripeObject(stripe.StripeObject):

    """Override blocking method."""

    def request(self, method, url, params=None, headers=None):
        """Return a deferred."""
        if params is None:
            params = self._retrieve_params

        return _request(
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


class ListObject(StripeObject):

    """Mixin overrides request."""

    all = stripe.ListObject.all
    create = stripe.ListObject.create
    retrieve = stripe.ListObject.retrieve


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
        return _request(cls, 'get', url, stripe_acconut=None, params=params)


class CreateableAPIResource(APIResource):

    """Override blocking methods."""

    @classmethod
    def create(
        cls, api_key=None, idempotency_key=None, stripe_account=None, **params
    ):
        """Return a deferred."""
        url = cls.class_url()
        headers = populate_headers(idempotency_key)
        return _request(
            cls, 'post', url, stripe_account=stripe_account, headers=headers)


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
        return d.addCallback(self.refresh_from).addCallback(lambda: self)


class DeletableAPIResource(APIResource):

    """Override blocking methods."""

    def delete(self, **params):
        """Return a deferred."""
        d = self.request('delete', self.instance_url(), params)
        return d.addCallback(self.request_from).addCallback(lambda: self)


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
        return d.addCallback(self.refresh_from).addCallback(lambda: self)

    def capture(self, idempotency_key=None, **params):
        """Return a deferred."""
        url = self.instance_url() + '/refund'
        headers = populate_headers(idempotency_key)
        d = self.request('post', url, params, headers)
        return d.addCallback(self.refresh_from).addCallback(lambda: self)

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
        return d.addCallback(self.refresh_from).addCallback(lambda: self)

    def mark_as_safe(self, idempotency_key=None):
        """Return a deferred."""
        params = {'fraud_details': {'user_report': 'safe'}}
        url = self.instance_url()
        headers = populate_headers(idempotency_key)
        d = self.request('post', url, params, headers)
        return d.addCallback(self.refresh_from).addCallback(lambda: self)


class Dispute(
    CreateableAPIResource, ListableAPIResource, UpdateableAPIResource
):

    """Override blocking methods."""

    def close(self, idempotency_key=None):
        """Return a deferred."""
        url = self.instance_url() + '/close'
        headers = populate_headers(idempotency_key)
        d = self.request('post', url, {}, headers)
        return d.addCallback(self.refresh_from).addCallback(lambda: self)


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
