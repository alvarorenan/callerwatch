# 📞 CallerWatch API

CallerWatch é uma API de segurança para análise de IPs e números de telefone, detectando atividades suspeitas e maliciosas através de múltiplas fontes de dados.

## 🚀 Funcionalidades

- **Análise de IP**: Verificação de reputação usando AbuseIPDB
- **Autenticação JWT**: Sistema seguro de autenticação
- **Cache Redis**: Performance otimizada com cache
- **Logging Kafka**: Sistema de logs distribuído
- **API REST**: Endpoints bem documentados
- **Docker**: Containerização completa

## 🛠 Tecnologias

- **FastAPI** - Framework web moderno
- **PostgreSQL** - Banco de dados principal
- **Redis** - Cache e sessões
- **Apache Kafka** - Sistema de mensageria
- **Docker** - Containerização
- **Poetry** - Gerenciamento de dependências

## 📋 Pré-requisitos

- Docker e Docker Compose
- Python 3.10+ (para desenvolvimento local)
- Conta no AbuseIPDB (para análise de IPs)

## ⚙️ Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/alvarorenan/callerwatch.git
cd callerwatch
```

### 2. Configurar variáveis de ambiente

Crie o arquivo `.env` baseado no exemplo:

```bash
cp .env.example .env
```

### 3. Editar o arquivo `.env`

```properties
# Database
DATABASE_URL=postgresql://callerwatch:password@localhost:5433/callerwatch

# Redis
REDIS_URL=redis://localhost:6380

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9093

# JWT
JWT_SECRET_KEY=sua-chave-jwt-super-secreta-aqui-mude-em-producao

# AbuseIPDB API (obrigatório para análise de IPs)
ABUSEIPDB_API_KEY=sua-chave-do-abuseipdb-aqui

# Debug
DEBUG=true

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

### 4. Obter chave da AbuseIPDB

1. Acesse [AbuseIPDB](https://www.abuseipdb.com/api)
2. Registre-se gratuitamente
3. Obtenha sua API key
4. Adicione no arquivo `.env`

### 5. Executar com Docker

```bash
# Iniciar todos os serviços
docker compose up -d

# Ver logs
docker compose logs -f

# Parar serviços
docker compose down
```

## 🌐 Endpoints da API

### Autenticação

```bash
# Login
POST /api/v1/auth/login
{
  "username": "admin",
  "password": "admin123"
}
```

### Análise de Segurança

```bash
# Verificar IP
POST /api/v1/security/check/ip
Authorization: Bearer <token>
{
  "ip": "8.8.8.8"
}

# Resposta
{
  "data": {
    "ip": "8.8.8.8",
    "reputation": "safe",
    "score": 0,
    "confidence": 0.95,
    "sources": ["abuseipdb"],
    "details": {
      "country": "US",
      "isp": "Google LLC",
      "usage_type": "Content Delivery Network"
    }
  }
}
```

### Health Check

```bash
# Verificar saúde da API
GET /health
```

### Documentação

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testes

### Executar testes automatizados

```bash
# Dar permissão ao script
chmod +x test-scenarios.sh

# Executar testes
./test-scenarios.sh
```

### Testes manuais

```bash
# 1. Obter token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | \
  jq -r '.access_token')

# 2. Testar IP seguro
curl -X POST "http://localhost:8000/api/v1/security/check/ip" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"ip": "8.8.8.8"}' | jq .

# 3. Testar IP malicioso
curl -X POST "http://localhost:8000/api/v1/security/check/ip" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"ip": "185.220.100.240"}' | jq .
```

## 📊 Critérios de Classificação

### IPs
- **Safe (score 0-15)**: IPs limpos, CDNs conhecidos, poucos reports
- **Suspicious (score 16-49)**: Alguns reports, comportamento questionável
- **Malicious (score 50+)**: Múltiplos reports, atividade confirmadamente maliciosa

## 🐛 Debug e Troubleshooting

### Ver logs detalhados

```bash
# Logs da aplicação
docker logs callerwatch-app-1 -f

# Logs de todos os serviços
docker compose logs -f

# Logs específicos
docker compose logs postgres
docker compose logs redis
docker compose logs kafka
```

### Limpar cache

```bash
# Conectar no Redis
docker exec -it callerwatch-redis-1 redis-cli

# Limpar cache
FLUSHALL

# Sair
exit
```

### Verificar conectividade

```bash
# Testar PostgreSQL
docker exec -it callerwatch-postgres-1 psql -U callerwatch -d callerwatch -c "SELECT version();"

# Testar Redis
docker exec -it callerwatch-redis-1 redis-cli ping

# Ver containers rodando
docker ps
```

### Problemas comuns

#### ❌ Porta já em uso
```bash
# Verificar o que está usando a porta
sudo lsof -i :8000

# Parar containers conflitantes
docker compose down --remove-orphans
```

#### ❌ API key inválida
- Verifique se a chave do AbuseIPDB está correta no `.env`
- Confirme se a chave não expirou
- Teste a chave diretamente:

```bash
curl -G https://api.abuseipdb.com/api/v2/check \
  --data-urlencode "ipAddress=8.8.8.8" \
  -H "Key: sua-chave-aqui" \
  -H "Accept: application/json"
```

#### ❌ Containers não iniciam
```bash
# Rebuild sem cache
docker compose down
docker compose build --no-cache
docker compose up -d
```

## 🔧 Desenvolvimento

### Executar localmente

```bash
# Instalar dependências
poetry install

# Executar aplicação
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Executar testes
poetry run pytest
```

### Estrutura do projeto

```
callerwatch/
├── app/
│   ├── core/           # Configurações e utilitários
│   ├── dependencies/   # Injeção de dependências
│   ├── models/         # Modelos de dados
│   ├── routers/        # Endpoints da API
│   └── services/       # Lógica de negócio
├── tests/              # Testes automatizados
├── docker-compose.yml  # Configuração Docker
├── Dockerfile         # Imagem da aplicação
├── pyproject.toml     # Dependências Python
└── README.md          # Documentação
```

## 📈 Monitoramento

### Métricas disponíveis

- Health check endpoint: `/health`
- Logs estruturados no formato JSON
- Métricas de performance via logs
- Cache hit/miss rates

### Status dos serviços

```bash
# Ver status geral
docker compose ps

# Monitorar recursos
docker stats

# Health check
curl http://localhost:8000/health
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 👨‍💻 Autor

**Alvaro Renan**
- Email: alvaroca1544@gmail.com
- GitHub: [@alvarorenan](https://github.com/alvarorenan)

---

⭐ Se este projeto te ajudou, considere dar uma star!