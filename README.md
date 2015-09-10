# Twisted Python bindings

Stripe Python bindings but for Twisted.

## Status

WIP. Don't use yet.

## Usage

Works exactly like [stripe-python](https://github.com/stripe/stripe-python), except each blocking method returns a Deferred.

## Examples

### In the REPL

```
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

```
import txstripe
txstripe.api_key = 'ABC123'


@inlineCallbacks
def print_customers_and_subs():
    customer = yield txstripe.Customer.all()
    print customer


if __name__ == "__main__":
    deferred = print_customers_and_subs()
    deferred.addErrback(lambda err: err.printTraceback())
    deferred.addCallback(lambda _: reactor.stop())
    reactor.run()
```

## Developing

Designed to be as small a port as possible without requiring any of the original dependancies.

## License

MIT. As per [original project](https://github.com/stripe/stripe-python).
