"""Stripe utils and some custom stuff."""

from twisted.internet import defer

from stripe.util import *  # noqa

from txstripe import error


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
