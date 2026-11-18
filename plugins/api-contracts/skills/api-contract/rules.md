# API contract: rules

Rules for REST API contracts. RES, CON and APISEC come from common REST design practice (ported from the `api-spec` skill of brunosouzas/agent-skills, same IDs). CONTRACT is new in devFoundry. In an existing API, follow the conventions it already uses and report a difference instead of renaming; these rules decide new resources and types.

How to change this file:
- **Add a rule:** copy an item, give it the next number in its group, write the rule, why it exists and how to check it. A new rule is a MINOR version of the skill.
- **Change a rule:** edit it in place and keep its ID, so old reviews still point at the right rule. A rule that now says the opposite is a MAJOR version; clearer wording is a PATCH.
- **Retire a rule:** keep its ID and heading, replace the text with `(retired in <version>: <reason>)`, and never reuse the number.

## Contract first (CONTRACT)

- **CONTRACT-1** Every operation the application implements is in the spec the application loads, with its parameters, request body and responses; a spec from a project template is a placeholder and is replaced by this API's own spec.
  Why: the router answers 404 or 405 for an operation the spec lacks, whatever the code behind it does; tests that call the code directly pass, and the gap shows only in production.
  Check: each implemented operation (method and path) appears in the loaded spec; the loaded spec's title and asset id name this API, not a template.

- **CONTRACT-2** When the published spec lacks the operations and cannot be published from where you work, write the spec in the project (`src/main/resources/api/`), point the router at it, and report publishing it to Exchange as a follow-up.
  Why: a spec kept in the project lets the application route, validate and be tested now; the follow-up keeps one versioned contract as the goal.
  Check: the router's `api` (or the property it reads) names the project file; the answer lists the publish follow-up.

## Resources (RES)

- **RES-1** Resources are plural nouns in kebab-case (`/customers/{customerId}/orders`); the HTTP method carries the verb.
  Why: consumers guess URLs from the pattern.
  Check: no verbs in paths (`/getCustomer`).

- **RES-2** Use methods and status codes for what they mean: `GET` reads and is safe, `POST` creates (`201` with `Location`), `PUT`/`PATCH` update, `DELETE` removes (`204`).
  Why: clients, proxies and caches rely on those meanings.
  Check: every operation's method and success code match.

- **RES-3** Collections are paginated, with the paging parameters and limits declared in the spec, unless the requirements bound the result (a date range, a fixed small set) and say so.
  Why: an unbounded collection works in testing and times out in production.
  Check: every collection `GET` has paging parameters or a documented bound.

## Contract (CON)

- **CON-1** Every request and response body has a named data type with required fields, formats and limits declared.
  Why: the type is what validation and the implementation are generated from.
  Check: no inline `object` or `any` bodies.

- **CON-2** Errors use one shared error type and the status codes the requirements name (`400`, `401`, `403`, `404`, `409`, `500`, `502`, `503`…), each documented on the operation.
  Why: one error shape lets every consumer handle errors the same way.
  Check: each operation lists its error responses with the shared type.

- **CON-3** Every request and response, success and error, has an example that validates against its type.
  Why: examples are the documentation consumers read first, and the mock service returns them.
  Check: the validator reports no example errors.

- **CON-4** The API has a major version in its base URI or name; a breaking change (removed field, new required field, changed type) is a new major version.
  Why: consumers must be able to keep working while they migrate.
  Check: the diff of types and operations has no breaking change within a version.

## Security (APISEC)

- **APISEC-1** Every operation declares its security scheme; a public operation says so explicitly.
  Why: an operation with no declared scheme is easy to deploy unprotected.
  Check: each operation has a `securedBy:` field (RAML) or a `security:` field (OAS).
