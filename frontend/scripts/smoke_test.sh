#!/bin/bash
# Smoke test script for ReCircle deployment
# Run against deployed URLs before demo

set -e

API_URL="${VITE_API_BASE_URL:-http://localhost:8000}"
WEB_URL="${WEB_URL:-http://localhost:5173}"

echo "🧪 ReCircle Smoke Test"
echo "API: $API_URL"
echo "Web: $WEB_URL"
echo ""

# Test 1: Health check
echo "1. Health check..."
curl -sf "$API_URL/health" | grep -q '"status":"ok"' && echo "   ✅ API health OK" || { echo "   ❌ API health failed"; exit 1; }

# Test 2: Version
echo "2. Version endpoint..."
curl -sf "$API_URL/version" | grep -q '"version"' && echo "   ✅ Version OK" || { echo "   ❌ Version failed"; exit 1; }

# Test 3: Twin endpoint
echo "3. Twin graph..."
curl -sf "$API_URL/api/v1/twin" | grep -q '"nodes"' && echo "   ✅ Twin graph OK" || { echo "   ❌ Twin graph failed"; exit 1; }

# Test 4: Simulate endpoint
echo "4. What-if simulation..."
curl -sf -X POST "$API_URL/api/v1/simulate" \
  -H "Content-Type: application/json" \
  -d '{"compliance":0.8,"ticks":10}' | grep -q '"baseline"' && echo "   ✅ Simulate OK" || { echo "   ❌ Simulate failed"; exit 1; }

# Test 5: Advice endpoint (cached)
echo "5. Cached advice..."
curl -sf -X POST "$API_URL/api/v1/advice?use_cached=true" | grep -q '"summary"' && echo "   ✅ Advice OK" || { echo "   ❌ Advice failed"; exit 1; }

# Test 6: Frontend loads
echo "6. Frontend loads..."
curl -sf "$WEB_URL" | grep -q "ReCircle" && echo "   ✅ Frontend OK" || { echo "   ❌ Frontend failed"; exit 1; }

# Test 7: Scan endpoint (with test image)
echo "7. Scan endpoint..."
# Create a minimal test image (1x1 pixel JPEG)
TEST_IMAGE=$(printf '\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x03\x02\x02\x02\x02\x02\x03\x02\x02\x02\x03\x03\x03\x03\x04\x06\x04\x04\x04\x04\x04\x08\x06\x06\x05\x06\x09\x08\n\n\x09\x08\t\t\n\x0c\x0f\x0c\n\x0b\x0e\x0b\t\t\r\x11\r\x0e\x0f\x10\x10\x11\x10\n\x0c\x12\x13\x12\x10\x13\x0f\x10\x10\x10\xff\xc9\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xcc\x00\x06\x00\x10\x10\x05\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xd2\xcf ')
echo "$TEST_IMAGE" | curl -sf -X POST "$API_URL/api/v1/scan" \
  -F "file=@-;filename=test.jpg" \
  -F "source_node_id=1" | grep -q '"predicted_class"' && echo "   ✅ Scan OK" || { echo "   ❌ Scan failed"; exit 1; }

echo ""
echo "🎉 All smoke tests passed!"
echo "✅ Ready for demo"