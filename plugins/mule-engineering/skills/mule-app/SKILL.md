---
name: mule-app
description: Rules for the code of a Mule 4 application, with a verified example - flows and their display names and descriptions, global configuration, project layout, properties per environment, the global error handler and how each error reaches the caller (a backend timeout is 504, never 408), structured logging with the correlation id, and the Maven build. Use when writing, changing or reviewing a Mule 4 application - a flow XML file under src/main/mule/, its global configuration, error handler, loggers or property files - recognised by a pom.xml with mule-application packaging or a mule-artifact.json. Do NOT use it for the names of flows, files and variables when the project has a profile (project-profile), the APIkit router (apikit), MUnit tests (munit), DataWeave scripts (dataweave), the API spec (api-contract), or deploy, CloudHub and API Manager configuration. It supersedes the `mulesoft` skill of brunosouzas/agent-skills when both are installed, keeping its rule IDs.
metadata:
  aliases: "mulesoft, mule, mule 4, anypoint, cloudhub"
---

# Mule application

What is particular to the code of a Mule 4 application: flows, layout, configuration, errors, logging and the build. `${CLAUDE_SKILL_DIR}` is this skill's directory. The router, tests and DataWeave have their own skills in this plugin (`apikit`, `munit`, `dataweave`); use them with this one.

## Steps

1. **Read the project first**: `pom.xml` (runtime, connector and MUnit versions), the global configuration, the error handler, the property files and two or three existing flows. In an existing project, follow its layout and names and report a difference instead of renaming. When the project has an `engineering/profile.yaml`, the `project-profile` skill gives the names; this skill never does.
2. **Build with the toolchain the runtime supports** (BUILD-1): Maven 3.9.x and Java 17 for Mule 4.6 and later. Check `java -version` and `mvn -version` before the first build: a wrong JDK fails with errors that do not mention Java.
3. **Put every environment value in properties** (CFG-1, CFG-3): hosts, ports, paths, client ids and every outbound timeout, the connection timeout included (MERR-3). Secrets come from secure properties or the secret store (FLOOR-2).
4. **Decide how each error reaches the caller** before writing the flows: list the error types the flow can raise (each connector call, each validation, the app's own types) and the status and body the spec gives each one. Map them in the global error handler (MERR-1, MERR-2): a backend timeout is 504 and a failed connection 503 or 502 (MERR-3), and no raw error message reaches the caller. Translate one operation's error with `error-mapping` on that operation: a `raise-error` inside an error handler, or in a flow it calls, logs an ERROR with a stack trace even with `logException="false"`, so a handler that must decide keeps the error in a variable and raises after the `try`.
5. **Name and describe as you build**, not at the end: every processor gets a `doc:name` that says what it does (FLOW-2) and every flow and sub-flow a `doc:description` (FLOW-4).
6. **Log structured entries** with the correlation id at entry, exit and on error, and never a payload or personal data at INFO (MLOG-1, MLOG-2).
7. **Test** every flow change and every mapped error type with MUnit (`munit` skill, MUNIT-1, MUNIT-2), and every DataWeave function (`dataweave` skill).
8. **Verify:** `mvn clean test` (or `verify`), then the name check on the flow files you added or changed, never on legacy files you did not touch. It lists each processor without `doc:name` or with a palette default name and each flow without `doc:description`, and exits 1 when it finds one:

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/check-docnames.py <each added or changed file under src/main/mule>
   ```

9. **Take the syntax from the verified example**, not from memory: `${CLAUDE_SKILL_DIR}/references/mule4/error-handling.md` explains it, and `${CLAUDE_SKILL_DIR}/assets/mule4/error-handling/` builds and passes its tests (`${CLAUDE_SKILL_DIR}/scripts/verify-examples.sh`). Its names are placeholders; the project's profile and conventions win.

## Rules

Read `${CLAUDE_SKILL_DIR}/rules.md` and act on every rule as its `Class:` says: `auto`, apply it; `propose`, recommend it, say what it costs, and apply it only when the developer agrees or the task already asks for it or implies it; `ask`, stop and ask the developer before acting on it. Cite a rule by its ID and this skill's version, for example "breaks MERR-3 (mule-app 1.2.0)".

If the project has an `engineering/profile.yaml`, apply these rules as the `project-profile` skill (engineering-profile) resolves them: skip a rule a pack or the project disabled, use the text and class of an overridden rule, and follow the rules the packs add. A rule marked `(floor)` always applies as written here.
