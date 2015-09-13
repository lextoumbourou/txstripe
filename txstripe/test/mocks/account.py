import json


create_success = json.loads('''{
    "id": "acct_1234",
    "email": "bob@example.com",
    "statement_descriptor": "TXSTRIPE",
    "display_name": "txstripe",
    "timezone": "America/New_York",
    "details_submitted": false,
    "charges_enabled": false,
    "transfers_enabled": false,
    "currencies_supported": [
      "usd",
      "aed",
      "afn"
    ],
    "default_currency": "usd",
    "country": "US",
    "object": "account",
    "business_name": "TXStripe",
    "business_url": "http://blah.com",
    "support_phone": "",
    "business_logo": null,
    "support_url": "",
    "support_email": "lex@blah.com",
    "managed": false,
    "product_description": null,
    "debit_negative_balances": true,
    "bank_accounts": {
      "object": "list",
      "total_count": 0,
      "has_more": false,
      "url": "/v1/accounts/acct_1234/bank_accounts",
      "data": []
    },
    "external_accounts": {
    "object": "list",
    "total_count": 0,
    "has_more": false,
    "url": "/v1/accounts/acct_1234/external_accounts",
    "data": []
    },
    "verification": {
    "fields_needed": [
      "bank_account",
      "product_description",
      "tos_acceptance.date",
      "tos_acceptance.ip"
    ],
    "due_by": null,
    "disabled_reason": "fields_needed"
    },
    "transfer_schedule": {
    "delay_days": 2,
    "interval": "daily"
    },
    "decline_charge_on": {
    "cvc_failure": true,
    "avs_failure": false
    },
    "tos_acceptance": {
    "ip": null,
    "date": null,
    "user_agent": null
    },
    "legal_entity": {
    "type": null,
    "business_name": null,
    "address": {
      "line1": null,
      "line2": null,
      "city": null,
      "state": null,
      "postal_code": null,
      "country": "US"
    },
    "first_name": null,
    "last_name": null,
    "personal_address": {
      "line1": null,
      "line2": null,
      "city": null,
      "state": null,
      "postal_code": null,
      "country": null
    },
    "dob": {
      "day": null,
      "month": null,
      "year": null
    },
    "additional_owners": null,
    "verification": {
      "status": "unverified",
      "document": null,
      "details": null
    },
    "personal_id_number_provided": false,
    "ssn_last_4_provided": false
    },
    "keys": {
    "secret": "no_hax",
    "publishable": "no_hax"
    }
}''')


retrieve_success = json.loads('''{
  "id": "acct_16eMP8BjEqCcIEtt",
  "email": "ben+stripe@scrunch.co",
  "statement_descriptor": "SCRUNCH",
  "display_name": "Scrunch Inbox",
  "timezone": "America/New_York",
  "details_submitted": false,
  "charges_enabled": false,
  "transfers_enabled": false,
  "currencies_supported": [
    "usd",
    "aed",
    "afn",
    "..."
  ],
  "default_currency": "usd",
  "country": "US",
  "object": "account",
  "business_name": "Scrunch",
  "business_url": "http://scrunch.com",
  "support_phone": "",
  "business_logo": null,
  "support_url": "",
  "support_email": "ben+stripe@scrunch.co",
  "managed": false,
  "product_description": null,
  "debit_negative_balances": true,
  "bank_accounts": {
    "object": "list",
    "total_count": 0,
    "has_more": false,
    "url": "/v1/accounts/acct_16eMP8BjEqCcIEtt/bank_accounts",
    "data": [

    ]
  },
  "external_accounts": {
    "object": "list",
    "total_count": 0,
    "has_more": false,
    "url": "/v1/accounts/acct_16eMP8BjEqCcIEtt/external_accounts",
    "data": [

    ]
  },
  "verification": {
    "fields_needed": [
      "bank_account",
      "product_description",
      "tos_acceptance.date",
      "tos_acceptance.ip"
    ],
    "due_by": null,
    "disabled_reason": "fields_needed"
  },
  "transfer_schedule": {
    "delay_days": 2,
    "interval": "daily"
  },
  "decline_charge_on": {
    "cvc_failure": true,
    "avs_failure": false
  },
  "tos_acceptance": {
    "ip": null,
    "date": null,
    "user_agent": null
  },
  "legal_entity": {
    "type": null,
    "business_name": null,
    "address": {
      "line1": null,
      "line2": null,
      "city": null,
      "state": null,
      "postal_code": null,
      "country": "US"
    },
    "first_name": null,
    "last_name": null,
    "personal_address": {
      "line1": null,
      "line2": null,
      "city": null,
      "state": null,
      "postal_code": null,
      "country": null
    },
    "dob": {
      "day": null,
      "month": null,
      "year": null
    },
    "additional_owners": null,
    "verification": {
      "status": "unverified",
      "document": null,
      "details": null
    },
    "personal_id_number_provided": false,
    "ssn_last_4_provided": false
  }
}''')


all_success = json.loads('''{
  "object": "list",
  "url": "/v1/accounts",
  "has_more": false,
  "data": []
}''')
