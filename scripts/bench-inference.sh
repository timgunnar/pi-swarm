#!/bin/bash
set -euo pipefail

API="${PI_SWARM_API:-http://localhost:8000/api/v1}"
MODEL="${1:-qwen2.5:7b}"
REQUESTS="${2:-20}"

echo "=== pi-swarm Inference Benchmark ==="
echo "Model: $MODEL | Requests: $REQUESTS"
echo ""

total_time=0
success=0

for i in $(seq 1 $REQUESTS); do
    start=$(date +%s%N)
    response=$(curl -s -X POST "$API/inference/chat/completions" \
        -H "Content-Type: application/json" \
        -d "{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}],\"max_tokens\":50}" \
        2>/dev/null) || true
    end=$(date +%s%N)
    elapsed=$(( (end - start) / 1000000 ))

    if echo "$response" | grep -q '"content"'; then
        success=$((success + 1))
        echo "  [$i/$REQUESTS] ${elapsed}ms ✓"
    else
        echo "  [$i/$REQUESTS] ${elapsed}ms ✗ FAILED"
    fi
    total_time=$((total_time + elapsed))
done

avg=$((total_time / REQUESTS))
echo ""
echo "=== Results ==="
echo "Success: $success/$REQUESTS"
echo "Average latency: ${avg}ms"
