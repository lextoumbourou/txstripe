# Stripe Twisted bindings

[![Build Status](https://travis-ci.org/lextoumbourou/txstripe.svg?branch=master)](https://travis-ci.org/lextoumbourou/txstripe)
[![Coverage Status](https://coveralls.io/repos/lextoumbourou/txstripe/badge.svg?branch=master&service=github)](https://coveralls.io/github/lextoumbourou/txstripe?branch=master)

## Installation

```
> pip install txstripe
```

## Usage

Works exactly like [stripe-python](https://github.com/stripe/stripe-python) except each blocking method returns a [Deferred](http://twistedmatrix.com/documents/current/core/howto/defer.html).

## Examples

### In the REPL

```python
$ python -m twisted.conch.stdio
>>> import txstripe
>>> txstripe.api_key = 'ABC123'
>>> txstripe.Customer.all()
<Deferred #0>
Deferred #0 called back: <ListObject list at 0x7f81ddb55eb0> JSON: {
  "data": [
    {
      "account_balance": 0,
      "created": 1441869100,
      "currency": "usd",
      "default_source": "card_123456",
      "delinquent": false,
      "description": "Customer for Bill",
      "discount": null,
      "email": "bill@gmail.com",
      "id": "cus_blah",
      "livemode": false,
      "metadata": {},
      "object": "customer",
      "shipping": null,
      "sources": {
       #...
```

### In code

```python
from twisted.internet import reactor
from twisted.internet import defer

import txstripe
txstripe.api_key = 'ABC123'


@defer.inlineCallbacks
def print_customers_and_subs():
    customer = yield txstripe.Customer.all()
    print customer


if __name__ == "__main__":
    deferred = print_customers_and_subs()
    deferred.addErrback(lambda err: err.printTraceback())
    deferred.addCallback(lambda _: reactor.stop())
    reactor.run()
```

## Changelog

### 0.0.4

* Ensure urls passed to Treq are bytes, not unicode.
* Test coverage.

### 0.0.3

* First working version.

## License

MIT. As per [original project](https://github.com/stripe/stripe-python).
