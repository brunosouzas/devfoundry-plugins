---
name: project-profile
description: Use before creating, changing or reviewing any Mule 4 flow, flow file, global configuration element or flow variable (endpoints, queue or event consumers, API calls). Applies the project's engineering profile (engineering/profile.yaml) when there is one, including projects whose existing code uses other names, and makes the flow's integration decisions explicit (repeated messages, failures) before any XML is written.
---

# Project profile

The project's conventions live in `engineering/profile.yaml`, not in this skill. This skill only says how to apply them.

## Steps

0. **Integration decisions (mandatory, before writing or changing any flow).** List, in your answer, the flow's integration decisions:
   - **Repeated message:** can the same message or request reach this flow more than once (broker redelivery, ack timeout, nack, client resend, replay), and what happens to each side effect if it does?
   - **After a failure:** for each step that can fail, what has already happened by then and what the flow does next (retry, redelivery, dead letter, compensation).
   - **A slow or unavailable dependency:** for each synchronous call, what happens to the flow, its callers and the rest of the app when the dependency hangs or fails for minutes.

   Then invoke the `integration-patterns` skill for repeated messages and side effects, and the `resilience-patterns` skill for slow or unavailable dependencies, and follow each one. Apply a pattern only when the problem it solves is present in this flow and none of its "When NOT to use" items applies; otherwise say which item applies and leave the flow without it. Do this whether or not the project has a profile.
1. Read `engineering/profile.yaml` at the project root before writing any Mule XML. If it does not exist, say so and follow the conventions already in the project.
2. Under `mulesoft.naming`, treat every key as a rule that the code must follow. Resolve each pattern by filling its placeholders from the change at hand (for example the resource and the operation of the endpoint). Take placeholder meaning and casing from the profile itself (its comments and examples); never from habit or from another project.
3. Apply each rule:
   - `flow`: the `name` of every flow or sub-flow you create.
   - `implFile`: the file that holds the flow.
   - `globalConfigFile`: the file that holds every global element (listener, request and other configs). Put every global element you add there, never inline in the flow file and never in another existing file.
   - `variable`: the name of every flow variable you create (`set-variable`, `target` attributes).
   - Any other key: apply it the way its name and comment say.
4. Under `mulesoft.precedence`, apply how the profile relates to code that already exists in the project:
   - `newCode: profile`: the rules above win over the surrounding code for everything you add, even when the existing flows, files and variables follow other names. Do not copy legacy names into new code. When the profile's file does not exist yet, create it instead of reusing a legacy file.
   - `legacyCode: keep`: do not rename, move or reformat existing code to fit the profile.
   - `divergence: report`: in your answer, say where the existing code diverges from the profile, as a note for the developer, not as a change.
   - If `precedence` is missing, ask nothing and follow the profile for new code; say so in the answer.
5. Before you finish, list each `mulesoft.naming` key with the value you used, so the reviewer can check it against the profile (skip when there is no profile), and the integration decisions of step 0 with the pattern decision for each.

Do not edit `engineering/profile.yaml` to fit the code. If a rule cannot be applied, say which and why.
