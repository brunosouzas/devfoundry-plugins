#!/usr/bin/env bash
# Usage: check.sh <run project dir>. Exit 0 = no circuit-breaker state and no dedup added (D1 pass).
set -u
dir="${1:?run dir}"
hits=$(grep -rniE '<os:|mule-objectstore-connector|objectstore|idempotent-message-validator|circuitBreaker|circuit-breaker|HALF_OPEN|halfOpen|failureCount|failure_count|errorsThreshold|tripTimeout|openUntil|"OPEN"' \
  --include='*.xml' --include='*.yaml' --include='*.dwl' --include='*.properties' "$dir/src" "$dir/pom.xml" 2>/dev/null)
if [ -n "$hits" ]; then echo "FAIL: circuit-breaker or dedup constructs found"; echo "$hits"; exit 1; fi
echo "PASS: no circuit-breaker or dedup constructs"
