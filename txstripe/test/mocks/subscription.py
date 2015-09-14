import json

retrieve_success = json.loads('''{
  "id": "sub_1234",
  "plan": {
    "interval": "month",
    "name": "My Plan 1",
    "created": 1441195927,
    "amount": 49900,
    "currency": "aud",
    "id": "my_plan_1",
    "object": "plan",
    "livemode": false,
    "interval_count": 1,
    "trial_period_days": null,
    "metadata": {
    },
    "statement_descriptor": "SOME PLAN 1"
  },
  "object": "subscription",
  "start": 1442236277,
  "status": "active",
  "customer": "cus_1234",
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
  "metadata": {
  }
}''')
