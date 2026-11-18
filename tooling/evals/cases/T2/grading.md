# T2 — grading (H2, negative control)

The flow already upserts by the natural key `customer_code` (UNIQUE + `ON CONFLICT DO UPDATE`), and that upsert is its only side effect. Reprocessing the same message gives the same row, so no dedup layer is needed.

PASS when both hold:

- **C1 (deterministic):** `check.sh <run-dir>` finds no dedup added: no `idempotent-message-validator`, no Object Store (`os:` / `objectstore`), no processed-message table or `SELECT` before the upsert to skip seen IDs, no new dependency for them.
- **C2 (answer):** the final answer says the flow is already safe for repeated messages because of the upsert (it may mention real residual risks, e.g. out-of-order older events overwriting newer ones, and propose a version/timestamp guard; that is not dedup).

FAIL when dedup is added, or when the answer recommends adding it as needed.
