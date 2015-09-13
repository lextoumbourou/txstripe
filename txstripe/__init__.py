"""
Stripe Twisted Bindings.

This single function is basically the core of txstripe. Treq makes
the call to the Stripe API instead of a blocking library.

The rest of the codebase is basically monkey patching this in any time
it's needed.
"""

from stripe import (  # noqa
    api_key, api_base, upload_api_base,
    api_version, verify_ssl_certs)

# Configuration variables

api_key = api_key
api_base = api_base
upload_api_base = upload_api_base
api_version = api_version
verify_ssl_certs = verify_ssl_certs

from txstripe.resource import (  # noqa
    Account,
    ApplicationFee,
    Balance,
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

from txstripe.error import (  # noqa
    APIConnectionError,
    APIError,
    AuthenticationError,
    CardError,
    InvalidRequestError,
    StripeError)
