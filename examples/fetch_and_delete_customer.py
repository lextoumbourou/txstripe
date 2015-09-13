from pprint import pprint

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

import txstripe


txstripe.api_key = 'YOUR-API-KEY'


@inlineCallbacks
def example():
    try:
        custs = yield txstripe.Customer.all()
        pprint(custs)
    except Exception as e:
        print e
        return

    try:
        print 'About to create a new customer!'
        new_customer = yield txstripe.Customer.create(
            description='Some customer!')
        pprint(new_customer)
    except Exception as e:
        print e
        return

    print 'Customer created! {}'.format(new_customer)

    try:
        print 'About to delete the customer.'
        deleted = yield new_customer.delete()
    except Exception as e:
        print e
        return

    print 'Customer deleted." {}'.format(deleted)


if __name__ == '__main__':
    df = example()
    df.addErrback(lambda err: err.printTraceback())
    df.addCallback(lambda _: reactor.stop())

    reactor.run()
