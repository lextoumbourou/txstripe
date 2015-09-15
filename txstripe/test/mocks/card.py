import json

retrieve_success = json.loads('''{
  "id": "card_1234",
  "object": "card",
  "last4": "9876",
  "brand": "Visa",
  "funding": "credit",
  "exp_month": 3,
  "exp_year": 2017,
  "country": "US",
  "name": "johnny@gmail.com",
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
  "customer": null
}''')
