# Twisted Python bindings

Stripe Python bindings but for Twisted.

## Status

WIP. Don't use yet.

## Usage

Exactly what the docs say, but each method returns a Deferred.

## Examples

### In the REPL

```
> pip install twisted
> python -m twisted.conch.stdio
>>> import txstripe
>>>
>>> txstripe.api_key = 'YADDA'
>>> txstripe.Customer.all()
Deferred returns...
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
