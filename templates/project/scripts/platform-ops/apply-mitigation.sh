#!/usr/bin/env bash
set -euo pipefail
# $1 is a mitigation id explicitly declared in .agentic/platform-ops.json.
# Map only named, pre-authorized reversible actions here. Never use this adapter
# for arbitrary shell/SQL, auth/billing/customer-data mutation, or destructive work.
echo 'ERROR: configure scripts/platform-ops/apply-mitigation.sh before enabling operational mitigation.' >&2
exit 78
