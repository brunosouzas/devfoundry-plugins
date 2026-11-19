#!/usr/bin/env bash
# Compiles and packages every verified example (plugins/*/skills/*/assets/<platform>/<example>/) without running its
# tests, with MuleSoft's public repositories only (tooling/ci/settings-public.xml). It catches XML that does not parse
# or breaks a schema, and a pom that does not resolve; it does not run MUnit, so it does not catch a wrong reference or
# behaviour: scripts/verify-examples.sh of each skill does, where the EE repository is available.
# Usage: package-examples.sh [maven local repo]. MVN overrides the maven binary. Exit 0 = every example packages.
set -uo pipefail
root="$(cd "$(dirname "$0")/../.." && pwd)"
mvn="${MVN:-mvn}"; rc=0; count=0
args=(-B -q -s "$root/tooling/ci/settings-public.xml" -Dmaven.wagon.http.retryHandler.count=3)
[ -n "${1:-}" ] && args+=(-Dmaven.repo.local="$1")
for example in "$root"/plugins/*/skills/*/assets/*/*/; do
  example="${example%/}"; [ -f "$example/pom.xml" ] || continue
  name="${example#"$root"/plugins/}"; count=$((count + 1))
  tmp="$(mktemp -d)"; cp -R "$example/." "$tmp/"
  if (cd "$tmp" && "$mvn" "${args[@]}" clean package -DskipMunitTests) > "$tmp.log" 2>&1; then
    echo "$name: OK"
  else
    echo "$name: FAILED"; rc=1
    if grep -q '^\[ERROR\]' "$tmp.log"; then grep '^\[ERROR\]' "$tmp.log" | head -20; else tail -n 30 "$tmp.log"; fi
  fi
  rm -rf "${tmp:?}" "$tmp.log"
done
[ "$count" -gt 0 ] || { echo "no example found under plugins/*/skills/*/assets/"; rc=1; }
exit $rc
