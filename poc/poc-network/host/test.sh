#!/usr/bin/env bash
# Envoie N requêtes au LB et affiche quel téléphone a répondu + temps total.
# Usage : ./test.sh [N]   (défaut 20)
N="${1:-20}"
start=$(date +%s.%N)
for _ in $(seq "$N"); do
    curl -s http://localhost:8000/ | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["node"], d["battery_pct"], d["battery_temp_c"])'
done | sort | uniq -c
end=$(date +%s.%N)
python3 -c "print(f'{$N} requêtes en {$end-$start:.2f} s -> {$N/($end-$start):.1f} req/s (séquentiel)')"
