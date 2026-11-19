# Session renewal

## The problem

The flow logs in to a dependency and caches the session (a token, a session id) for less than the dependency says it lasts, so most requests skip the login. But the dependency can end a session early: a restart, a deploy, a failover, an administrator, a limit on sessions per user. From then on every request sends a session the dependency rejects, and every request fails until the cache entry expires on its own, minutes later. Nothing is wrong with the dependency or the credentials: the flow just holds a dead session.

Session renewal drops the rejected session, logs in again and repeats the call **once**.

## When to use

All of these hold:

- The flow **caches** a session or token, so a rejected one would otherwise be reused.
- The dependency has a **distinct signal for "this session is no longer valid"**: a `401`, or a fault code its documentation names (a SOAP fault, an error field in a `200`). With a fault or an error field, check that code and treat only it as expiry; mapping every fault to "session rejected" is the ambiguous case below. A signal that also means "these credentials are wrong" still works, because the second attempt then fails too (see the limit below).
- The call is **safe to repeat**: a read, or a write the dependency makes idempotent (an idempotency key, an upsert by a natural key). A rejected session usually means the call was not executed, but a call that can have side effects needs that confirmed before it is repeated.

## When NOT to use

- **No cache.** A flow that logs in on every request never holds a stale session; renewal adds nothing.
- **The dependency refreshes the session itself** (an OAuth client with refresh tokens, a connector that re-authenticates on its own): use that mechanism, do not wrap it a second time.
- **A write that is not safe to repeat**, unless the dependency confirms the rejected call did nothing. Otherwise return a defined error and let the caller decide.
- **The signal is ambiguous.** If the dependency answers the same way for an expired session and for a forbidden operation (`403` for both), renewal turns every authorisation error into a second login. Renew only on the signal that means expiry.

## How it works

1. Read the session from the cache, or log in and cache it.
2. Make the call.
3. On the expiry signal: remove the cached session, log in again, cache the new one, and make the call once more.
4. On a second rejection: stop and return a defined error (`502`: the dependency refused the API's own session). **Never loop**: a login that keeps being rejected is a credentials or a dependency problem, and a loop multiplies logins and can lock the account.

Concurrent requests can all see the same rejection. Only one whose rejected session is still the cached one should drop it and log in; one that finds a newer session in the cache reuses it. Two can still log in at the same moment (both read the old session before either stores a new one): a few extra logins, harmless for most dependencies. If the dependency allows one session per user, a second login ends the first, so make those calls one at a time and state it.

## The test

- **A rejected session is renewed once:** a cached session the dependency rejects; the call succeeds with exactly one new login and two attempts of the call.
- **A second rejection fails without a loop:** the dependency rejects every session; two logins, two attempts, then the defined error.
- **The session is cached:** two requests, one login.

The renewal test needs the dependency to answer differently to the old and the new session. A mock that always gives the same answer cannot show it; use a stub of the dependency that reads the session it receives. The platform realization shows how.

## Realization per platform

- **Mule 4:** `${CLAUDE_SKILL_DIR}/references/mule4/fan-out-with-session.md`, with the verified example `${CLAUDE_SKILL_DIR}/assets/mule4/fan-out-with-session/`.
