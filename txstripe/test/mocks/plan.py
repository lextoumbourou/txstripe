import json


create_success = json.loads('''{
  "interval": "month",
  "name": "Gold Special",
  "created": 1442136520,
  "amount": 2000,
  "currency": "aud",
  "id": "gold",
  "object": "plan",
  "livemode": false,
  "interval_count": 1,
  "trial_period_days": null,
  "metadata": {},
  "statement_descriptor": null
}''')

retrieve_success = json.loads('''{
  "interval": "month",
  "name": "Test!",
  "created": 1442136520,
  "amount": 2000,
  "currency": "aud",
  "id": "gold",
  "object": "plan",
  "livemode": false,
  "interval_count": 1,
  "trial_period_days": null,
  "metadata": {},
  "statement_descriptor": null
}''')
