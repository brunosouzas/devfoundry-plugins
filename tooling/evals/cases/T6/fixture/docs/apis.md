# APIs used by the exchange-rates job

## Rates provider (external)
`GET https://rates.example.test/v1/latest?base=BRL` returns `{ "base": "BRL", "date": "YYYY-MM-DD", "rates": { "USD": 0.18, "EUR": 0.17 } }`. Read-only.
Notes: usually answers in under a second. A few times a month a request times out; a new request a minute later almost always works. The provider allows 1,000 requests per day on our plan.

## Pricing API (internal)
`PUT https://pricing.internal.example.test/api/exchange-rates` with `{ "date": "YYYY-MM-DD", "rates": { ... } }` replaces the whole rate table. Sending the same body twice leaves the same table.

## The job
Runs once a day at 06:00 (America/Sao_Paulo). If it fails, prices keep the previous day's rates until someone runs it again by hand.
