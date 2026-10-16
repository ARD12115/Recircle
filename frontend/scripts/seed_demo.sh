#!/bin/bash
# Seed demo data script
# Resets demo data and starts traffic generator

set -e

API_URL="${VITE_API_BASE_URL:-http://localhost:8000}"

echo "🌱 ReCircle Demo Data Seed"
echo "API: $API_URL"
echo ""

# Reset demo data
echo "Resetting demo data..."
curl -sf -X POST "$API_URL/api/v1/admin/demo/reset" | grep -q "reset" && echo "   ✅ Demo data reset" || { echo "   ❌ Reset failed"; exit 1; }

# Start traffic generator
echo "Starting traffic generator..."
curl -sf -X POST "$API_URL/api/v1/admin/demo/traffic?start=true" | grep -q "started" && echo "   ✅ Traffic generator started" || { echo "   ❌ Traffic start failed"; exit 1; }

# Wait a moment for initial events
sleep 2

# Verify twin is updating
echo "Verifying twin updates..."
curl -sf "$API_URL/api/v1/twin" | grep -q '"nodes"' && echo "   ✅ Twin responding" || { echo "   ❌ Twin verification failed"; exit 1; }

echo ""
echo "✅ Demo seeded and traffic running"
echo "🎯 Ready for live demo"