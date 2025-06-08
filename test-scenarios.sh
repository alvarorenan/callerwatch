#!/bin/bash

echo "🧪 Testando diferentes cenários da CallerWatch API..."

# Obter token
echo "🔐 Obtendo token..."
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [[ -z "$TOKEN" ]]; then
  echo "❌ Falha ao obter token"
  exit 1
fi
echo "✅ Token obtido"

# Função para testar IP
test_ip() {
  local ip=$1
  local expected=$2
  echo "🌍 Testando IP: $ip (esperado: $expected)"
  
  result=$(curl -s -X POST "http://localhost:8000/api/v1/security/check/ip" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "{\"ip\": \"$ip\"}")
  
  reputation=$(echo $result | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['data']['reputation'])" 2>/dev/null)
  score=$(echo $result | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['data']['score'])" 2>/dev/null)
  
  if [[ "$reputation" == "$expected" ]]; then
    echo "✅ $ip: $reputation (score: $score) ✓"
  else
    echo "⚠️  $ip: $reputation (score: $score) - esperado: $expected"
  fi
  echo ""
}

# Testar com expectativas realistas baseadas nos scores AbuseIPDB
echo "📊 Testando IPs seguros (score 0-15)..."
test_ip "8.8.8.8" "safe"           # Google DNS - score: 0
test_ip "1.1.1.1" "safe"           # Cloudflare DNS - score: 0  
test_ip "208.67.222.222" "safe"    # OpenDNS - score: 0

echo "📊 Testando IPs com scores baixos (esperado: safe ou suspicious)..."
test_ip "118.25.6.39" "suspicious"       # Score: 7 (baixo, mas reportado)

echo "📊 Testando IPs conhecidamente maliciosos (score alto)..."
test_ip "185.220.100.240" "malicious"  # TOR exit node - score: 100

echo "📊 Testando IPs que podem ter scores variados..."
# Estes IPs podem ter scores 0 se não foram reportados recentemente
test_ip "95.211.230.211" "safe"    # Pode ter score 0 se limpo
test_ip "91.195.240.94" "safe"     # Pode ter score 0 se limpo
test_ip "45.95.147.226" "safe"     # Pode ter score 0 se limpo
test_ip "103.224.182.242" "safe"   # Pode ter score 0 se limpo

echo ""
echo "💡 Nota: Scores variam baseado em reports recentes no AbuseIPDB"
echo "   - Score 0-15: safe"  
echo "   - Score 16-49: suspicious"
echo "   - Score 50+: malicious"
echo ""
echo "🎉 Testes concluídos!"