# T1b — grading (H2, implicit Idempotent Receiver, realistic request)

The request never mentions resends, duplicates or double charges. The risk is implicit: Anypoint MQ delivers at least once (redelivery after an acknowledgement timeout, a crash or a nack), and `POST /invoices` creates an invoice and charges the customer on every call.

Same rubric as T1 (`tooling/evals/cases/T1/grading.md`), applied to the new consumer flow. One point per item; PASS = 3/3.

| # | Item | PASS when |
| --- | --- | --- |
| R1 | Business-key dedup | The consumer uses an Idempotent Receiver or an equivalent (idempotent-message-validator, Object Store check-and-store, unique key in a DB) keyed on `orderId`, so a redelivered message does not call `POST /invoices` again. Only forwarding `orderId` and hoping that billing deduplicates does not count: the doc does not say it does. |
| R2 | Failure after the key is stored | Handles the case where the key is recorded but the billing call fails or the app crashes before the ack. For example, it removes the key on error so the redelivery can retry, or it keeps a state per key. |
| R3 | TTL / window limit stated (flexible) | States that the dedup only holds within the store TTL or window, or within the store's durability, **or** configures a finite TTL on the dedup store in the code (for example `entryTtl` on the Object Store). A store with no TTL and no statement of the limit fails. |

R3 is read flexibly (decided 2026-11-18): configuring a finite TTL counts as stating the window. It applies to both arms alike.

Record also, ungraded: whether the run mentions duplicates or redelivery at all, unprompted.
