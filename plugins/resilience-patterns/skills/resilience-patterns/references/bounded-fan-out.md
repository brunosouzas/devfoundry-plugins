# Bounded fan-out with a time budget

## The problem

One request becomes many calls: a search returns N ids, then one call per id reads the details (the N+1 pattern). In testing N is three. In production a wide search returns hundreds: the request makes hundreds of calls, one after the other or all at once, and either runs far past the time the caller waits (the caller gives up, the work goes on and is thrown away) or takes every connection to the dependency and slows every other request.

Each call has its own timeout, but nothing bounds the request as a whole. Ten calls of a 20-second timeout is over three minutes.

## When to use

All of these hold:

- A request makes **a number of calls that depends on the data** (the size of a search, the items of an order), not a fixed number.
- The requirements **do not bound that number** to something small, or the bound is only implied (a date range with no stated volume).
- Someone **waits** for the request: a client, a gateway, a caller with its own timeout.

On an **existing API** that consumers already use, a new bound changes what they see: a request that returned 80 items now gets `422`. That is a breaking change to the contract (api-contracts CON-5, class `ask`): propose the bound, its value and the error to the developer. Apply it directly to a new endpoint, or when the requirements ask for it.

## When NOT to use

- **The number is fixed and small**, or the requirements bound it (at most five items, a page size the API enforces). Say which bound applies.
- **Nobody waits:** a batch or an asynchronous job can take as long as it needs; bound its concurrency to protect the dependency, but a request deadline does not apply.
- **The dependency has a bulk operation** (read many ids in one call): use it instead of the fan-out.

## The three parts

1. **A bound on N, checked before the first call.** More items than the request can read inside its budget is refused at once, with a defined error the caller can act on (`422`, "narrow the search"), or paged when the API's contract has paging. Never start a request that cannot finish.
2. **Bounded concurrency.** Run the calls in parallel only up to a set number at once, so one request cannot take every connection to the dependency. Sequential is the bound of one: fine when N is small, and say why.
3. **A time budget for the whole request,** below what the caller waits (a client timeout, a gateway timeout), set once at the start as a deadline. Before **every** call, retry attempt and login, check the deadline: once it has passed, start nothing more and answer `504` (a system behind the API was too slow), never `408`. Each call keeps its own timeout, below the budget, so the request ends at most one call's worst case (its connection timeout plus its response timeout) after its deadline.

Choose the values together and state them. Size `maxItems` on the dependency's usual latency (with `maxItems` items, `maxConcurrency` at once and a usual latency `l`, about `ceil(maxItems / maxConcurrency) x l`), so a normal request finishes well inside the budget. When the dependency is slow, the deadline is the guard, not `maxItems`. The budget plus one call's worst case (connection timeout plus response timeout) must fit what the caller waits.

## One failure among many

A failed call inside a parallel fan-out usually surfaces as the framework's composite error, carrying the dependency's own message. Catch each call's failure where it happens, then map the set to one defined error, the most telling first (the budget, then a rejected session, then an unavailable dependency). Returning the items that succeeded, flagged as partial, is the other choice; the API's contract decides which.

## Limits

- The deadline is checked before each call, not during one: a call that started just before the deadline can run for its full timeout after it: its connection timeout plus its response timeout, since the response timeout does not bound the connect.
- The bound on N refuses a request the caller may need. Say what the caller does instead (a narrower search, paging).

## The test

- **The bound:** a search with `maxItems + 1` results is refused, and no detail call is made.
- **The budget:** with the deadline already in the past, no detail call is made and the request ends with the timeout error; and a deadline that passes during the retries of one call stops them. Do not wait on purpose in a test: put the deadline in the past, or just ahead of a delay the flow already has.
- **The happy path:** every item is read and returned.

## Realization per platform

- **Mule 4:** `${CLAUDE_SKILL_DIR}/references/mule4/fan-out-with-session.md`, with the verified example `${CLAUDE_SKILL_DIR}/assets/mule4/fan-out-with-session/`.
