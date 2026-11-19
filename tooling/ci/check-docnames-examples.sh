#!/usr/bin/env bash
# Runs mule-app's check-docnames.py (FLOW-2, FLOW-4) on the flow files of every verified example, except those listed
# in tooling/ci/docnames-exempt.txt (examples that predate the mule-app rules). Exit 0 = every checked example passes.
set -uo pipefail
root="$(cd "$(dirname "$0")/../.." && pwd)"
check="$root/plugins/mule-engineering/skills/mule-app/scripts/check-docnames.py"
exempt="$(grep -v '^#' "$root/tooling/ci/docnames-exempt.txt" | sed '/^$/d')"; rc=0; count=0
for example in "$root"/plugins/*/skills/*/assets/*/*/; do
  example="${example%/}"; name="${example#"$root"/plugins/}"
  [ -d "$example/src/main/mule" ] || continue
  if grep -qxF "$name" <<< "$exempt"; then echo "$name: exempt (tooling/ci/docnames-exempt.txt)"; continue; fi
  count=$((count + 1))
  if python3 "$check" "$example/src/main/mule"; then echo "$name: OK"; else echo "$name: FAILED"; rc=1; fi
done
[ "$count" -gt 0 ] || { echo "no example checked"; rc=1; }
exit $rc
