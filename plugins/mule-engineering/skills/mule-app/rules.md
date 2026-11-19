# Mule application: rules

Rules for Mule 4 applications: flows, layout, configuration, errors, logging and the build. Most are ported from the `mulesoft` skill of brunosouzas/agent-skills, from MuleSoft's published development practice and the platform's documented behaviour; the IDs are kept, so a review that cites one still points at the same rule. MERR-3 is new. In an existing project, follow the conventions it already uses and report a difference instead of renaming; these rules decide new projects, and new files where the project has no convention of its own.

Not here on purpose:
- **Names.** The project profile (`engineering/profile.yaml`, `project-profile` skill) owns the names of flows, files and variables, and the project's own conventions come next. These rules only ask that a name says what the thing does (FLOW-2) and that a new project picks one convention and keeps it. The naming rules of the `mulesoft` skill (FLOW-5, FLOW-6) are not ported.
- **Rules other skills own.** The APIkit router (APIKIT, `apikit`), tests (MUNIT, `munit`), DataWeave (DW, `dataweave`), the API contract (`api-contract`), secrets (FLOOR-2) and synthetic data (FLOOR-1) of `project-profile`. FLOW-1 and PLAT-2 of the `mulesoft` skill are APIKIT-3 and APIKIT-1 here; CFG-2 is FLOOR-2.
- **Deploy and platform.** CloudHub 2.0 deployment configuration, API Manager policies and health checks for the deploy belong to the delivery process, which is outside devFoundry.

Changed on purpose from the source, each to fit a public skill under a profile:
- FLOW-3 keeps the rule (one definition, referenced by name) and drops its display-name pattern (`<Purpose> <Type> Config`), which is naming.
- LAYOUT-2 and CFG-3 keep the layout but no fixed file names (`<api-name>-main.xml`, `config.yaml`); the profile or the project names the files.
- MERR-1 names the mechanism (`defaultErrorHandler-ref`); MERR-3 is new.
- MLOG-2 is a floor rule.

How to change this file: add a rule with the next number in its group; edit a rule in place and keep its ID; retire a rule by keeping its ID with `(retired in <version>: <reason>)`, never reusing the number. A rule marked `(floor)` protects data or secrets: no layer of the profile can disable or override it.

Every rule has a `Class:` line that says how the agent acts on it: `auto`, apply it; `propose`, recommend it with what it costs and apply it only when the developer agrees or the task already asks for it or implies it; `ask`, stop and ask the developer before acting on it. A new rule gets a class; a profile can change it by ID (`project-profile`, `references/layers.md`), except on a floor rule.

## Flows (FLOW)

- **FLOW-2** Every processor and scope has an explicit `doc:name` that says what it does; never a missing name, never the palette default (`Transform Message`, `Set Variable`, `Logger`, `Try`, `Choice`, `Scatter-Gather`).
  Why: the Studio canvas, logs and Anypoint Monitoring show these names; a flow of unnamed `Set Variable` and `Choice` boxes can only be read by opening each one. A missing `doc:name` is as bad as a default one: Studio shows the component type.
  Check: in `src/main/mule/**/*.xml`, every child of `flow`, `sub-flow`, `try`, `when`, `otherwise`, `foreach`, `parallel-foreach`, `async`, `route`, `error-handler`, `on-error-*` and `until-successful` has `doc:name`, except value elements (`ee:message`, `ee:variables`, `http:headers`, `http:body` and similar), and none equals its palette default. `scripts/check-docnames.py` checks this.
  Class: auto

- **FLOW-3** Global elements (listeners, requesters, connectors, the global error handler) are defined once, in the global configuration files (LAYOUT-2), and referenced by name.
  Why: duplicated configurations drift apart and multiply connection pools.
  Check: no global element is defined twice, and none lives in the entry file or a file of `impl/`.
  Class: auto

- **FLOW-4** Every flow and sub-flow has a one-sentence description in `doc:description` (Studio's Notes tab): what it does and when it is called.
  Why: the name says what, the note says why and from where; it is the first thing a maintainer reads.
  Check: no `flow` or `sub-flow` without `doc:description`; `scripts/check-docnames.py` checks this.
  Class: auto

## Layout (LAYOUT)

- **LAYOUT-1** One Mule application per project, created from Anypoint Studio, Code Builder or an official template. A test helper that is an application of its own is a separate project, never nested inside another application's folder.
  Why: Studio imports one project per folder, and a Mule developer expects to open the application directly; an aggregator or a nested application needs manual setup.
  Check: the application folder has `pom.xml` with `mule-application` packaging and `mule-artifact.json`, and no other Mule project below it.
  Class: auto

- **LAYOUT-2** `src/main/mule/` holds one entry file (the listener or the APIkit router), a `common/` folder with the global configuration and the global error handler, and an `impl/` folder with one file per resource or use case. A file the profile or the project names (the global configuration, an implementation file) goes where it says; the files it does not name follow this layout. In an existing project with another layout (one file per API or per exercise, globals beside the flows), a new file follows the layout the project has, and the difference is reported.
  Why: a maintainer finds the entry point, the shared configuration and each use case without searching.
  Check: new flow files go into these folders (or the ones the profile names, or the layout an existing project already has, reported); no global element in an `impl/` file.
  Class: auto

## Configuration (CFG)

- **CFG-1** Every environment-specific value (host, port, path, timeout, client id) is a property, read from a per-environment file or from runtime properties; nothing environment-specific is written in the XML.
  Why: the same artifact must run in every environment.
  Check: search the XML for hosts, ports, URLs and timeouts written as literals.
  Class: auto

- **CFG-3** Properties live in `src/main/resources/properties/`: a common file holds what is the same in every environment; keys are hierarchical (`crm.retry.maxCount`). What differs per environment comes either from one file per environment, or from runtime properties that the deploy sets; the project's delivery decides which, and never both for one key. A `configuration-properties` element is global to the application: every flow sees its keys, so loading a file that another part of the application does not load can change how that part resolves a placeholder. A new part of a shared application loads its own file with its own key prefix, and the change shows that the existing flows still start: a listener test of each existing listener flow (MUNIT-5), or the application run once with each listener bound to its port, since MUnit's lazy initialization starts only what a test reaches.
  Why: one predictable place per value; a key set in a file and again at deploy has two owners, and nobody knows which one won.
  Check: with per-environment files, one exists for each target environment; with runtime properties, no per-environment file exists and each such key is named in the deploy's configuration; a file added to a shared application has its own name and key prefix.
  Class: auto

## Errors (MERR)

- **MERR-1** Handle errors with one global error handler (`configuration defaultErrorHandler-ref`), plus a local `on-error-continue` or `on-error-propagate` only where the flow needs a specific response. In an existing application with no global handler, where adding one would change how flows that already exist answer (a published or legacy application), the new flows handle their own errors and the difference is reported.
  Why: one place defines the error contract; scattered handlers return inconsistent errors.
  Check: the application sets `defaultErrorHandler-ref`, and each local handler covers a case the global one does not; or the report says why the application has none.
  Class: auto

- **MERR-2** Map each error type to the HTTP status and body the API spec defines; never return a raw Mule error message (`error.description`, `error.detailedDescription`) or a stack trace to the caller.
  Why: internal messages leak implementation detail and break the contract.
  Check: the error responses match the spec's error types; no error description of a call to another system reaches a response body.
  Class: auto

- **MERR-3** A call to another system that times out (`HTTP:TIMEOUT`, or a connector's own timeout error) reaches the caller as `504 Gateway Timeout`; a connection that fails or is refused (`HTTP:CONNECTIVITY`) as `503` or `502`, as the spec defines. Never `408`. Every outbound request configuration of the application sets its response timeout and, where the connector has one, its connection timeout from properties (CFG-1); for HTTP, `responseTimeout` on the request config and `connectionTimeout` on `sockets:tcp-client-socket-properties` inside `http:client-socket-properties` of the connection. A worst case stated for a call counts both, with a margin: the sum is approximate. When the spec gives such a case another status, follow the spec and report the difference.
  Why: `408 Request Timeout` says the caller was too slow to send its request, so a client retries it as its own fault or gives up; `504` and `503` say a system behind the API did not answer, which is what happened. A request with no explicit timeout waits as long as the connector's default, and the response timeout does not bound the TCP connect: a request to a host that does not answer the connect, with `responseTimeout` at 1 s, failed with `HTTP:CONNECTIVITY` after about 30 s, the connector's default connection timeout, and after 2.2 s with a 1 s connection timeout (measured, Mule 4.9.5).
  Check: the global handler maps `HTTP:TIMEOUT` to 504 and `HTTP:CONNECTIVITY` to 503 or 502, each with a test that raises it (MUNIT-2); no `408` in the XML; every outbound requester or connector configuration under `src/main/` sets its response timeout, and its connection timeout where the connector has one, from properties.
  Class: auto

## Logging (MLOG)

- **MLOG-1** Log structured entries through a JSON logger the project already uses or a core logger with a JSON layout in the application's `log4j2.xml`, with the correlation id at the start and end of each inbound flow, and on every error. When `log4j2.xml` is shared and may not change, a core logger writes each entry as one line of JSON text and the report says the layout is unchanged. The verified examples use `message='#[output application/json indent=false --- { event: "orders.entry", correlationId: correlationId }]'`; `output text/plain --- write({...}, "application/json", { indent: false })` also works (seen in a real application). A `write` with no `output text/plain` was logged there as a quoted, escaped string.
  Why: the correlation id is the only way to follow one call across APIs, and structured entries can be searched by it in the log platform.
  Check: the listener flows log `correlationId` at entry, exit and in the error handler; no core `<logger>` in new flows unless `log4j2.xml` gives it a JSON layout or, where `log4j2.xml` may not change, its message is one line of JSON text.
  Class: auto

- **MLOG-2** (floor) Never log a full payload or personal data at INFO or above; log identifiers.
  Why: logs are retained, copied to other platforms and read widely; a payload in a log is personal data outside the system that owns it.
  Check: no `#[payload]`, `message` or a whole request or response body in a logger at INFO or above.
  Class: auto

## Build (BUILD)

- **BUILD-1** Build with Maven 3.9.x, the JDK the runtime supports (17 for Mule 4.6 and later) and a pinned LTS runtime version; never Maven 3.10 with the Mule plugins.
  Why: Maven 3.10 breaks the Mule Maven plugins with `NoSuchMethodError`, and a wrong JDK fails with errors that do not mention Java.
  Check: the build and its wrapper pin Maven 3.9.x and Java 17; the runtime version is explicit in `pom.xml`.
  Class: propose

- **BUILD-2** The POM has a `<name>`, and the dependencies outside test scope have no known vulnerability: upgrade the library that brings one, or pin the fixed version in `dependencyManagement`; never drop the scan.
  Why: publishing to Exchange fails after the whole test run on a missing `name` ("Property name is required"); a vulnerable transitive dependency ships with the application.
  Check: `<name>` present; the project's dependency scan passes without exclusions.
  Class: propose
