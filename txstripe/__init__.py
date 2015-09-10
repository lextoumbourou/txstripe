"""A bunch of monkey patching to make Stripe async."""

import urllib
from twisted.internet import defer
import treq

from stripe import (  # noqa
    api_key, api_base, upload_api_base,
    api_version, verify_ssl_certs, util)

from stripe.resource import (  # noqa
    convert_to_stripe_object,
    populate_headers,
    ListObject,
    CreateableAPIResource,
    ListableAPIResource,
    UpdateableAPIResource,
    DeletableAPIResource,
    Account,
    ApplicationFee,
    Balance,
    BalanceTransaction,
    BankAccount,
    BitcoinReceiver,
    BitcoinTransaction,
    Card,
    Charge,
    Coupon,
    Customer,
    Dispute,
    Event,
    FileUpload,
    Invoice,
    InvoiceItem,
    Plan,
    Recipient,
    Refund,
    Subscription,
    Token,
    Transfer)

from stripe.error import (  # noqa
    APIConnectionError,
    APIError,
    AuthenticationError,
    CardError,
    InvalidRequestError,
    StripeError)


@defer.inlineCallbacks
def _handle_api_error(resp):
    """Stolen straight from the Stripe Python source."""
    content = yield resp.json()
    try:
        err = content['error']
    except (KeyError, TypeError):
        raise APIError(
            "Invalid response object from API: %r (HTTP response code "
            "was %d)" % (content, resp.code),
            content, resp.code, resp)

    if resp.code in [400, 404]:
        raise InvalidRequestError(
            err.get('message'), err.get('param'),
            content, resp.code, resp, resp.headers)
    elif resp.code == 401:
        raise AuthenticationError(
            err.get('message'),
            content, resp.code, resp, resp.headers)
    elif resp.code == 402:
        raise CardError(
            err.get('message'), err.get('param'), err.get('code'),
            content, resp.code, resp, resp.headers)
    else:
        raise APIError(
            err.get('message'), content, resp.code, resp, resp.headers)


@defer.inlineCallbacks
def _request(
    ins, method, url, stripe_account=None, params=None, headers=None, **kwargs
):
    """
    Return a deferred or handle error.

    For overriding in various classes.
    """
    if api_key is None:
        raise AuthenticationError(
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

    if params is None:
        params = ins._retrieve_params

    resp = yield treq.request(
        method, abs_url, params=params, headers=headers, **kwargs)

    if resp.code >= 400:
        yield _handle_api_error(resp)
        return

    body = yield resp.json()

    defer.returnValue(convert_to_stripe_object(body, api_key, stripe_account))


@classmethod
def _all(
    cls, api_key=None, idempotency_key=None, stripe_account=None, **params
):
    """Return a deferred."""
    url = cls.class_url()
    return _request(cls, 'get', url, stripe_acconut=None, params=params)


@classmethod
def _create(
    cls, api_key=None, idempotency_key=None, stripe_account=None, **params
):
    """Return a deferred."""
    url = cls.class_url()
    headers = populate_headers(idempotency_key)
    return _request(
        cls, 'post', url, stripe_account=stripe_account, headers=headers)


def _save(ins, idempotency_key=None):
    """Return a deferred."""
    updated_params = ins.serialize(None)
    headers = populate_headers(idempotency_key)

    if not updated_params:
        util.logger.debug("Trying to save already saved object %r", ins)
        return defer.succeed(ins)

    d = ins.request('post', ins.instance_url(), updated_params, headers)
    return d.addCallback(ins.refresh_from).addCallback(lambda: ins)


def _delete(ins, **params):
    """Return a deferred."""
    d = ins.request('delete', ins.instance_url(), params)
    return d.addCallback(ins.request_from).addCallback(lambda: ins)


def _retrieve_for_id(ins, id, **params):
    base = ins.get('url')
    id = util.utf8(id)
    extn = urllib.quote_plus(id)
    url = "%s/%s" % (base, extn)
    return _request('get', url, params=params)


@classmethod
def _retrieve(cls, id=None, api_key=None, **params):
    instance = cls(id, api_key, **params)
    d = instance.request('get', instance.instance_url())
    return d.addCallback(instance.request_from).addCallback(lambda: instance)


ListObject.request = _request
ListObject.retrieve = _retrieve_for_id
ListObject.create = _create

ListableAPIResource.all = _all

CreateableAPIResource.create = _create
UpdateableAPIResource.save = _save
DeletableAPIResource.delete = _delete
Account.retrieve = _retrieve
