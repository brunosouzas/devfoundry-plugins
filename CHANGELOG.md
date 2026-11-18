# Changelog

## Unreleased

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
