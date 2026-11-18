# T6 — grading (H2, negative control for the Circuit Breaker)

A daily job makes one call to a provider that occasionally times out, and a retry a minute later almost always works. There is no load to shed and no thread pool to protect, and stopping calls for a while would only make the job fail. The fix is a retry with a delay (for example `until-successful` with a few attempts and a wait), and optionally an alert when every attempt fails. The pricing `PUT` replaces the whole table, so repeating it is safe: no dedup either.

PASS when all hold:

- **D1 (deterministic):** `check.sh <run project dir>` finds no circuit-breaker state (no Object Store, no failure counter or open/half-open state, no `circuitBreaker` element) and no dedup construct.
- **D2 (answer):** the answer explains a fix for the transient timeout (retry with a delay, more attempts, a timeout setting, or an alert/manual-rerun path). If it mentions a circuit breaker or dedup, it says why neither is needed here.

FAIL when circuit-breaker state or dedup is added, or when the answer recommends adding them as needed.

Rule fixed before the counted round: `check.sh` is broad on purpose. When it flags a hit that is clearly neither circuit-breaker state nor dedup (for example an Object Store that keeps the last successful run date), D1 is decided by hand, and the hit and the reason are recorded in the evidence.
