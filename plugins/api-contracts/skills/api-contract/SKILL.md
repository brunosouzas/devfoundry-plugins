---
name: api-contract
description: Makes every REST endpoint start from a spec that describes it, and writes or reviews that spec (OpenAPI 3 or RAML 1.0). Use before implementing, changing or reviewing an endpoint of an API, in Mule (APIkit) or any framework that routes or validates from a spec, and when writing or reviewing the spec itself (openapi.yaml, *.raml, their types, examples and fragments). Use it even when the developer only asks for the endpoints "following the requirements": first check that the spec the app actually loads has those operations; when it is a template placeholder or a published asset that lacks them, write or extend the spec in the project. Do NOT use it to decide what the API must do (the requirements come first), for the flow code behind the route (mule-engineering), or for a client that only calls someone else's API.
---

# API contract

The spec is the contract: the router checks every request against it, and an operation that is not in the spec does not exist at runtime, whatever the code behind it says. This skill makes sure the endpoints you implement are in the spec the application loads, and gives the rules for writing that spec.

## Steps

1. **Find the spec the application loads.** Follow the router's configuration, not the folder layout: in Mule, the `api` attribute of `apikit:config` (and the property it reads, if any); `resource::<groupId>:<assetId>:<version>:<classifier>:zip:<file>` names a Maven dependency, a plain file name is read from `src/main/resources/api/`. Open that spec. A dependency's zip is in `~/.m2/repository/<groupId path>/<assetId>/<version>/`, or `mvn dependency:copy -Dartifact=<groupId>:<assetId>:<version>:zip:<classifier>` fetches it.
2. **Check each operation you are asked to build** against it: path, method, parameters (with their types and enums), request body and every response the requirements name. Write the result in your answer, one line per operation: `in the spec` or `missing`.
3. **When an operation is missing (CONTRACT-1, CONTRACT-2):**
   - A spec that came from a project template (`template`, `sample` or `example` in its asset id or title, or operations unrelated to this API) is a placeholder: it is replaced, not kept.
   - Write the spec for this API in the project, at `src/main/resources/api/<api-name>.yaml` (or `.raml`, following the project), from the requirements. Keep what the old spec shared that still applies (security scheme, error type, traits).
   - Point the router at it. When the configuration reads a property (`api="${api.spec}"`), change the property, not the attribute.
   - In your answer, add the follow-up: publish the spec to Exchange under its own asset id, add it as a dependency and point the router back to its `resource::` coordinates (mule-engineering's APIKIT-1). Publishing is never a reason to leave the operations out.
   - Never route around the spec: an implementation flow or a flow mapping for a route the spec lacks is dead code at runtime (mule-engineering's APIKIT-2).
4. **Write or change the spec** by the rules in `${CLAUDE_SKILL_DIR}/rules.md`: start from the requirements; each operation answers one of them. Reuse the project's shared types, error responses and security schemes.
5. **Verify:** the spec parses (the application build loads it: APIkit fails the deployment on an invalid spec), and each new operation has a test that goes through the HTTP listener and the router (mule-engineering's munit skill, MUNIT-5), so a route missing from the spec fails a test instead of answering 404 in production.

## Precedence with the project profile

`engineering/profile.yaml` with `legacyCode: keep` keeps the names and files of existing code. It does not make a placeholder spec the contract of new endpoints: replacing or extending the spec is part of the new code.

## Rules

Read `${CLAUDE_SKILL_DIR}/rules.md` and follow every rule. Cite a rule by its ID and this skill's version when you apply or break it, for example "breaks CONTRACT-1 (api-contract 0.1.0)".
