---
name: resilience-patterns
description: Decides whether a flow or service needs a resilience pattern against a slow or failing dependency (Circuit Breaker, and timeouts, retries with backoff, bulkheads as its companions) and applies it only when the problem is present, on any platform. Use when writing, changing or reviewing code that calls another system synchronously, or when the developer reports that the app hangs, threads or requests pile up, other endpoints stop answering, a dependency's outage spreads, or recovery is slow after the dependency comes back, even without naming a pattern. Do NOT use it to add a circuit breaker to a low-volume job, a batch, or a message consumer that can simply retry later; the skill then says why a retry with a delay is enough. Repeated messages and duplicate side effects are integration-patterns, not this skill.
---

# Resilience patterns

These patterns are not from the *Enterprise Integration Patterns* catalog. They are stability patterns (Nygard, *Release It!*): they stop one failing dependency from taking the caller down with it. A pattern is a fix for a specific problem. This skill checks whether the problem is in the code before anything is added. A breaker where nothing is at risk only adds state and a new way to fail.

## Steps

1. **Start from the dependency decisions.** For each call to another system, write down (briefly, in your answer):
   - **Who waits:** is the call on a request path that a client or a thread waits for, or in a job or consumer that can retry later?
   - **How it fails:** how slow can the dependency get and for how long (one slow request, or minutes of degradation), and what does its documentation say about load, timeouts and recovery?
   - **What the traffic does:** how many requests keep hitting it while it is down, and what that does to the app's threads, to other endpoints, and to the dependency's recovery.
   - **The answer without it:** is there a sensible fallback (partial data, a "pending" field, a cached value) or a fast, explicit error?
2. **Match against the catalog.** For each row whose signals are present, read the pattern's reference before writing code, then its realization for the project's platform. `${CLAUDE_SKILL_DIR}` is this skill's directory. The reference explains why each piece is there and does not depend on any platform. The realization gives the platform's native options first, then an example project that is known to build and pass its tests: take the syntax from it, not from memory. Platforms with a realization today: Mule 4 (`references/mule4/`, `assets/mule4/`).

   | Pattern | Signals that the problem is present | Reference, then realization |
   | --- | --- | --- |
   | Circuit Breaker | A **synchronous** call on a request path to a dependency that can be slow or down for minutes, **and** enough traffic that waiting on it ties up the app's threads or keeps hammering it while it recovers. | `${CLAUDE_SKILL_DIR}/references/circuit-breaker.md`, then `${CLAUDE_SKILL_DIR}/references/mule4/circuit-breaker.md` |

3. **Check "not when" first.** Every reference has a "When NOT to use" section. If any item applies, do not add the pattern. Say which item applies, and what fits instead (often a retry with a delay, or a shorter timeout).
4. **Apply only what the reference requires.** Implement the pattern as the reference and its platform realization describe, with an explicit timeout, the failures that count, the fallback, the limits and the test. Do not add retries in front of a breaker that is open, and do not add patterns "just in case".
5. **Report the decision.** End the answer with one line per pattern considered: `applied` or `not applied`, with the reason in one sentence. State the values chosen (threshold, cool-down, timeout) and the limits of the protection.

## Rules

- Never infer the problem from the developer's wording alone: read the code and the dependency's documentation first.
- A timeout is always part of the fix for a slow dependency, but a timeout alone does not stop the traffic.
- A pattern that changes behaviour needs a test that shows the behaviour (for the Circuit Breaker: an open circuit does not call the dependency).
- Duplicate messages and side effects that must happen once are the `integration-patterns` skill. A flow can need both skills.
