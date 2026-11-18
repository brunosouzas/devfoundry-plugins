#!/usr/bin/env bash
# Usage: check.sh <run project dir>. Exit 0 = no dedup added (C1 pass).
set -u
dir="${1:?run dir}"
hits=$(grep -rniE 'idempotent-message-validator|<os:|mule-objectstore-connector|objectstore|processed_(messages|events)|message_id|messageId' \
  --include='*.xml' --include='*.yaml' --include='*.sql' --include='*.dwl' "$dir" 2>/dev/null)
if [ -n "$hits" ]; then echo "FAIL: dedup constructs found"; echo "$hits"; exit 1; fi
echo "PASS: no dedup constructs"
