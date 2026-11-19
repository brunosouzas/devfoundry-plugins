# Backlog: the EIP rules of brunosouzas/agent-skills

Copied whole from `plugins/mulesoft/skills/mulesoft/references/eip.md` of brunosouzas/agent-skills (same author), before its `mulesoft` plugin is retired. Not a devFoundry skill: the source for the patterns `integration-patterns` does not have yet (Dead Letter Channel, Correlation Identifier, Publish-Subscribe Channel, and the general rules EIP-1 to EIP-8). Idempotent Receiver and Circuit Breaker are already patterns here (`integration-patterns`, `resilience-patterns`). A pattern ported from here follows AGENTS.md: a neutral reference, a realization, a verified example and its two fixed cases.

---

# EIP in Mule 4 applications: patterns

Read this file for every change that makes an integration decision: routing, splitting, aggregating, retrying, deduplicating, delivering later, correlating a reply, or stopping calls to a failing service. Apply the pattern whose problem the change has, without waiting for the developer to name it; the rules say when not to use it. Each pattern has its general problem, which applies in any language, then its Mule 4 implementation and its test.

How to change this file (see CONTRIBUTING.md of this repository):
- **Add a rule:** give it the next number in its pattern's group. A new rule is a MINOR version of the mulesoft skill.
- **Change a rule:** edit it in place and keep its ID. A rule that now says the opposite is a MAJOR version; clearer wording is a PATCH.
- **Retire a rule:** keep its ID and heading, replace the text with `(retired in <version>: <reason>)`, and never reuse the number.

## Applying any pattern (EIP)

- **EIP-1** Name the question before the pattern: what must the flow decide (where a message goes, how often it is processed, what happens after a failure)? Then pick the pattern that answers that question.
  Why: a pattern chosen by its name often solves a different problem from the one the flow has.
  Check: the change says which question each pattern answers.

- **EIP-2** Use the smallest pattern that answers the question. Every pattern adds state, a failure mode or a place to look; a pattern without a question is a cost.
  Why: the "not when" of each rule is where the simpler answer lives.
  Check: each pattern in a change has a reason, and its "not when" was checked against the case.

- **EIP-3** Design for the guarantee the system really gives. A queue delivers at least once, a Scheduler can run on several replicas, and an Object Store is local to a worker unless it is shared and has no transactions. A receiver must tolerate a repeated message; an effect that must happen once needs a key the target itself checks (IDEM-2).
  Why: a flow that assumes exactly once fails silently on the first retry or the first concurrent copy.
  Check: each consumer states how it handles a repeated message, and each effect that must happen once names the key that makes it so.

- **EIP-4** Every pattern that stores, retries or delivers later says what happens to a message that cannot be processed: a retry with a limit, a dead letter queue, an error reply, a compensation. Logging and continuing is not one of them.
  Why: the failure path is where the patterns differ, and no happy-path test exercises it.
  Check: the failure branch exists and a test drives it.

- **EIP-5** Test the behaviour the pattern exists for, not only the happy path: the duplicate, the expired message, the failed write, the concurrent copy. Use the `munit` skill (MUNIT-1 and MUNIT-2) when it is installed, and follow the same rules when it is not. Mock the failure and assert the state after the flow, not only the status code.
  Why: the patterns' bugs are in the cases the happy path skips.
  Check: each pattern in a change has one test of its failure path.

- **EIP-6** A Mule component is not a pattern. One component can implement several patterns, so name the pattern by the reason the component is used.
  Why: the reason decides the rule that applies.
  Check: the change names the pattern for each component it adds.

- **EIP-7** Check version-sensitive behaviour against the runtime you deploy. Defaults change between runtime versions, and CloudHub 2.0 differs from a Mule cluster for schedules and object stores.
  Why: a default that changed silently changes a pattern's behaviour without a code change.
  Check: the runtime version and the replica behaviour are named when the flow runs on several replicas.

- **EIP-8** When the developer names a pattern, apply it even when the problem in the flow does not match it. This is the one override of the selection in the flow's implementation step and of the pattern's "not when": it applies to the named pattern only. It does not override correctness, the API contract (MERR-2) or locked rules. Then say in the change what the pattern does, what problem it does not solve in this flow, and what it costs (state, latency, failure modes). When the pattern fits, do not ask again.
  Why: the developer may know a constraint the flow does not show; the cost belongs in the change, not in a silent choice.
  Check: a named pattern appears in the change with its cost, and its "not when" is stated when the case matches it.

## Dead Letter Channel (DLC)

**The pattern.** A message that a consumer cannot process after repeated attempts must leave the channel, with its reason kept, so that the other messages keep flowing and someone can handle it later. The messaging system moves it to a dead letter channel; the consumer only confirms or refuses each message.

- **DLC-1** Use a Dead Letter Channel for a message that a queue consumer cannot process after repeated attempts, when someone owns the dead letter queue and can reprocess its messages. Not for a flow that starts with an HTTP listener (no queue: the caller gets the error). Not for a message that will never be valid (use an invalid message channel: its content must be inspected, not retried). Not for a brief failure that a retry inside the attempt window handles.
  Why: after the last attempt the broker moves the message aside; retrying forever blocks the queue and dropping it loses the order.
  Check: the source queue has a dead letter queue, and the flow's owner is named.

- **DLC-2** In Mule 4 with Anypoint MQ, assign the dead letter queue in the source queue's configuration ("Assign a Dead Letter Queue", "Delivery attempts before reroute", 10 by default), not in the flow. Create the dead letter queue first, with the same type, region, environment and account as the source. The consumer's Subscriber uses `acknowledgementMode="AUTO"` (the default): the message is acknowledged when the flow ends without error and refused when an error propagates; the broker then counts the attempt. Do not confuse the attempts of the queue with the connector's Max Redelivery Count, which throws `MULE:REDELIVERY_EXHAUSTED`. Set `acknowledgementTimeout` above the flow's processing time.
  Why: the flow only answers ACK or NACK; the broker decides when a message is dead.
  Check: a MUnit test raises an error in the consumer and asserts the error propagates (so the broker counts the attempt); the broker configuration is checked by hand, since MUnit has no broker.

- **DLC-3** A dead letter queue has its own TTL and needs an owner and a way back into a queue. A FIFO queue with a dead letter queue does not keep strict order. Each message in it is a failure that someone must explain.
  Why: a dead letter queue nobody reads is a silent loss with a longer delay.
  Check: the change names who reprocesses the dead letter queue and how.

## Idempotent Receiver

**The pattern.** The same message can arrive more than once, from a client retry, a gateway or a reprocessing. A receiver that remembers what it already processed filters the repeats. Filtering is not the same as an effect that happens once across concurrent copies: that needs a key the target checks.

- **IDEM-1** Use an Idempotent Receiver when the same message can arrive more than once and its effect must happen once, such as a charge. Not when the target operation is already idempotent by business key (an upsert by `orderId`) and has no other effect such as an email or an event: the receiver would add a store, a TTL and a failure trap for nothing.
  Why: the receiver costs storage and adds a failure mode; it pays only when the target would double the effect.
  Check: the target creates something on each call, or the change says why the receiver is needed.

- **IDEM-2** In Mule 4, use the Idempotent Message Validator with `idExpression` set to a business key (the order ID). Do not use the default `#[correlationId]`: a client that resends without the header gets a new one, and a For Each batch shares one ID across different orders. Do not use a hash of the payload: a timestamp field changes it. Without a configured store, IDs stay in memory for 5 minutes; set the store and its TTL to cover the window in which a duplicate can arrive. Object Store v2 TTL is either static (fixed from the write, at most 30 days) or rolling (30 days minimum, extended only by qualifying accesses in the final seven days of its window; `Contains` does not extend it). For a shorter fixed deduplication window, configure a static TTL. Object Store v2 has no distributed lock on CloudHub, so two copies that arrive together at two replicas can both pass the validator. When the effect must happen once across replicas, the target must check a key: a provider's idempotency key sent with the charge, or a unique constraint in a database. A repeated request is then answered from the stored result. Where a duplicate is an error, the API contract (MERR-2) decides its status (for example 409 when the spec defines it); on a queue, the duplicate is acknowledged after the effect is confirmed, as a decision in the flow, not by an error handler that acknowledges silently.
  Why: the default key, the in-memory store and the absence of a distributed lock are the three ways the receiver silently does the wrong thing.
  Check: a MUnit test sends the same request twice and asserts one effect; a test sends two concurrent copies to the target fake and asserts one effect when the target checks the key.

- **IDEM-3** The validator stores the ID before the rest of the flow runs and does not remove it when the flow fails afterwards. A failed charge therefore makes the retry a duplicate, and the order is never charged. Decide the failure behaviour on purpose: remove the ID in the error handler only when the effect is known not to have happened (removing it after a charge that succeeded allows a second charge); the other option is to store the ID only after success, which leaves a race between the check and the store unless the target checks the key (IDEM-2). Cover the chosen behaviour with a test that makes the effect fail and then retries. When the target may have committed and the response timed out, the outcome is uncertain: the next request must not stop at the validator with a dead end. Reconcile instead: ask the provider for the result of the idempotency key, or repeat the call with the same key, then store the confirmed result and answer or acknowledge with it. The test asserts eventual recovery with one effect, not only that the effect happened once.
  Why: this trap is quiet: the retry gets an answer that looks correct.
  Check: a MUnit test fails the effect after the validator and asserts the retry's outcome and the number of effects; a timeout test after a committed effect asserts the reconciled result and one effect.

## Correlation Identifier

**The pattern.** A reply arrives by another route (a payment provider's callback, a reply queue) and several requests are pending. A request identifier is sent with the request, comes back in the reply, and matches the reply to its request.

- **CORR-1** Use a Correlation Identifier when a reply arrives by another route and several requests are outstanding. Not when the reply comes on the same synchronous connection (a stored identifier only adds moving parts).
  Why: the pattern answers "which request is this reply for".
  Check: the flow generates the request identifier, sends it with the request, and matches the reply on it.

- **CORR-2** Choose the carrier by the guarantee it gives. Mule's `correlationId` identifies an execution: it is inherited from an incoming message or generated, and it is the right tool for tracing a flow across applications, not for a business reply, because a client that resends without the header gets a new one. For request/reply on JMS, the connector matches the reply by `CORRELATION_ID`; use it when the message broker is the reply channel. For a provider's callback, the request identifier is a business value you generate (`"PRQ-" ++ uuid()`), sent in the body or a header, and stored with the pending request. Store the pending request durably before the outbound call, because the callback can arrive before the 202 answer, and set an explicit TTL: a pending entry that expires leaves the order pending, so decide what happens then. An in-memory store is lost on a restart and is not shared between workers.
  Why: each identifier answers a different question, and a reused identifier answers the wrong one.
  Check: each identifier in the change names what it identifies and where its uniqueness comes from.

- **CORR-3** Keep the pending state until the outcome is committed. Do not remove the pending request before writing the outcome: a failed write then leaves the reply with no record, and the retry gets 404 while the order stays pending. Read the pending request, compute the outcome, write the outcome, and only then remove the pending entry. A repeated callback finds the outcome already written and returns it without changing it. Object Store has no transactions, so two copies that arrive together can both write; when the outcome must be written exactly once, make the write conditional on the order's current state (a database row with a version or a unique constraint), not on the Object Store alone.
  Why: removing first turns a failed write into a lost reply.
  Check: MUnit tests cover an out-of-order callback, a repeated callback (the first outcome is returned, unchanged), a failed outcome write followed by a retry that completes the order, and two simultaneous callbacks, which must produce one outcome.

## Publish-Subscribe Channel

**The pattern.** An event must reach several systems, each needing its own copy, and the publisher must not know them. Each subscriber has its own channel; the publisher sends once.

- **PUBSUB-1** Use a publish-subscribe channel when an event must reach several systems that each need their own copy. Not with a single consumer (a queue is enough), not when the publisher needs a reply (a synchronous call), and not for sharing the work of one consumer between instances (competing consumers on a single queue).
  Why: a new subscriber is a new binding, not a change to the publisher.
  Check: the publisher publishes to the exchange only; each subscriber consumes its own bound queue.

- **PUBSUB-2** In Mule 4 with Anypoint MQ, the channel is a message exchange with one queue bound to it per subscriber. The bindings are configured in Anypoint MQ, not in the XML, and the exchange accepts only publishing (consuming from it fails). Publish with `anypoint-mq:publish` to the exchange; each subscriber's flow uses `anypoint-mq:subscriber` on its own queue. A publish that succeeds only means the exchange accepted the message: if no queue matches, nothing is delivered. With routing rules, a message that matches no binding goes nowhere. A queue bound later receives only new events.
  Why: each of these is a silent loss that looks like success to the publisher.
  Check: one published event reaches every queue whose binding matches it; an event that matches no binding is checked to go nowhere; a queue bound later receives only new events. Checked by hand, since MUnit has no broker.

- **PUBSUB-3** Each subscriber must tolerate a repeated event: standard queues are at least once (EIP-3). Each queue has its own dead letter queue (DLC-2).
  Why: a copy per subscriber multiplies every repeat.
  Check: each subscriber names its idempotency rule (IDEM-2).

## Circuit Breaker

**The pattern.** When a call to a degrading service keeps failing, retrying it adds load to a system that is already failing. A breaker counts failures; when they cross a threshold it opens and fails fast without calling the service; after a reset timeout it is half-open and lets a limited number of probe calls through: a success closes it, a failure opens it again.

- **CB-1** Use a circuit breaker around an outbound call that can degrade (for example an HTTP call to a payment service), when retry alone would add load to a backend that is going down, and when the call should fail fast and recover on its own. Not when you need an exact failure count under heavy concurrency. Choose the implementation by what it protects. A native circuit breaker of the connector, such as the Anypoint MQ Subscriber's, protects that consumer and keeps its state in the worker. A custom breaker in the flow protects one outbound call and must keep its state where its replicas can read it. A gateway circuit breaker policy limits the concurrent calls an API makes to its backend; it is a different mechanism, not a replacement for the failure-threshold breaker here. Before recommending a gateway policy, check the platform rules (PLAT).
  Why: the three mechanisms share a name and protect different things; a rule that treats them as one leads to the wrong choice.
  Check: the change names the implementation and what it protects.

- **CB-2** In a custom breaker, count only infrastructure errors (timeout, connectivity) toward the threshold. A business error (a declined card) is a correct answer from a healthy backend and never opens the circuit. Specify the state transitions: closed to open when the failures in a window cross the threshold; open to half-open after the reset timeout; half-open to closed on a successful probe and back to open on a failed one. Limit the probes in half-open, because concurrent probes are the load the breaker exists to stop. A global limit across replicas needs an atomic probe permit with a lease (a distributed lock or a conditional write in a shared system); Object Store alone does not provide it. Without that, state the limit per replica and the aggregate number of probes it allows. A blocked call raises a typed error that the flow answers clearly to the caller. Give each independent backend its own circuit key.
  Why: a business error that opens the circuit blocks healthy traffic; unlimited probes defeat the breaker.
  Check: the error handler separates infrastructure from business errors before the breaker counts, and the state transitions are written in the change.

- **CB-3** Test the whole cycle, not only the threshold: open calls fail without reaching the backend; after the reset timeout a successful probe closes the circuit; a failed probe reopens it; concurrent probes stay within the limit; a business error leaves it closed. Know what the state costs: each call reads and writes the state, which adds latency, and replicas that share a store can race, so the count can be off at the start of a circuit.
  Why: a breaker that opens and never recovers, or recovers under load, fails in production with no test showing it.
  Check: MUnit tests (with the `munit` skill when installed) cover each transition listed in CB-2; the probe limit is tested with simultaneous probes across independent replica instances, or the per-replica limit and its aggregate are written in the change; the latency added is measured for the replica count the change runs with.
