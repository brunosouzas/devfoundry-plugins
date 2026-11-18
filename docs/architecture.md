# Architecture

## Principles

- **Capabilities, policies and context are separate.** Skills hold reusable capabilities. The project profile (`engineering/profile.yaml`) holds the conventions that vary between people and companies. The project's code and specs hold the current requirements. A company changes the profile, never the skill.
- **Proactive but safe.** A skill may recommend a pattern the developer did not ask for. Every pattern reference says when NOT to use it, and the skill says why none is needed when none applies.
- **Verifiable.** A pattern's code comes from a project that builds and passes its tests. Changes are checked against fixed cases with a baseline arm.

## Plugins

- **`integration-patterns`:** one skill with a catalog, not one skill per pattern. A single skill chooses between patterns, or none, and does not compete with sibling skills for the same trigger. A pattern can still be asked for by name. Each pattern has:
  - `references/<pattern>.md`: platform-neutral. The problem, when to use, when NOT to use, failures, limits and the test.
  - `references/<platform>/<pattern>.md`: how to build it on that platform. Native options first, then the files of the verified example, and the pitfalls its build caught.
  - `assets/<platform>/<pattern>/`: the verified example, built by `scripts/verify-examples.sh`.
- **`engineering-profile`:** applies `mulesoft.naming` and `mulesoft.precedence` from the profile, and lists each flow's integration decisions (repeats, failures, slow dependencies) before invoking `integration-patterns`.

## Reusable components

A pattern's realization can prefer a ready-made component over code in the flow. For the Mule 4 Circuit Breaker, the order is:

1. a module the project profile approves (`mulesoft.components.circuitBreaker`, already published in the company's Exchange);
2. otherwise, propose the public module [`brunosouzas/mule4-circuit-breaker`](https://github.com/brunosouzas/mule4-circuit-breaker) (MIT). The developer publishes it to their own Exchange, or installs it locally for development;
3. otherwise, the in-flow solution, following the module's design.

Publishing to a company Exchange is an external action: the skill shows the repository, the tag, the target organisation and the command, and waits for the developer's yes. (Planned; not in the first release.)

## Repository layout

```
.claude-plugin/marketplace.json    the devfoundry marketplace
plugins/<plugin>/                  Claude Code plugin layout
profiles/                          profile schema and examples
tooling/evals/                     fixed cases, runners and graders
docs/                              this file, decisions, proof-of-concept results
```

## Naming

- The brand is devFoundry and the repository is `devfoundry-plugins`.
- Plugin and skill names are technical and carry no brand. A plugin name is an immutable slug.
