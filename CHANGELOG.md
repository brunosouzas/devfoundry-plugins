# Changelog

## Unreleased

### Added
- `api-contracts` 0.1.0, skill `api-contract`: before an endpoint is built, check that the spec the application loads describes it; replace a template's placeholder spec, or write the spec in the project when the published one lacks the operations (CONTRACT-1, CONTRACT-2). RES, CON and APISEC ported from the `api-spec` skill of brunosouzas/agent-skills.
- `mule-engineering` 0.1.0, skills `apikit` and `munit`: the spec the router loads and implementation flows that match it (APIKIT-1 to APIKIT-3), and endpoints tested through the HTTP listener (MUNIT-5), with mocks matched by `doc:name` (MUNIT-6). Verified example `apikit/assets/mule4/local-spec-router/`, with its mutation checks.

### Changed
- `engineering-profile` 0.6.0: invokes `api-contract` and `munit` for an API endpoint; `legacyCode: keep` does not keep a template's placeholder spec.

### Changed
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
