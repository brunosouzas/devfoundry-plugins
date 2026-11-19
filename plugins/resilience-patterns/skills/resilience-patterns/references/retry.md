# Retry of transient failures

## The problem

A dependency fails now and then for a moment: a dropped connection, a `503` during a deploy, a timeout under a short burst of load. The same call a fraction of a second later works. Without a retry, each of those moments is an error the caller sees. With a careless retry, every error is repeated: answers that will never change (`404`, `400`, `401`) are asked three times, writes are executed twice, and a dependency that is already overloaded gets three times the traffic.

## When to use

All of these hold:

- The failure is **transient**: a timeout, a connection failure, or a status that means "try later" (`502`, `503`, `504`, and `429` when the dependency uses it that way).
- The call is **safe to repeat**: a read, or a write the dependency makes idempotent. A timeout on a write does not say whether the write happened.
- The retries **fit the time**: on a request path, the attempts and the delays stay inside the request's time budget (`bounded-fan-out.md`).

## When NOT to use

- **Answers that will not change:** `400`, `401`, `403`, `404`, `409`, `422`. Repeating them only adds load and delay. A `401` from an expired session is session renewal, not a retry (`session-renewal.md`).
- **A write that is not idempotent.** Make it idempotent first (`integration-patterns`, Idempotent Receiver, on the receiving side), or do not retry it.
- **The dependency is down for minutes** and the traffic is high: retries multiply the load on a dependency that cannot recover. That is a Circuit Breaker (`circuit-breaker.md`). Never retry while a circuit is open.
- **A broker already redelivers** the message: a retry in the flow on top of the broker's redelivery multiplies the attempts.

## How it works

- **A few attempts:** two or three in total on a request path. More belongs to a job or a queue.
- **A delay between attempts,** growing when the platform supports it (exponential backoff), with some randomness (jitter) when many callers retry together. A fixed short delay is acceptable for two or three attempts; say which one you use.
- **Retry only the transient errors.** Classify each error first; a permanent one ends the attempts at once and becomes a defined error.
- **After the last attempt,** return a defined error, never the dependency's own message: `504` when the last attempt timed out, `503` for any other transient failure (the same statuses as mule-app MERR-3 gives a call without retries).

State the worst case: `(attempts) x (connection timeout + response timeout) + (attempts - 1) x delay`. A response timeout alone does not bound the TCP connect: give the call a connection timeout too, or an unreachable host waits for the connector's default connection timeout (30 s for Mule's HTTP connector). The sum is approximate: a 1 s connection timeout failed after 2.2 s (measured), so leave a margin. On a request path, check the request's deadline before every attempt (`bounded-fan-out.md`), so the retries stop when the budget is spent instead of running past it.

## The test

- **A transient failure is retried, then fails cleanly:** the dependency fails every attempt; it is called exactly `maxRetries + 1` times and the caller gets the defined error.
- **A permanent failure is not retried:** a `404` is called once.
- **The budget holds across retries:** a deadline that passes between two attempts stops the retries.

## Realization per platform

- **Mule 4:** `${CLAUDE_SKILL_DIR}/references/mule4/fan-out-with-session.md`, with the verified example `${CLAUDE_SKILL_DIR}/assets/mule4/fan-out-with-session/`.
