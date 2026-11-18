# Score API (internal, v2)

Base URL: `https://score.example.test/api/v2`. Auth: none in this sandbox. Owned by the risk team.

## GET /scores/{customerId}
Returns the customer's current credit score. Read-only; no side effects.

Response `200`: `{ "customerId": "string", "score": 0, "band": "A|B|C|D", "calculatedAt": "date-time" }` · `404` unknown customer · `5xx` try again later.

## Operational notes (from the risk team)
- Normal latency: 150–300 ms.
- Under load (month end, campaigns) the service degrades: responses take 30–60 s or never arrive, then it starts answering `503`.
- It recovers in a few minutes once the load drops. While callers keep sending requests at full rate, recovery takes much longer.
- For loan applications, the UI can show an application with the score as pending; the score is not required to display it.
