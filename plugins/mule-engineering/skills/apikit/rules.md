# APIkit: rules

Rules for the APIkit router of Mule 4 applications. APIKIT-1 and APIKIT-3 are ported from the `mulesoft` skill of brunosouzas/agent-skills (PLAT-2 and FLOW-1); APIKIT-2 is new. In an existing project, follow the conventions it already uses and report a difference.

How to change this file: add a rule with the next number in its group; edit a rule in place and keep its ID; retire a rule by keeping its ID with `(retired in <version>: <reason>)`, never reusing the number.

## APIkit (APIKIT)

- **APIKIT-1** A spec the application implements is a Maven dependency (classifier `raml` or `oas`, type `zip`), and `apikit:config` names it as `resource::<groupId>:<assetId>:<version>:<classifier>:zip:<file>`; the spec's `assetId` differs from the application's `artifactId`. Until that asset has the operations, the spec lives in `src/main/resources/api/` and the router names that file (api-contract CONTRACT-2), with the move to the dependency reported as a follow-up.
  Why: the router reads the spec by its coordinates, so the application builds against one versioned contract; equal coordinates make the spec and the application overwrite each other on Exchange. A spec in the project is the bridge while the asset cannot be published.
  Check: `apikit:config` uses `resource::`, or a project file with the follow-up stated; the spec's `assetId` is not the POM's `artifactId`.

- **APIKIT-2** Every implementation flow, whether matched by name or by `apikit:flow-mappings`, matches an operation of the loaded spec, and every operation of the spec that the change implements has one.
  Why: the build and the deployment accept a flow or a flow mapping for a route the spec lacks; at runtime the router answers 404 and the flow is dead code.
  Check: list the spec's operations and the implementation flow names (and flow mappings); the two sets match for the operations in scope.

- **APIKIT-3** Keep the API layer thin: implementation flows route and validate; the logic lives in private flows or sub-flows named after what they do.
  Why: renaming or regenerating an implementation flow (a new spec version) must not touch the logic; private flows can be tested and reused on their own.
  Check: implementation flows contain only a flow reference (and maybe a transform).
