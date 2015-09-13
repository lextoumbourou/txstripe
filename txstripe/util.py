from stripe.util import *  # noqa


class HeaderWrapper(object):

    """Simple wrapper for Twisted headers to behave a bit like a dict."""

    def __init__(self, headers):
        self.headers = headers

    def get(self, name, default=None):
        headers = self.headers.getRawHeaders(name, None)
        return headers[0] if headers else default
