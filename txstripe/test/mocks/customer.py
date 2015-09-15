import json


retrieve_success = json.loads('''{
  "object": "customer",
  "created": 1442136572,
  "id": "cus_1234",
  "livemode": false,
  "description": null,
  "email": null,
  "shipping": null,
  "delinquent": false,
  "metadata": {},
  "subscriptions": {
    "object": "list",
    "total_count": 0,
    "has_more": false,
    "url": "/v1/customers/cus_1234/subscriptions",
    "data": [{
      "id": "sub_6yuYOFaUhpWt73",
      "plan": {
        "interval": "month",
        "name": "Small Plan",
        "created": 1441195927,
        "amount": 49900,
        "currency": "usd",
        "id": "small_plan_1",
        "object": "plan",
        "livemode": false,
        "interval_count": 1,
        "trial_period_days": null,
        "metadata": {
        },
        "statement_descriptor": "SCRUNCH SMALL PLAN"
      },
      "object": "subscription",
      "start": 1442236277,
      "status": "active",
      "customer": "cus_6ypxqa4dHSGhbU",
      "cancel_at_period_end": false,
      "current_period_start": 1442236277,
      "current_period_end": 1444828277,
      "ended_at": null,
      "trial_start": null,
      "trial_end": null,
      "canceled_at": null,
      "quantity": 1,
      "application_fee_percent": null,
      "discount": null,
      "tax_percent": null,
      "metadata": {}
    }]
  },
  "discount": null,
  "account_balance": 0,
  "currency": "aud",
  "sources": {
    "object": "list",
    "total_count": 0,
    "has_more": false,
    "url": "/v1/customers/cus_1234/sources",
    "data": [{
      "id": "card_1234",
      "object": "card",
      "last4": "1881",
      "brand": "Visa",
      "funding": "credit",
      "exp_month": 3,
      "exp_year": 2017,
      "country": "US",
      "name": "lextoumbourou@hello.com",
      "address_line1": null,
      "address_line2": null,
      "address_city": null,
      "address_state": null,
      "address_zip": null,
      "address_country": null,
      "cvc_check": "pass",
      "address_line1_check": null,
      "address_zip_check": null,
      "tokenization_method": null,
      "dynamic_last4": null,
      "metadata": {},
      "customer": "abc_1234"
    }]
  },
  "default_source": null
}''')


delete_success = json.loads('''{
    "deleted": true,
    "id": "something_123"
}''')
