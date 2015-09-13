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
    "data": [

    ]
  },
  "discount": null,
  "account_balance": 0,
  "currency": "aud",
  "sources": {
    "object": "list",
    "total_count": 0,
    "has_more": false,
    "url": "/v1/customers/cus_1234/sources",
    "data": []
  },
  "default_source": null
}''')


delete_success = json.loads('''{
    "deleted": true,
    "id": "something_123"
}''')
