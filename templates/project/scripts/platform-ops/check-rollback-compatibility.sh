#!/usr/bin/env bash
set -euo pipefail
# Exit 0 only when rolling from $1 (current SHA) to $2 (prior known-good SHA)
# is mechanically safe for the project's current schema/data state.
echo 'ERROR: configure rollback compatibility validation before enabling rollback.' >&2
exit 78
