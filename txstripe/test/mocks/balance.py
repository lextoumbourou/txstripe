import json


retrieve_success = json.loads('''{
  "pending": [
    {
      "amount": 0,
      "currency": "sek"
    },
    {
      "amount": 2703089,
      "currency": "usd"
    }
  ],
  "available": [
    {
      "amount": 0,
      "currency": "sek"
    },
    {
      "amount": 497771,
      "currency": "usd"
    }
  ],
  "livemode": false,
  "object": "balance"
}''')
