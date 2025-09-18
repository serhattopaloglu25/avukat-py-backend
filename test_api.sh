#!/bin/bash

API_URL=${1:-"http://localhost:8000"}

echo "🧪 Testing AA-PY Backend API at: $API_URL"
echo "=================================="

# 1. Ping test
echo "1️⃣ Testing /ping endpoint..."
curl -sS -m 5 "$API_URL/ping" | python3 -m json.tool

# 2. Health check
echo -e "\n2️⃣ Testing /health endpoint..."
curl -sS -m 5 "$API_URL/health" | python3 -m json.tool

# 3. Register test user
echo -e "\n3️⃣ Registering test user..."
REGISTER_RESPONSE=$(curl -sS -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123456",
    "name": "Test User"
  }')
echo "$REGISTER_RESPONSE" | python3 -m json.tool

# Extract token
TOKEN=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))")

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get token"
    exit 1
fi

echo "✅ Got token: ${TOKEN:0:20}..."

# 4. Test /me endpoint
echo -e "\n4️⃣ Testing /auth/me endpoint..."
curl -sS "$API_URL/auth/me" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 5. Test stats
echo -e "\n5️⃣ Testing /api/stats endpoint..."
curl -sS "$API_URL/api/stats" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 6. Create a client
echo -e "\n6️⃣ Creating a test client..."
CLIENT_RESPONSE=$(curl -sS -X POST "$API_URL/api/clients" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "555-0123",
    "address": "123 Main St"
  }')
echo "$CLIENT_RESPONSE" | python3 -m json.tool
CLIENT_ID=$(echo "$CLIENT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))")

# 7. Create a case
echo -e "\n7️⃣ Creating a test case..."
CASE_RESPONSE=$(curl -sS -X POST "$API_URL/api/cases" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"client_id\": $CLIENT_ID,
    \"case_number\": \"2024-001\",
    \"title\": \"Test Case\",
    \"status\": \"active\"
  }")
echo "$CASE_RESPONSE" | python3 -m json.tool
CASE_ID=$(echo "$CASE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))")

# 8. Create an event
echo -e "\n8️⃣ Creating a test event..."
curl -sS -X POST "$API_URL/api/events" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"case_id\": $CASE_ID,
    \"title\": \"Court Hearing\",
    \"type\": \"hearing\",
    \"starts_at\": \"2024-06-01T10:00:00\",
    \"ends_at\": \"2024-06-01T12:00:00\",
    \"location\": \"Courthouse Room 201\"
  }" | python3 -m json.tool

# 9. List all data
echo -e "\n9️⃣ Listing all clients..."
curl -sS "$API_URL/api/clients" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo -e "\n🎯 All tests completed!"
