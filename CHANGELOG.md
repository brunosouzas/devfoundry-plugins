# Changelog

## Unreleased

### Added
- Profile layers (`profiles/SCHEMA.md` v1, `apiVersion: devfoundry/v1`): `extends` lists company or personal rules packs (`kind: RulesPack`, in `engineering/packs/<name>/`), and `rules` overrides, disables or adds rules by ID. Public < packs in order < project. Floor rules (`FLOOR-1`, `FLOOR-2`, `APISEC-1`) cannot be disabled or overridden; an attempt is refused and reported. v0 profiles still read. The merge rules ship with the plugin in `project-profile/references/layers.md`. Marking APISEC-1 as floor would be a MAJOR change from 1.0 on; under 0.x it is a minor bump.
- `engineering-profile` 0.7.0: `project-profile` resolves the layers and reports every changed or refused rule; floor rules in `project-profile/rules.md`; `scripts/resolve-profile.py` (validation and the rules in effect, with tests). `api-contracts` 0.2.0 and `mule-engineering` 0.2.0 apply their rules as resolved.
- Synthetic example pack `profiles/examples/packs/acme-mule/`; eval cases T8 (a pack and a project override) and T9 (a pack tries to disable a floor rule).
- `docs/scope.md`: the three layers (public skills, personal and company rules and agents), what is in and out of scope, and the order of the next pieces.
- `api-contracts` 0.1.0, skill `api-contract`: before an endpoint is built, check that the spec the application loads describes it; replace a template's placeholder spec, or write the spec in the project when the published one lacks the operations (CONTRACT-1, CONTRACT-2). RES, CON and APISEC ported from the `api-spec` skill of brunosouzas/agent-skills.
- `mule-engineering` 0.1.0, skills `apikit` and `munit`: the spec the router loads and implementation flows that match it (APIKIT-1 to APIKIT-3), and endpoints tested through the HTTP listener (MUNIT-5), with mocks matched by `doc:name` (MUNIT-6). Verified example `apikit/assets/mule4/local-spec-router/`, with its mutation checks.

### Changed
- `engineering-profile` 0.6.0: invokes `api-contract` and `munit` for an API endpoint; `legacyCode: keep` does not keep a template's placeholder spec.
- The Circuit Breaker moved from `integration-patterns` into a new plugin, `resilience-patterns` 0.1.0: it is a stability pattern, not an Enterprise Integration Pattern. `integration-patterns` 0.5.0 keeps the book's catalog (Idempotent Receiver). `engineering-profile` 0.5.0 invokes both skills.

## 2026-11-18, bootstrap

### Added
- Repository bootstrap: the `integration-patterns` and `engineering-profile` plugins, migrated from the engineering-plugins proof of concept (see `docs/poc-results.md`).
- `integration-patterns` 0.4.0:
  - references split into platform-neutral files plus Mule 4 realizations (`references/mule4/`);
  - verified examples in `assets/mule4/<pattern>/`;
  - `scripts/verify-examples.sh`.
- Eval tooling in `tooling/evals/`: the fixed cases T1b, T2, T3b, T5 and T6, the runners, and the graders.
- `.claude-plugin/marketplace.json` (marketplace `devfoundry`).
