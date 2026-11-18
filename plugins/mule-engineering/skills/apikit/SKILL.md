---
name: apikit
description: Rules for the APIkit router of a Mule 4 API, with a verified example. Use when creating, changing or reviewing the endpoints of a Mule 4 application that has (or should have) an APIkit router - apikit:config, apikit:router, implementation flows named like get:\resource:config, apikit:flow-mappings - or when an endpoint answers 404, 405 or NOT_IMPLEMENTED although its flow exists. Covers which spec the router loads (an Exchange dependency or a file in the project), how implementation flows match the spec, and the listener flow's error responses. Do NOT use it for the spec's own content (api-contracts), for the logic behind the route (keep it in private flows), or for MUnit details beyond calling the router (munit).
---

# APIkit

The router reads one spec and sends each request to the implementation flow of the matching operation. What the router loads decides what exists at runtime; the build does not compare your flows with the spec. `${CLAUDE_SKILL_DIR}` is this skill's directory.

## Steps

1. **Find the loaded spec** (the `api` attribute of `apikit:config`, and the property it reads) and check that it has every operation you build. If it does not, follow the `api-contract` skill of api-contracts (CONTRACT-1, CONTRACT-2) before writing flows; without that skill, write the spec in `src/main/resources/api/` and point the router at it.
2. **One implementation flow per operation**, named `<method>:\<path with \ for />:<apikit config name>` (path parameters as `(name)`), each with only a flow reference (and maybe a transform) to a private flow that does the work (APIKIT-2, APIKIT-3). Names of the private flows, files and variables come from the project profile (`engineering/profile.yaml`) when there is one.
3. **The listener flow** maps the router's errors to responses: `APIKIT:BAD_REQUEST` 400, `APIKIT:NOT_FOUND` 404, `APIKIT:METHOD_NOT_ALLOWED` 405, `APIKIT:NOT_ACCEPTABLE` 406, `APIKIT:UNSUPPORTED_MEDIA_TYPE` 415, `APIKIT:NOT_IMPLEMENTED` 501, plus the application's own error types. Reuse the template's handler when the project has one.
4. **Test through the listener**: each operation has an MUnit test that sends an HTTP request to the app (`munit` skill, MUNIT-5). This is the only test that fails when the route is missing from the spec.
5. **Take the syntax from the verified example**, not from memory: `${CLAUDE_SKILL_DIR}/references/local-spec-router.md` explains it, and `${CLAUDE_SKILL_DIR}/assets/mule4/local-spec-router/` builds and passes its tests (`scripts/verify-examples.sh`). Its names are placeholders; the project's profile and conventions win.

## Rules

Read `${CLAUDE_SKILL_DIR}/rules.md` and follow every rule. Cite a rule by its ID and this skill's version, for example "breaks APIKIT-2 (apikit 0.1.0)".
