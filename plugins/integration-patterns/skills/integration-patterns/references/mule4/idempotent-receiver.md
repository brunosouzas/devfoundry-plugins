# Idempotent Receiver — Mule 4 realization

The why of each piece is in `../idempotent-receiver.md`. This file is how to build it in Mule 4.

A complete, built and tested Mule 4 project is in `${CLAUDE_SKILL_DIR}/assets/mule4/idempotent-receiver/` (this skill's directory). `scripts/verify-examples.sh` builds it and runs its 4 MUnit tests, and every pitfall listed below was caught by that build. Its domain is a payment charge (`paymentId`, `POST /charges`). Adapt the names, the key and the error types to the flow at hand. Do not copy its domain.

Read these files before writing the flow:

| File | What it shows |
| --- | --- |
| `pom.xml` | The `mule-objectstore-connector` dependency (with `<classifier>mule-plugin</classifier>`) next to HTTP and Anypoint MQ |
| `src/main/mule/global.xml` | The persistent Object Store with a finite `entryTtl`, plus the namespaces and schema locations of `os` |
| `src/main/mule/payments.xml` | The broker flow (manual ack, ack after done, nack on error) and the processing flow without a source: claim, call, mark done, with both failure branches |
| `src/test/munit/charge-payment-flow-test-suite.xml` | The 4 tests: duplicate, different keys, a certain failure releases the key, an unknown outcome keeps it |
| `src/main/resources/config.yaml` | The TTL and ack-timeout properties, with the reasons for their values |

## Store

The store must survive restarts and be shared by every replica or worker of the app (`persistent="true"`, plus a finite `entryTtl`). An in-memory or non-persistent store forgets everything on restart. A store local to one node does not see deliveries taken by another node. On CloudHub, the persistent store is Object Store v2; check its TTL ceiling (30 days) and its rate limits for your plan. When the window must be longer, or when you need strict uniqueness under concurrency across replicas, use a database table with a `UNIQUE` constraint on the business key instead.

## Claim, process, mark done

Record the key **before** the side effect, so two concurrent deliveries cannot both pass. Record the outcome **after** it. Keep a state per key:

1. **Claim:** `os:store` with `failIfPresent="true"` and the value `IN_PROGRESS`. If it raises `OS:KEY_ALREADY_EXISTS`, the message is a repeat: read the stored state and do not call the side effect again. `DONE` means it was already handled. `IN_PROGRESS` means another delivery is working on it, or one crashed mid-way (see below).
2. **Process:** call the side effect. If the target accepts an idempotency key, send the business key there too.
3. **Mark done:** overwrite the entry with `DONE` and the result, then acknowledge the source message.

Keep the processing logic in a flow without a source (`charge-payment-flow` in the example), so that MUnit can call it without the broker.

The compact alternative, `<idempotent-message-validator idExpression="..." objectStore="..."/>`, raises `MULE:DUPLICATE_MESSAGE` on a repeat. It records the key as soon as the event passes, with no state, so it still needs the failure handling below.

With Anypoint MQ, use `acknowledgementMode="MANUAL"` on the subscriber and call `anypoint-mq:ack` only after the entry is `DONE`. Set the `acknowledgementTimeout` longer than the slowest side-effect call, so that the broker does not redeliver while the first delivery is still working.

## Pitfalls the build catches (all seen in generated code)

- `anypoint-mq:ack` and `anypoint-mq:nack` need `config-ref`. Without it, the XSD validation fails.
- `os:remove` has no `failIfNotPresent` attribute. Only `os:store` takes `failIfPresent`.
- Using `doc:name` (for example to target an `http:request` from an MUnit mock) needs `xmlns:doc="http://www.mulesoft.org/schema/mule/documentation"` on the `<mule>` element of that file. Without it, the app does not load.
- Store the key as a Java string: `#[output application/java --- payload.orderId as String]`. A value read from a JSON payload keeps the JSON media type, and string concatenation with it (`'...' ++ vars.key`) fails in loggers.
- In MUnit, give the input as serialized JSON: `<munit:payload value='#[output application/json --- { ... }]' mediaType="application/json"/>`. A bare DataWeave object with `mediaType="application/json"` is a Java `Map`, and the flow's first DataWeave fails with "requires a Stream Compatible content".
- `--` is not allowed inside an XML comment.

## Failure handling in Mule

- **Release the key** in the error handler with `os:remove` (`key` and `objectStore` only), then nack so the broker can redeliver.
- **A sure rejection** is an `HTTP:BAD_REQUEST` or another `4xx` that the target documents as "not processed".
- **`HTTP:CONNECTIVITY` is not sure.** Mule reports a refused connection and a connection lost after the request was sent with the same type, so treat it as an unknown outcome unless the flow can tell the two apart.

## The duplicate test in MUnit

Use `assets/mule4/idempotent-receiver/src/test/munit/charge-payment-flow-test-suite.xml` as the model:

- **Duplicate:** clear the store (`os:clear`). Mock the side-effect call, targeted by `doc:name`. Call the processing flow twice with the same key. Then check `verify-call ... times="1"`.
- **Different keys:** two different keys, so `times="2"`.
- **A certain failure releases the key:** the mock raises the error (`<munit-tools:error typeId="HTTP:BAD_REQUEST"/>`). Catch it in a `try` around the `flow-ref`. Then `os:contains` for the key is `false`.
- **An unknown outcome keeps the key:** the mock raises `HTTP:TIMEOUT`. The key is still stored as `IN_PROGRESS`.

Run the tests with `mvn clean test` when the environment allows it.
