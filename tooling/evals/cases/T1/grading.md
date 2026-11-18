# T1 — grading (H2, implicit Idempotent Receiver)

Grade each run on the final project files plus the final answer. One point per item; PASS = 3/3.

| # | Item | PASS when | FAIL examples |
| --- | --- | --- | --- |
| R1 | Business-key dedup | Uses Idempotent Receiver or an equivalent (idempotent-message-validator, Object Store check-and-store, unique key in a DB) keyed on `orderId` (optionally with customerId), and a duplicate does not reach the payment call. | Key on message hash / correlation ID / `#[payload]`; dedup only on the gateway side without changes; only advice, no change. |
| R2 | Failure after the key is stored | Explicitly handles the case where the key is recorded but the charge fails or the flow crashes before completion: e.g. removes the key on error, stores state (IN_PROGRESS/DONE) and returns the stored result, or forwards `orderId` as the gateway's idempotency key. | A failed first attempt blocks every retry forever (key stored, charge never made) and this is not addressed. |
| R3 | TTL / window limit stated | States that dedup only holds within the Object Store entry TTL / window (or store durability, e.g. persistent vs in-memory, cluster), i.e. it is not unlimited exactly-once. | Claims "never charged twice again" with no window/durability caveat. |

Not graded: code style, whether it compiles (T4, Stage 3), response status code chosen for duplicates (as long as it is not a second charge).
