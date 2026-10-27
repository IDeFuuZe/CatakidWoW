#!/usr/bin/env bash
# Continuous Phase0 harvest (cloud). Prefer finish Phase0 before --from-queue fulltext.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p /tmp/arxiv-census /tmp/arxiv-census-logs
export PYTHONUNBUFFERED=1
LOG=/tmp/arxiv-census-logs/phase0-loop.log
echo "phase0-loop start $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$LOG"
while true; do
  python3 -u run_phase0_pass.py --page-size 100 --max-seconds 10800 >>"$LOG" 2>&1 || true
  if python3 - <<'PY'
import json
from pathlib import Path
p = Path("state/phase0-status.json")
s = json.loads(p.read_text()) if p.exists() else {}
print("status", s.get("status"), "n", s.get("n_phase0_scored_cum"), "next", s.get("next_pointer"), flush=True)
cats = json.loads(Path("categories.json").read_text())["categories"]
nxt = s.get("next_pointer") or {}
raise SystemExit(0 if int(nxt.get("category_index") or 0) >= len(cats) else 1)
PY
  then
    echo "phase0 corpus complete $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$LOG"
    break
  fi
  sleep 30
done
