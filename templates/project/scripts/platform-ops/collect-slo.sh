#!/usr/bin/env bash
set -euo pipefail
# Emit aggregate, redacted JSON only:
# {"environment":"production","objectives":[{"id":"availability","target":0.999,"good_events":9990,"total_events":10000,"source":"..."}]}
echo 'ERROR: configure scripts/platform-ops/collect-slo.sh before enabling error-budget gating.' >&2
exit 78
