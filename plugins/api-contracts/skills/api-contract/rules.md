# API contract: rules

Rules for REST API contracts. RES, CON and APISEC come from common REST design practice (ported from the `api-spec` skill of brunosouzas/agent-skills, same IDs). RES-3 gained an exception for bounded results. CONTRACT and CON-5 are new in devFoundry. LAYER and NFR are new in devFoundry: the API-led layers as MuleSoft publishes them, and the limits a contract states. They are rules about one API's responsibility and contract, not solution architecture: the platform, the topology, the integration strategy of a company and the design documents and reviews belong to the team's own process. In an existing API, follow the conventions it already uses and report a difference instead of renaming; these rules decide new resources and types.

How to change this file:
- **Add a rule:** copy an item, give it the next number in its group, write the rule, why it exists and how to check it. A new rule is a MINOR version of the skill.
- **Change a rule:** edit it in place and keep its ID, so old reviews still point at the right rule. A rule that now says the opposite is a MAJOR version; clearer wording is a PATCH.
- **Retire a rule:** keep its ID and heading, replace the text with `(retired in <version>: <reason>)`, and never reuse the number.
- **Floor:** a rule marked `(floor)` cannot be disabled or overridden by a pack or a project profile (`profiles/SCHEMA.md`). Adding or removing the mark is a MAJOR version.
- **Class:** every rule has a `Class:` line that says how the agent acts on it: `auto`, apply it; `propose`, recommend it with what it costs and apply it only when the developer agrees or the task already asks for it or implies it; `ask`, stop and ask the developer before acting on it. A new rule gets a class; a profile can change it by ID (`project-profile`, `references/layers.md`), except on a floor rule.

## Contract first (CONTRACT)

- **CONTRACT-1** Every operation the application implements is in the spec the application loads, with its parameters, request body and responses; a spec from a project template is a placeholder and is replaced by this API's own spec.
  Why: the router answers 404 or 405 for an operation the spec lacks, whatever the code behind it does; tests that call the code directly pass, and the gap shows only in production.
  Check: each implemented operation (method and path) appears in the loaded spec; the loaded spec describes this API (its title and operations), not a template's.
  Class: auto

- **CONTRACT-2** When the published spec lacks the operations and cannot be published from where you work, write the spec in the project (`src/main/resources/api/`), point the router at it, and report publishing it to Exchange as a follow-up. A real published spec is copied whole and extended; only a placeholder is replaced.
  Why: a spec kept in the project lets the application route, validate and be tested now; the follow-up keeps one versioned contract as the goal.
  Check: the router's `api` (or the property it reads) names the project file; the answer lists the publish follow-up.
  Class: auto

## Resources (RES)

- **RES-1** Resources are plural nouns in kebab-case (`/customers/{customerId}/orders`); the HTTP method carries the verb.
  Why: consumers guess URLs from the pattern.
  Check: no verbs in paths (`/getCustomer`).
  Class: auto

- **RES-2** Use methods and status codes for what they mean: `GET` reads and is safe, `POST` creates (`201` with `Location`), `PUT`/`PATCH` update, `DELETE` removes (`204`).
  Why: clients, proxies and caches rely on those meanings.
  Check: every operation's method and success code match.
  Class: auto

- **RES-3** Collections are paginated, with the paging parameters and limits declared in the spec, unless the requirements bound the result (a date range, a fixed small set) and say so.
  Why: an unbounded collection works in testing and times out in production.
  Check: every collection `GET` has paging parameters or a documented bound.
  Class: auto

## Contract (CON)

- **CON-1** Every request and response body has a named data type with required fields, formats and limits declared.
  Why: the type is what validation and the implementation are generated from.
  Check: no inline `object` or `any` bodies.
  Class: auto

- **CON-2** Errors use one shared error type and the status codes the requirements name (`400`, `401`, `403`, `404`, `409`, `500`, `502`, `503`, `504`…), each documented on the operation.
  Why: one error shape lets every consumer handle errors the same way.
  Check: each operation lists its error responses with the shared type.
  Class: auto

- **CON-3** Every request and response, success and error, has an example that validates against its type.
  Why: examples are the documentation consumers read first, and the mock service returns them.
  Check: the validator reports no example errors.
  Class: auto

- **CON-4** The API has a major version in its base URI or name; a breaking change (removed field, new required field, changed type) is a new major version.
  Why: consumers must be able to keep working while they migrate.
  Check: the diff of types and operations has no breaking change within a version.
  Class: auto

- **CON-5** A breaking change to a spec that consumers use (one published, or the project's own spec of a deployed API) is the developer's decision, with the version it goes in. Replacing a template's placeholder spec (CONTRACT-1), or adding to a spec, is not a breaking change.
  Why: consumers outside the change break with it, and a new major version is a new contract to run in parallel; the agent cannot see who depends on the API.
  Check: no breaking change to such a spec unless the developer asked for it or agreed to it; the answer names each one.
  Class: ask

## Security (APISEC)

- **APISEC-1** (floor) Every operation declares its security scheme; a public operation says so explicitly.
  Why: an operation with no declared scheme is easy to deploy unprotected.
  Check: each operation has a `securedBy:` field (RAML) or a `security:` field (OAS).
  Class: auto

## API-led layers (LAYER)

- **LAYER-1** An API states its layer (system, process or experience) in its spec's description and keeps to that layer's responsibility (LAYER-2 to LAYER-4). The layer comes from the requirements, the project's name or its documents; when none says, write the layer you assume in the spec and list it in the answer's "Decisions for you" (api-first AFI-3). When the requirements put a rule of another layer in this API, follow them and name the rule and the layer it would belong to.
  Why: the layer tells consumers what the API promises and tells maintainers what does not belong in it; a rule placed in the wrong layer is copied into every API that needs it again.
  Check: the spec's description names the layer; an assumed layer and each rule of another layer the API holds are named in the answer.
  Class: auto

- **LAYER-2** A System API exposes one system of record in the API's own model: its contract hides the backend's protocol, sessions, field names, codes and error messages, and carries no rule that serves one consumer or one channel. A query parameter over the system's own data belongs here (any consumer may use it); a default, a hard-coded value or a behaviour that only one consumer needs is a channel rule.
  Why: consumers of a System API must survive a change of backend or of its version; a backend name or a channel rule in its contract ties every consumer to both.
  Check: no backend field name, code, envelope or message in the spec's types and examples; no channel rule unless LAYER-1 names it.
  Class: auto

- **LAYER-3** A Process API orchestrates or composes one or more System APIs (and other Process APIs) into a business process, and reaches backends through them. Calling a backend directly instead is the layering decision of LAYER-5.
  Why: a Process API that calls a backend directly duplicates the System API's mapping, credentials and error handling, and breaks when the backend changes.
  Check: the spec exposes no backend concern; the answer names each outbound dependency and its layer.
  Class: auto

- **LAYER-4** An Experience API shapes data for one channel or consumer (the fields, paging, format and errors that channel needs) and calls Process or System APIs; a business rule shared by several channels belongs in a Process API.
  Why: a shared rule kept in one channel's API is copied, then diverges, in the next channel's.
  Check: the contract carries the channel's shape; a business rule the requirements show other channels need is named in the answer.
  Class: auto

- **LAYER-5** A change to the layers: a new System API for a backend, a Process API that calls a backend directly, a layer folded into another or split. Give one recommendation with what each way costs (one more deployment and its operation, the latency of a hop, who owns it; or the coupling the shortcut leaves). This is the same decision as api-first AFI-6: give it once. Until it is decided, build what the requirements describe and list the choice in "Decisions for you".
  Why: a layer is a long-lived application with an owner, a deployment and a contract; it is cheap to propose and expensive to undo.
  Check: each such change appears in the answer once, with both costs and the developer's choice or the requirement that decided it.
  Class: propose

## Limits in the contract (NFR)

- **NFR-1** Every limit the implementation enforces is in the contract with the error it returns: the largest result or date range a request may ask for (`422`), a rate limit (`429`), a time budget (`504`), and the response time when the requirements state one. A value the code needs that the requirements lack (a pattern's bound or budget) is chosen as that pattern's skill says, written in the spec and listed as an assumption in "Decisions for you". The values a pattern chose (a call's timeouts, the request's budget, the status of a request over a limit) go in the spec's description of the API or the operation, so a caller and a reviewer see them without reading the code. A value the code does not enforce (an SLA, a rate the platform applies) is not invented: it stays out of the spec and is listed as an open question. On a spec consumers already use, a new limit is a change to the contract (CON-5).
  Why: a limit that is only in the code surprises every caller the first time it is reached; a stated limit lets them page, narrow or wait.
  Check: each limit the code enforces appears in the spec with its error, and each value a pattern chose is in the description; each value the requirements did not give is in "Decisions for you", as an assumption or an open question.
  Class: auto
