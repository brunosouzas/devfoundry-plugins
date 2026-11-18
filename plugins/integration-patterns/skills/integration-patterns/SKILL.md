---
name: integration-patterns
description: Decides whether a Mule 4 flow needs an enterprise integration or resilience pattern and applies it only when the problem it solves is present. Use when writing, changing or reviewing a flow that consumes messages or events (Anypoint MQ, JMS, VM, Kafka, webhooks), that can receive the same request twice (broker redelivery, ack timeout, client resend, DLQ replay), that calls a system with side effects (charges, invoices, emails, orders, inserts), or that calls a dependency synchronously which can get slow or go down (the app hangs, threads pile up, other endpoints stop answering, recovery is slow); also when the developer asks how a flow should cope with repeats, retries, duplicates, timeouts, outages or "charged twice" problems, even without naming a pattern. Do NOT use it to add a dedup layer when the only side effect is already idempotent (an upsert or MERGE by natural key, a full PUT, a read), or a circuit breaker to a low-volume job or a consumer that can simply retry later: the skill then says why no pattern is needed.
---

# Integration patterns

A pattern is a fix for a specific problem. This skill checks whether the problem is in the flow before anything is added. Adding a pattern where the problem is absent is a defect too: it adds state, failure modes and code that someone must maintain.

## Steps

1. **Start from the integration decisions.** For the flow at hand, write down (briefly, in your answer):
   - **Repeats:** can the same message or request reach the flow more than once? Look at the source: a broker with at-least-once delivery, an acknowledgement timeout, a nack, a client that resends, a scheduler that overlaps. Then look at every side effect the flow causes and ask whether doing it twice is harmful.
   - **Failures:** for each step, what happens when it fails, and what has already happened by then (a charge made, a key recorded, a message acknowledged)?
   - **Dependencies:** for each synchronous call, how slow can the dependency get and for how long, who waits for it, and how much traffic keeps hitting it while it is down?
2. **Match against the catalog.** For each row whose signals are present, read the pattern's reference before writing code, and then its realization for the project's platform. `${CLAUDE_SKILL_DIR}` is this skill's directory, the base directory given when the skill loads. The reference explains why each piece of the pattern is there, and it does not depend on any platform. The realization points to an example project that is known to build and pass its tests, so take the syntax from it rather than from memory. Platforms with a realization today: Mule 4 (`references/mule4/`, `assets/mule4/`).

   | Pattern | Signals that the problem is present | Reference, then realization |
   | --- | --- | --- |
   | Idempotent Receiver | The same message can arrive again **and** processing it twice has a harmful, non-repeatable side effect (a charge, an invoice, an email, an insert without a natural key, a counter). | `${CLAUDE_SKILL_DIR}/references/idempotent-receiver.md`, then `${CLAUDE_SKILL_DIR}/references/mule4/idempotent-receiver.md` |
   | Circuit Breaker | A **synchronous** call on a request path to a dependency that can be slow or down for minutes, **and** enough traffic that waiting on it ties up the app's threads or keeps hammering it while it recovers. | `${CLAUDE_SKILL_DIR}/references/circuit-breaker.md`, then `${CLAUDE_SKILL_DIR}/references/mule4/circuit-breaker.md` |

3. **Check "not when" first.** Every reference has a "When NOT to use" section. If any item applies, do not add the pattern. Say in your answer which item applies and why the flow is already safe, using evidence from the code (the SQL, the connector, the API doc).
4. **Apply only what the reference requires.** When the problem is present and no "not when" applies, implement the pattern as the reference's Mule 4 section describes, including its failure handling, its limits and its test. Do not add extra patterns "just in case".
5. **Report the decision.** End the answer with one line per pattern considered: `applied` or `not applied`, with the reason in one sentence. State the limits of what was applied (for example the window the protection covers).

## Rules

- Never infer the problem from the developer's wording alone. A request that says "make it handle repeated messages" does not mean a dedup layer is missing; read the flow first.
- Never assume that a downstream system deduplicates unless its contract says so.
- A pattern that changes behaviour needs a test that shows the behaviour (for the Idempotent Receiver: the duplicate test; for the Circuit Breaker: an open circuit does not call the dependency).
- Patterns are independent. One flow can need one, several or none of them: check each row on its own.
