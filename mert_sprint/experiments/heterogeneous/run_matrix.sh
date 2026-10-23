#!/usr/bin/env bash
# Heterogeneous-team matrix on the fast subscription models (via the 127.0.0.1:8787 proxy, $0 API).
# Families: C = Claude Haiku 5.5, O = GPT-6 Luna (requested as gpt-5.4-mini), G = Gemini 3.8 Flash.
#
# Double auction: 3 sellers, chat + boss pressure, scripted ZIP buyers, 8 rounds.
#   Homogeneous CCC, OOO, GGG already exist from earlier sprint runs.
#   Minority (2 vs 1): CCO CCG OOC OOG GGC GGO.  Fully diverse: COG and OGC (seat order swapped).
# Bertrand: two firms, plain profit prompt (P0), 15 rounds: C-O, C-G, O-G cross-family pairs + G-G baseline.
#
# Usage: bash run_matrix.sh   (runs 4 jobs at a time; logs in ./logs)
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
LOGS="$HERE/logs"; mkdir -p "$LOGS"
H="${COLLUSION_HACKATHON:-$(cd "$HERE/../.." && pwd)/collusion_hackathon}"
CDA=$H/llm-agent-collusion
CARTEL=$H/llm-cartel
C=claude-3-5-haiku-latest O=gpt-5.4-mini G=gemini-3.8-flash-low
BC=claude-haiku-5-5

jobs=()
da() { jobs+=("cd $CDA && uv run python src/continuous_double_auction/simulation.py --seller_models $2 $3 $4 --buyer_models zip zip zip --seller_comms_enabled --boss_pressure --rounds 8 --tag het_$1 -y"); }
bt() { jobs+=("cd $CARTEL && uv run python run_game.py --models $2,$3 --prefix P0 --rounds 15 --name het_P0_$1 --overwrite -y"); }

da CCO $C $C $O;  da CCG $C $C $G
da OOC $O $O $C;  da OOG $O $O $G
da GGC $G $G $C;  da GGO $G $G $O
da COG $C $O $G;  da OGC $O $G $C
bt haiku-luna $BC $O;  bt haiku-gemini $BC $G;  bt luna-gemini $O $G;  bt gemini-gemini $G $G
# The planned run tags, one per line: the dashboard reads this with matrix.log to draw batch progress.
printf '%s\n' "${jobs[@]}" | grep -o "het_[A-Za-z0-9_-]*" > "$LOGS/plan.txt"
: > "$LOGS/matrix.log"

run_one() {
  local cmd="$1" tag; tag=$(echo "$cmd" | grep -o "het_[A-Za-z0-9_-]*" | head -1)
  echo "[$(date +%H:%M:%S)] start $tag" >> "$LOGS/matrix.log"
  bash -c "$cmd" > "$LOGS/$tag.log" 2>&1
  echo "[$(date +%H:%M:%S)] done  $tag rc=$?" >> "$LOGS/matrix.log"
}
for cmd in "${jobs[@]}"; do
  while [ "$(jobs -rp | wc -l)" -ge 4 ]; do wait -n; done
  run_one "$cmd" &
done
wait
echo "[$(date +%H:%M:%S)] matrix finished" >> "$LOGS/matrix.log"
