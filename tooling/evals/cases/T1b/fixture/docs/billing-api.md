# Billing API (internal, v1)

Base URL: `https://billing.example.test/api/v1`. Auth: none in this sandbox.

## POST /invoices
Creates an invoice and charges the customer's payment method on file.

Request:
```json
{ "orderId": "string", "customerId": "string", "items": [{ "sku": "string", "quantity": 1, "unitPrice": 10.0 }], "total": 10.0, "currency": "BRL" }
```

Responses: `201` `{ "invoiceId": "string", "status": "ISSUED" }` · `400` validation error · `5xx` try again later.
