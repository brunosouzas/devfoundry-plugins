# TAPI — blind review brief

You receive two Mule projects, labelled S and T, built from the same template and the same requirements
(`docs/requirements/` inside each project), and each developer's final answer (`S-answer.md`, `T-answer.md`). You are
not told how they were produced. Judge each project on its own against the items below: PASS or FAIL, with evidence
(file:line). Read the requirements first. Do not run anything; read only.

| # | Item |
| --- | --- |
| A1 | The spec describes both endpoints: `dateFrom`, `dateTo`, `searchType` (enum `DATE-RANGE-SEARCH`, required), `filter` (enum `CUSTOMER-NOTIFY`, optional), the `jobRef` path parameter, and the fields of the mapping table. |
| B1 | WRS login with `LoginWS`; the session is cached about 16 minutes and reused across requests, not one login per request. |
| B2 | `/jobs`: `JobSearch` by date range; then, only with `filter=CUSTOMER-NOTIFY`, branch `NRT` and job type in the configured list; then for each job `JobById`, then `PersonById` only for roles OWN, DRV or REP; a job with no included party is left out. |
| B3 | `/jobs/{jobRef}`: `JobByRef`, then `PersonById`; an unknown reference answers 404. |
| B4 | Each `QueryWS` sends the `<Find>` XML encoded (escaped) inside `<wrs:query>`, with the session id. |
| C1 | Every output field with its transform: `NRT` to `NORTH-REGION`; job type name and code from the list, `null` when the id is not in it; `safetyFlags` true when `Job__Flags` or `Job__Flags2` holds a configured flag; `jobCreatedTime` from UTC to Europe/London; `lastCustomerUpdate` the most recent `CU_OUTBOUND` note, else `jobCreatedTime`; telephone the most recent, `null` under 10 characters; e-mail the most recent valid one; `hasPortal` from the active `CUSTOMER PORTAL USER` flag; technician only for `LEAD`, `null` when not a Person, badge `null` for a contractor; `closed` and inspection `mandatory` as booleans. List each sub-item that is missing or wrong. |
| C2 | The under-18 exclusion is either implemented (parties under 18 left out, with a test), or not implemented with the doubt stated (whether this API or its consumer owns the rule) and raised as an explicit question to the developer in the final answer, not only in a table row; the `ZZTEST` rule is driven by a toggle per environment. |
| C3 | The lists that could change (safety flags, job types, the note sub-type, contractors) live in properties or a data file a property names, not in code. |
| D1 | Invalid or missing parameters answer 400; WRS failures map to defined error responses with fixed messages (never WRS's own text); custom error types use the `WRS` namespace. |
| D2 | The answer or the code states the integration decisions: the N+1 calls (sequential or parallel, and why; a bound or a time budget), timeouts on WRS calls, what happens when WRS ends the session early, and whether a circuit breaker or similar protection fits. Judge whether each decision is reasonable, not whether a pattern was used. |
| E2 | MUnit covers both endpoints with WRS mocked by the sample XMLs (the login and `JobSearch` have no sample: mocks the developer built for them are expected), plus at least one filter or exclusion case and one error case. |
| F2 | The template is kept: its audit, error handler, health check and logging are reused, not replaced or removed. |

End with a short comparison: which project is closer to production-ready, and the three most important gaps of each.
