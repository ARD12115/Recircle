#!/bin/bash
# Warm-up script for ReCircle deployment
# Run 10 minutes before demo to avoid cold starts

set -e

API_URL="${VITE_API_BASE_URL:-http://localhost:8000}"
WEB_URL="${WEB_URL:-http://localhost:5173}"

echo "🔥 ReCircle Warm-up"
echo "API: $API_URL"
echo "Web: $WEB_URL"
echo ""

# Warm up API endpoints
echo "Warming up API..."
for i in {1..3}; do
  echo "  Pass $i/3..."
  curl -sf "$API_URL/health" > /dev/null
  curl -sf "$API_URL/api/v1/twin" > /dev/null
  curl -sf -X POST "$API_URL/api/v1/simulate" \
    -H "Content-Type: application/json" \
    -d '{"compliance":0.6,"ticks":5}' > /dev/null
  curl -sf -X POST "$API_URL/api/v1/advice?use_cached=true" > /dev/null
  sleep 2
done

# Warm up frontend
echo "Warming up frontend..."
curl -sf "$WEB_URL" > /dev/null

echo ""
echo "✅ Warm-up complete - no cold starts expected"