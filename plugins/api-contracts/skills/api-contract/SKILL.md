---
name: api-contract
description: "Makes every REST endpoint start from a spec that describes it, and writes or reviews that spec (OpenAPI 3 or RAML 1.0): operations, types, errors, versioning, security, the API-led layer the API belongs to (system, process, experience) and the limits its contract states. Use before implementing, changing or reviewing an endpoint of an API that routes or validates from a spec (in Mule, an APIkit router), and when writing or reviewing the spec itself, even when the developer only asks for the endpoints \"following the requirements\": first check that the spec the app loads has those operations; when it is a template placeholder or a published asset that lacks them, write or extend the spec in the project. Do NOT use it to decide what the API must do (the requirements come first), for solution architecture (platform, topology, integration strategy, design documents or reviews), for the flow code (mule-engineering), for a client of someone else's API, or to add a spec or a router nobody asked for."
metadata:
  aliases: "raml, openapi, oas, swagger, api spec"
---

# API contract

The spec is the contract: the router checks every request against it, and an operation that is not in the spec does not exist at runtime, whatever the code behind it says. This skill makes sure the endpoints you implement are in the spec the application loads, and gives the rules for writing that spec.

## Steps

1. **Find the spec the application loads.** If the application has no spec-driven router (in Mule: no `apikit:config`, one `http:listener` per flow), say so and do not add a spec or a router unless the request asks for one; the endpoint is still tested through HTTP (mule-engineering's MUNIT-5). Otherwise: Follow the router's configuration, not the folder layout: in Mule, the `api` attribute of `apikit:config` (and the property it reads, if any); `resource::<groupId>:<assetId>:<version>:<classifier>:zip:<file>` names a Maven dependency, a plain file name is read from `src/main/resources/api/`. Open that spec. A dependency's zip is in `~/.m2/repository/<groupId path>/<assetId>/<version>/`, or `mvn dependency:copy -Dartifact=<groupId>:<assetId>:<version>:zip:<classifier>` fetches it.
2. **Check each operation you are asked to build** against it: path, method, parameters (with their types and enums), request body and every response the requirements name. Write the result in your answer, one line per operation: `in the spec` or `missing`.
3. **When an operation is missing (CONTRACT-1, CONTRACT-2):**
   - **Which case it is.** A **placeholder** describes operations unrelated to this API (the main signal; a `template` or `sample` asset id or title only supports it) and has no implementation flows in the app. A **real spec** has operations the app already implements.
   - **A placeholder is replaced:** write this API's spec from the requirements. Keep what it shared that still applies (security scheme, error type, traits).
   - **A real spec is extended, never rewritten:** copy it whole into the project and add the missing operations, so every route that works today still exists.
   - **Where:** when you can publish the spec (the developer asked for it or agreed when asked, api-first AFI-5, and a publish command is in the project), publish a new version and update the dependency. Otherwise write it at `src/main/resources/api/<api-name>.yaml` (or `.raml`, following the project), and point the router at it; when the configuration reads a property (`api="${api.spec}"`), change the property, not the attribute. Add the follow-up to your answer: publish it to Exchange under its own asset id, add it as a dependency and point the router back to its `resource::` coordinates (mule-engineering's APIKIT-1). Publishing is never a reason to leave the operations out.
   - **Check every route, not only the new ones (CONTRACT-1):** list every implementation flow and flow mapping in the app and confirm each matches an operation of the spec the router now loads.
   - Never route around the spec: an implementation flow or a flow mapping for a route the spec lacks is dead code at runtime (mule-engineering's APIKIT-2; load its `apikit` skill when it is installed).
4. **Write or change the spec** by the rules in `${CLAUDE_SKILL_DIR}/rules.md`: start from the requirements; each operation answers one of them. Reuse the project's shared types, error responses and security schemes.
   - **The layer (LAYER).** Name the API's layer in the spec's description (an assumed one goes in "Decisions for you"), keep the contract to that layer's responsibility, and name any rule of another layer the requirements put in it. A new layer, a skipped one or a shortcut to a backend is one recommendation with its costs (LAYER-5, the same decision as api-first AFI-6); until it is decided, build what the requirements describe.
   - **The limits (NFR-1).** Every limit the code enforces (a bound on results, a time budget, a rate) is in the spec with the error it returns. A value the requirements lack is chosen as the pattern says and listed as an assumption; a value the code does not enforce (an SLA) is an open question, not a guess.
5. **Verify:** the spec parses (the application build loads it: APIkit fails the deployment on an invalid spec), and each new operation has a test that goes through the HTTP listener and the router (mule-engineering's munit skill, MUNIT-5), so a route missing from the spec fails a test instead of answering 404 in production.

## Precedence with the project profile

`engineering/profile.yaml` with `legacyCode: keep` keeps the names and files of existing code. It does not make a placeholder spec the contract of new endpoints: replacing or extending the spec is part of the new code.

## Rules

Read `${CLAUDE_SKILL_DIR}/rules.md` and act on every rule as its `Class:` says: `auto`, apply it; `propose`, recommend it, say what it costs, and apply it only when the developer agrees or the task already asks for it or implies it; `ask`, stop and ask the developer before acting on it. Cite a rule by its ID and this skill's version when you apply or break it, for example "breaks CONTRACT-1 (api-contract 1.0.1)".

If the project has an `engineering/profile.yaml`, apply these rules as the `project-profile` skill (engineering-profile) resolves them: skip a rule a pack or the project disabled, use the text and class of an overridden rule, and follow the rules the packs add. A rule marked `(floor)` always applies as written here.
