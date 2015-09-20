import json


retrieve_success = json.loads('''{
  "id": "ch_1234",
  "object": "charge",
  "created": 1442723274,
  "livemode": false,
  "paid": true,
  "status": "succeeded",
  "amount": 100,
  "currency": "aud",
  "refunded": false,
  "source": {
    "id": "card_1234",
    "object": "card",
    "last4": "4242",
    "brand": "Visa",
    "funding": "credit",
    "exp_month": 8,
    "exp_year": 2016,
    "country": "US",
    "name": null,
    "address_line1": null,
    "address_line2": null,
    "address_city": null,
    "address_state": null,
    "address_zip": null,
    "address_country": null,
    "cvc_check": null,
    "address_line1_check": null,
    "address_zip_check": null,
    "tokenization_method": null,
    "dynamic_last4": null,
    "metadata": {
    },
    "customer": null
  },
  "captured": true,
  "balance_transaction": "txn_234",
  "failure_message": null,
  "failure_code": null,
  "amount_refunded": 0,
  "customer": null,
  "invoice": null,
  "description": "Some refund",
  "dispute": null,
  "metadata": {},
  "statement_descriptor": null,
  "fraud_details": {},
  "receipt_email": null,
  "receipt_number": null,
  "shipping": null,
  "destination": null,
  "application_fee": null,
  "refunds": {
    "object": "list",
    "total_count": 0,
    "has_more": false,
    "url": "/v1/charges/ch_1234/refunds",
    "data": [

    ]
  }
}''')
