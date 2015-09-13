"""Stripe utils and some custom stuff."""

import treq

from twisted.internet import defer

from stripe.util import *  # noqa
from stripe.resource import convert_to_stripe_object

from txstripe import error

import txstripe


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

    abs_url = '%s%s' % (txstripe.api_base, url)

    ua = {
        'lang': 'python',
        'publisher': 'lextoumbourou',
        'httplib': 'Twisted',
    }

    headers = headers or {}
    headers.update({
        'X-Stripe-Client-User-Agent': json.dumps(ua),
        'User-Agent': 'txstripe',
        'Authorization': 'Bearer %s' % (txstripe.api_key,)
    })

    if stripe_account:
        headers['Stripe-Account'] = stripe_account

    if txstripe.api_version is not None:
        headers['Stripe-Version'] = txstripe.api_version

    resp = yield treq.request(
        method, abs_url, params=params, headers=headers, **kwargs)

    if resp.code >= 400:
        yield handle_api_error(resp)
        return

    body = yield resp.json()

    defer.returnValue(
        convert_to_stripe_object(body, txstripe.api_key, stripe_account))


@defer.inlineCallbacks
def handle_api_error(resp):
    """Stolen straight from the Stripe Python source."""
    content = yield resp.json()

    headers = HeaderWrapper(resp.headers)

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


class HeaderWrapper(dict):

    """Simple wrapper for Twisted headers to behave like a dict."""

    def __init__(self, headers):
        self.headers = headers

    def __getitem__(self, name):
        headers = self.headers.getRawHeaders(name, None)
        if headers:
            return headers

        raise KeyError(name)
