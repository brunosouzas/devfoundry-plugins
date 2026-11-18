# Idempotent Receiver

## The problem

Most transports promise "at least once", not "exactly once". A broker redelivers when an acknowledgement does not arrive in time, when the consumer crashes, or when it nacks. A client resends when its connection drops before the response. A replay from a dead-letter queue sends old messages again. Each of these reaches the receiver as a new delivery of the same business fact.

If handling that fact twice has a harmful effect (the customer is charged twice, two invoices exist, two emails go out), the receiver itself must recognise the repeat and skip the effect. That is the Idempotent Receiver: the receiver remembers which business facts it has already handled, and on a repeat it returns the earlier outcome instead of doing the work again.

## When to use

All of these hold:

- The same message or request can arrive more than once (assume it can, unless the source contract guarantees otherwise).
- Processing it causes a side effect that is **not** naturally repeatable: a payment, an invoice, an order, an email or notification, an `INSERT` without a natural unique key, an increment.
- Nothing downstream already rejects the repeat. "The other system probably deduplicates" does not count; only its documented contract does (for example an idempotency key that it promises to honour).

## When NOT to use

Do not add a dedup layer when any of these holds. Say which one in the answer.

- **The consumer is already idempotent.** The only side effect is an upsert or an absolute write keyed by the business's natural key (`INSERT ... ON CONFLICT (natural_key) DO UPDATE`, `MERGE`, a `PUT` that replaces the whole resource, a delete by id). Processing the same message twice leaves the same state, so a repeat is harmless.
- **The flow has no side effect.** Reads, lookups and pure transformations can run twice.
- **The downstream contract already deduplicates on a key you send.** If the target documents an idempotency key and the flow sends the business key in it, the target is the idempotent receiver. Add a local store only if the contract's window is shorter than your redelivery span.
- **The real risk is ordering, not repetition.** An older event arriving after a newer one and overwriting it is a different problem. It is solved by a version or timestamp guard on the write (`WHERE stored.version < incoming.version`), not by remembering message IDs. A dedup store keyed by entity would even drop legitimate later updates.

Adding the pattern where it is not needed is not free: it introduces a store that can be lost or fill up, a new failure mode (the key is recorded and the processing then fails, so the retry is wrongly dropped), and extra code to test.

## Choosing the key

Use the **business key** of the fact being processed, such as `orderId` for "invoice this order". Do not use the transport's message ID: a producer that republishes the same order, or a replay tool, gives it a new message ID, and the duplicate passes. When one business entity can legitimately trigger the effect several times, the key is the business key of the *effect* (for example `orderId + ":" + installmentNumber`).

## Realization per platform

Read the realization for the project's platform before writing code. It shows a complete project that is known to build and pass its tests, and the pitfalls its build caught:

- **Mule 4:** `${CLAUDE_SKILL_DIR}/references/mule4/idempotent-receiver.md`.

## Failure after the key is stored

This is the part that most implementations get wrong. Once the key is claimed, a failure must not leave the system in a state where the retry is silently dropped, or where it charges again blindly. Separate the outcomes:

- **The side effect certainly did not happen** (the target rejected the request with a `4xx` before processing it, or a step before the call failed): release the key, then let the source redeliver. Route a permanent rejection to a dead-letter queue. A transport error that cannot tell "never sent" from "sent, then lost" is not certain: treat it as unknown.
- **The outcome is unknown** (a response timeout, a connection lost after the request was sent, a `5xx` from a system that may have committed): do not release the key. The charge may have gone through. Keep the entry `IN_PROGRESS`, log it with the business key, and send it to reconciliation: a review queue, a lookup on the target by business key, or a retry that carries the target's idempotency key.
- **The app crashes after the claim:** the entry stays `IN_PROGRESS` and the source redelivers. Treat a stale `IN_PROGRESS` (older than the slowest expected call, judged by a timestamp in the value) as "unknown outcome" and reconcile it, rather than processing it again or ignoring it forever.

## Limits: the TTL and the window

The protection only holds while the key is in the store:

- A repeat that arrives **after the entry's TTL** is processed again. Choose a TTL longer than the longest span over which a repeat can arrive: the broker's message TTL and redelivery span, dead-letter replays, client resends. State the chosen TTL and this limit in the answer.
- A store that is lost (non-persistent, wiped, not shared across nodes) takes the protection with it.
- Entries that never expire grow forever, so a TTL is required, not optional.

## The test of the duplicate

The pattern is proven only by a test that sends the same business fact twice and checks that the side effect ran once. Add, as the flow requires:

- **Different keys:** two different keys both reach the side effect, so the dedup does not over-block.
- **A certain failure releases the key:** after the flow fails, the key is gone, so a redelivery can retry.
- **An unknown outcome keeps the key:** the key is still stored as `IN_PROGRESS`, and the message went to reconciliation.

The platform realization shows these tests in the platform's test framework. Run them when the environment allows it; if it does not, say that they were not run.
