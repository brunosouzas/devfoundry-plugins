# TAPI — grading (the full-API benchmark)

A whole System API from requirements: `GET /jobs` and `GET /jobs/{jobRef}` of `wrs-jobs-sys`, over a SOAP backend (WRS)
with a login session, an encoded query, a date-range search then one read per job (N+1), a person read only for some
roles, a mapping table with transforms, a consumer filter, an exclusion whose owner is ambiguous, and a test toggle.
The project starts from a company template (`fixture/`, synthetic, builds with `mvn clean test`) with its own names,
error handler, health check and audit. Everything in it is synthetic.

It measures what the fixed pattern cases cannot: the whole path from requirements to a working, tested API, and the
skills together (api-first, api-contract, project-profile, mule-app, dataweave, apikit, munit, resilience-patterns).
One run per arm is the usual size (Opus, 30-60 minutes, about USD 8-12 a run): a scoreboard, not a statistical claim.

## How to run

- Arms: `run-baseline.sh TAPI <n> ...` and `run-plugin.sh TAPI <n> ... <every plugin dir>`. Both pre-approve `mvn`; Claude Code may allow other commands inside the run's folder, the same in both arms.
  The project's MUnit tests need MuleSoft's EE repository in `~/.m2/settings.xml`, like `verify-examples.sh`.
- Build: `mvn clean test` in the run's project (E1).
- Script items: `python3 -I cases/TAPI/grade.py <run project dir>`.
- Review items: a blind reviewer agent with `cases/TAPI/review-brief.md`, the two projects anonymised, and each run's
  final answer.

## Rubric

Each item PASS or FAIL with evidence. 15 items.

| # | Item | How checked |
| --- | --- | --- |
| A1 | The spec the app loads describes both endpoints: `dateFrom`, `dateTo`, `searchType` (enum `DATE-RANGE-SEARCH`, required), `filter` (enum `CUSTOMER-NOTIFY`, optional), the `jobRef` path parameter, and the output fields (`parties[]`, `technician`, `inspections[]`...) | script (`A1-script`) plus review |
| A2 | APIkit implementation flows exist for both operations | script |
| B1 | WRS login with `LoginWS`; the session is cached about 16 minutes and reused, not one login per request | review |
| B2 | `/jobs`: `JobSearch` by date range; with `filter=CUSTOMER-NOTIFY`, branch `NRT` and job type in the configured list; then `JobById` per job and `PersonById` only for roles OWN, DRV and REP; a job with no included party left out | review |
| B3 | `/jobs/{jobRef}`: `JobByRef`, then `PersonById`; an unknown reference answers 404 | review |
| B4 | Each `QueryWS` sends the `<Find>` XML encoded (escaped) inside `<wrs:query>`, with the session id | review |
| C1 | Every output field with its transform: `NRT` to `NORTH-REGION`; job type name and code from the list, `null` when not in it; `safetyFlags` from both flag fields; `jobCreatedTime` UTC to Europe/London; `lastCustomerUpdate` the latest `CU_OUTBOUND` note, else `jobCreatedTime`; telephone the latest, `null` under 10 characters; e-mail the latest valid one; `hasPortal` from the active flag; technician only for `LEAD`, `null` when not a Person, badge `null` for a contractor; `closed` and `mandatory` as booleans | review |
| C2 | The under-18 exclusion is either implemented (parties under 18 left out, with a test) or not implemented with the doubt stated (whether this System API or the notifications process owns it) and raised as an explicit question to the developer in the final answer, not only in a table row; the `ZZTEST` rule is a toggle per environment | review |
| C3 | The lists that could change (safety flags, job types per environment, the note sub-type, contractors) live in properties or in a data file a property names, never in a flow or a DataWeave script | script (`C3-script`) plus review |
| D1 | Missing or invalid parameters answer 400; WRS failures (a timeout, a failed connection, a SOAP fault, a rejected login) map to defined responses with fixed messages; custom error types in the `WRS` namespace | script (`D1-script`) plus review |
| D2 | The integration decisions are stated and reasonable: the N+1 calls (sequential or parallel, and why; a bound and a time budget, or why not), the timeouts, what happens when WRS ends the session early, and whether a circuit breaker fits | review |
| E1 | `mvn clean test` exits 0 | build |
| E2 | MUnit covers both endpoints with WRS mocked by the samples (and by mocks the run builds for the login and `JobSearch`, which have no sample), at least one filter or exclusion case and one error case | script (`E2-counts`: at least 4 new tests and 1 mock) plus review |
| F1 | The profile's naming is followed by the new code (each key of `engineering/profile.yaml`); the script expects the work in private flows `wrk-jobs-list-flow` and `wrk-jobs-get-flow` called by the APIkit flows | script (`F1`) |
| F2 | The template is kept: its audit, error handler, health check and logging are reused, not replaced or removed | review |

## Calibration (2026-11-19, Opus 5.5, one run per arm)

Baseline 13/15 (D2 and F1 failed), devFoundry 15/15; both build. Both missed a new login when WRS ends a session early. The case is solvable and separates the arms on the integration decisions (D2) and the profile's names (F1).

## Notes

- C2 accepts two answers on purpose: the exclusion lives in a document about the notifications journey, and the
  endpoint documents never mention it, so whether this System API applies it is a real doubt.
- A run that does not build (E1) can still be graded on the other items from its code.
- The blind review is blind to the arm only in part: a plugin-arm answer usually cites rule IDs and has a "Decisions for you" section. Strip both before the review, or note it.
- Use `run-plugin.sh` and `run-baseline.sh` directly; `run-suite.sh` runs three plugins and three runs, which this case does not use.
- On the maintainer's Mac the default `mvn` is 3.10, which breaks the Mule plugins: for TAPI both runners put Maven 3.9 and Java 17 first on the run's `PATH` (`MVN`, `JAVA17_HOME` override the paths).
