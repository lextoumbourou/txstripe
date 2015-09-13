"""A bunch of monkey patching to make Stripe async."""

import urllib
from twisted.internet import defer
import treq

from stripe import (  # noqa
    api_key, api_base, upload_api_base,
    api_version, verify_ssl_certs)
from stripe.resource import populate_headers

import stripe

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
        return d.addCallback(lambda: instance)

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


class SingletonAPIResource(StripeObject):

    """Mixin overrides request."""

    retrieve = stripe.SingletonAPIResource.retrieve
    class_url = stripe.SingletonAPIResource.class_url
    instance_url = stripe.SingletonAPIResource.instance_url


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


class DeleteableAPIResource(APIResource):

    """Override blocking methods."""

    def delete(self, **params):
        """Return a deferred."""
        d = self.request('delete', self.instance_url(), params)
        return d.addCallback(self.request_from).addCallback(lambda: self)


class Account(CreateableAPIResource, ListableAPIResource,
              UpdateableAPIResource, DeleteableAPIResource, stripe.Account):

    """Override blocking methods."""

    @classmethod
    def retrieve(cls, id=None, api_key=None, **params):
        """Return a deferred."""
        instance = cls(id, api_key, **params)
        d = instance.refresh()
        return d.addCallback(lambda _: instance)

    def instance_url(self):
        return super(Account, self).instance_url()
