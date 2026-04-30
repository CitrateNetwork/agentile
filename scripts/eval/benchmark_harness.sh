#!/usr/bin/env bash
# benchmark_harness.sh — language-agnostic benchmark runner.
#
# Walks `scripts/eval/scenarios/` looking for executable scenario
# files. Each scenario is responsible for:
#   - Setting up its own preconditions
#   - Running its workload
#   - Emitting one or more lines to stdout in the format:
#       BENCH <metric_name> <value> [unit]
#
# This script aggregates those lines into a single JSON report under
# `scripts/eval/baselines/<timestamp>.json` and a "latest" symlink at
# `scripts/eval/baselines/latest.json`.
#
# `check_regression.py` consumes the JSON to compare a fresh run to
# a stored baseline.
#
# Project owners add scenarios by dropping executables into
# `scripts/eval/scenarios/`. The skeleton ships an empty scenarios
# directory with a README explaining the contract.
#
# Why bash + JSON instead of a heavier framework: zero dependencies,
# every CI environment can run it, the contract (BENCH lines) is
# trivial to implement in any language. Real benchmark frameworks
# (cargo bench, hyperfine, k6) emit results in their own formats —
# adapter scenarios convert their output to BENCH lines.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
find_project_root() {
  local d="$SCRIPT_DIR"
  while [[ "$d" != "/" ]]; do
    [[ -d "$d/.agentile" ]] && { echo "$d"; return 0; }
    d="$(dirname "$d")"
  done
  echo "ERROR: no .agentile/ found above ${SCRIPT_DIR}" >&2
  exit 2
}
PROJECT_ROOT="$(find_project_root)"

SCENARIOS_DIR="${PROJECT_ROOT}/scripts/eval/scenarios"
BASELINES_DIR="${PROJECT_ROOT}/scripts/eval/baselines"
mkdir -p "${BASELINES_DIR}"

TIMESTAMP="$(date -u +%Y-%m-%dT%H%M%SZ)"
GIT_SHA="$(git -C "${PROJECT_ROOT}" rev-parse HEAD 2>/dev/null || echo unknown)"
GIT_BRANCH="$(git -C "${PROJECT_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
RUN_ID="${TIMESTAMP}_${GIT_SHA:0:8}"
OUT_FILE="${BASELINES_DIR}/${RUN_ID}.json"
LATEST="${BASELINES_DIR}/latest.json"

if [[ ! -d "${SCENARIOS_DIR}" ]] || ! find "${SCENARIOS_DIR}" -mindepth 1 -maxdepth 1 -executable -type f | grep -q .; then
  echo "No executable scenarios under ${SCENARIOS_DIR}."
  echo "Writing an empty result file so downstream tooling has something to read."
  cat > "${OUT_FILE}" <<EOF
{
  "run_id": "${RUN_ID}",
  "timestamp": "${TIMESTAMP}",
  "git_sha": "${GIT_SHA}",
  "git_branch": "${GIT_BRANCH}",
  "scenarios": [],
  "metrics": {}
}
EOF
  ln -sfn "${OUT_FILE}" "${LATEST}"
  echo "Wrote ${OUT_FILE}"
  exit 0
fi

# Collect output. Each scenario runs in its own subprocess so a
# failure doesn't kill the harness.
TMPDIR="$(mktemp -d)"
trap 'rm -rf "${TMPDIR}"' EXIT

scenarios_json=()
metrics_json=""

while IFS= read -r -d '' scenario; do
  name="$(basename "${scenario}")"
  log="${TMPDIR}/${name}.log"
  status="ok"
  start_ts="$(date +%s.%N)"
  if ! "${scenario}" > "${log}" 2>&1; then
    status="failed"
  fi
  end_ts="$(date +%s.%N)"
  elapsed="$(awk "BEGIN{print ${end_ts} - ${start_ts}}")"

  # Parse BENCH lines.
  scenario_metrics_json=""
  while IFS= read -r line; do
    # shellcheck disable=SC2206
    fields=( $line )
    if [[ "${#fields[@]}" -ge 3 && "${fields[0]}" == "BENCH" ]]; then
      metric_name="${fields[1]}"
      metric_value="${fields[2]}"
      metric_unit="${fields[3]:-}"
      [[ -n "${scenario_metrics_json}" ]] && scenario_metrics_json+=","
      scenario_metrics_json+="\"${metric_name}\":{\"value\":${metric_value},\"unit\":\"${metric_unit}\"}"
      # Top-level metrics map: scenario.metric_name -> ...
      [[ -n "${metrics_json}" ]] && metrics_json+=","
      metrics_json+="\"${name}.${metric_name}\":{\"value\":${metric_value},\"unit\":\"${metric_unit}\"}"
    fi
  done < "${log}"

  scenario_entry=$(printf '{"name":"%s","status":"%s","elapsed_seconds":%s,"metrics":{%s},"log_excerpt":"%s"}' \
    "${name}" "${status}" "${elapsed}" "${scenario_metrics_json}" \
    "$(tail -c 500 "${log}" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read())[1:-1])')")
  scenarios_json+=("${scenario_entry}")
done < <(find "${SCENARIOS_DIR}" -mindepth 1 -maxdepth 1 -executable -type f -print0 | sort -z)

scenarios_concat="$(IFS=,; echo "${scenarios_json[*]}")"

cat > "${OUT_FILE}" <<EOF
{
  "run_id": "${RUN_ID}",
  "timestamp": "${TIMESTAMP}",
  "git_sha": "${GIT_SHA}",
  "git_branch": "${GIT_BRANCH}",
  "scenarios": [${scenarios_concat}],
  "metrics": {${metrics_json}}
}
EOF

ln -sfn "${OUT_FILE}" "${LATEST}"

echo "Wrote ${OUT_FILE}"
echo "Updated ${LATEST}"

# Brief summary
python3 -c "
import json, sys
d = json.load(open('${OUT_FILE}'))
print(f\"Scenarios: {len(d['scenarios'])}\")
for s in d['scenarios']:
    print(f\"  {s['name']}: {s['status']} ({s['elapsed_seconds']}s, {len(s['metrics'])} metric(s))\")
print(f\"Total metrics: {len(d['metrics'])}\")
"
