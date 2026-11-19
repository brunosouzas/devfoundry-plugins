---
name: integration-patterns
description: "Decides whether an integration flow needs an Enterprise Integration Pattern (the Hohpe and Woolf catalog) and applies it only when the problem it solves is present, on any platform. Use when writing, changing or reviewing a flow or service that consumes messages or events (a queue, a topic, JMS, Kafka, webhooks), that can receive the same message or request twice (broker redelivery, ack timeout, client resend, DLQ replay), or that triggers side effects in other systems (charges, invoices, emails, orders, inserts); also when the developer asks how a flow should cope with repeats, duplicates or \"charged twice\" problems, even without naming a pattern. Do NOT use it to add a dedup layer when the only side effect is already idempotent (an upsert or MERGE by natural key, a full PUT, a read): the skill then says why no pattern is needed. For a slow or failing dependency (timeouts, outages, an app that hangs), use resilience-patterns instead."
---

# Integration patterns

The catalog is the one of *Enterprise Integration Patterns* (Hohpe and Woolf), with the book's names. A pattern is a fix for a specific problem. This skill checks whether the problem is in the flow before anything is added. Adding a pattern where the problem is absent is a defect too: it adds state, failure modes and code that someone must maintain.

## Steps

1. **Start from the integration decisions.** For the flow at hand, write down (briefly, in your answer):
   - **Repeats:** can the same message or request reach the flow more than once? Look at the source: a broker with at-least-once delivery, an acknowledgement timeout, a nack, a client that resends, a scheduler that overlaps. Then look at every side effect the flow causes and ask whether doing it twice is harmful.
   - **Failures:** for each step, what happens when it fails, and what has already happened by then (a charge made, a key recorded, a message acknowledged)?
2. **Match against the catalog.** For each row whose signals are present, read the pattern's reference before writing code, and then its realization for the project's platform. `${CLAUDE_SKILL_DIR}` is this skill's directory, the base directory given when the skill loads. The reference explains why each piece of the pattern is there, and it does not depend on any platform. The realization points to an example project that is known to build and pass its tests, so take the syntax from it rather than from memory. Platforms with a realization today: Mule 4 (`references/mule4/`, `assets/mule4/`).

   | Pattern | Signals that the problem is present | Reference, then realization |
   | --- | --- | --- |
   | Idempotent Receiver | The same message can arrive again **and** processing it twice has a harmful, non-repeatable side effect (a charge, an invoice, an email, an insert without a natural key, a counter). | `${CLAUDE_SKILL_DIR}/references/idempotent-receiver.md`, then `${CLAUDE_SKILL_DIR}/references/mule4/idempotent-receiver.md` |

3. **Check "not when" first.** Every reference has a "When NOT to use" section. If any item applies, do not add the pattern. Say in your answer which item applies and why the flow is already safe, using evidence from the code (the SQL, the connector, the API doc).
4. **Apply only what the reference requires.** When the problem is present and no "not when" applies, implement the pattern as the reference and its platform realization describe, including its failure handling, its limits and its test. Do not add extra patterns "just in case".
5. **Report the decision.** End the answer with one line per pattern considered: `applied` or `not applied`, with the reason in one sentence. State the limits of what was applied (for example the window the protection covers).

## Rules

- Never infer the problem from the developer's wording alone. A request that says "make it handle repeated messages" does not mean a dedup layer is missing; read the flow first.
- Never assume that a downstream system deduplicates unless its contract says so.
- A pattern that changes behaviour needs a test that shows the behaviour (for the Idempotent Receiver: the duplicate test).
- Patterns are independent. One flow can need one, several or none of them: check each row on its own.
- Resilience is a separate concern. A slow or unavailable dependency (timeouts, a circuit breaker, retries with backoff) is the `resilience-patterns` skill: invoke it when the integration decisions show one.
