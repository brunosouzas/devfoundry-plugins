#!/usr/bin/env bash
# Regression suite: runs fixed cases in one arm, 3 runs each, for each model, into <out>/<arm>/<model>/.
# Usage: run-suite.sh <baseline|plugin> <out dir> <case>...   e.g. run-suite.sh plugin /tmp/r T1b T2 T5 T6
# MODELS overrides the default models. Cases run in parallel per model; runs of one case run in sequence.
set -uo pipefail
here="$(cd "$(dirname "$0")" && pwd)"; arm="$1"; out="$2"; shift 2
work="${WORK:-$(mktemp -d)}"; models="${MODELS:-claude-opus-5-5 claude-sonnet-5-5}"
plugins=("$here/../../plugins/engineering-profile" "$here/../../plugins/integration-patterns" "$here/../../plugins/resilience-patterns")
for m in $models; do for c in "$@"; do
  ( for n in 1 2 3; do
      if [ "$arm" = baseline ]; then MODEL=$m "$here/run-baseline.sh" "$c" "$n" "$work/$arm" "$out/$arm/$m"
      else MODEL=$m "$here/run-plugin.sh" "$c" "$n" "$work/$arm" "$out/$arm/$m" "${plugins[@]}"; fi
    done ) &
done; done
wait
