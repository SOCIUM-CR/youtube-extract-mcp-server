# Arquitectura Remota Propuesta

**Versión:** 1.0
**Fecha:** 2025-11-05
**Target:** Fase 3 del Roadmap

---

## 🎯 Objetivos de Diseño

1. **Escalabilidad horizontal** - Auto-scaling basado en demanda
2. **Alta disponibilidad** - 99.9%+ uptime
3. **Seguridad enterprise** - OAuth 2.1, encryption, isolation
4. **Multi-tenancy** - Aislamiento de datos por usuario
5. **Performance** - Latencia < 500ms p95
6. **Observabilidad** - Logs, metrics, traces completos

---

## 🏗️ Arquitectura de Sistema

### Vista de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────┐
│                         Internet / WAN                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ HTTPS (TLS 1.3)
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                     Edge / CDN Layer                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  CloudFlare / Fastly                                     │  │
│  │  • DDoS Protection                                       │  │
│  │  • SSL Termination                                       │  │
│  │  • Rate Limiting (global)                                │  │
│  │  • Geolocation routing                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                   Application Gateway                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Gateway (Kong / AWS API Gateway)                    │  │
│  │  • OAuth 2.1 Token Validation                            │  │
│  │  • Request routing                                       │  │
│  │  • Rate limiting (per-user)                              │  │
│  │  • Request transformation                                │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────┬───────────────────────────────┬───────────────────────────┘
      │                               │
      │                               │
┌─────▼───────────────┐     ┌─────────▼────────────┐
│  Auth Service       │     │  MCP Server Fleet    │
│  ┌───────────────┐  │     │  ┌────────────────┐  │
│  │ OAuth 2.1     │  │     │  │ Auto-scaling   │  │
│  │ (Auth0/       │  │     │  │ K8s Deployment │  │
│  │  Cognito)     │  │     │  │                │  │
│  │               │  │     │  │ ┌────────────┐ │  │
│  │ • User DB     │  │     │  │ │ Server 1   │ │  │
│  │ • Token mgmt  │  │     │  │ ├────────────┤ │  │
│  │ • JWKS        │  │     │  │ │ Server 2   │ │  │
│  └───────────────┘  │     │  │ ├────────────┤ │  │
└─────────────────────┘     │  │ │ Server N   │ │  │
                            │  │ └────────────┘ │  │
                            │  │                │  │
                            │  │ Each Server:   │  │
                            │  │ • FastAPI      │  │
                            │  │ • SSE Support  │  │
                            │  │ • Session Mgmt │  │
                            │  └────────────────┘  │
                            └──┬──────────────┬────┘
                               │              │
                ┌──────────────┘              └─────────────┐
                │                                           │
    ┌───────────▼──────────┐                  ┌────────────▼────────┐
    │  State / Cache       │                  │  Persistent Storage │
    │  ┌────────────────┐  │                  │  ┌──────────────┐   │
    │  │ Redis Cluster  │  │                  │  │ PostgreSQL   │   │
    │  │                │  │                  │  │              │   │
    │  │ • Sessions     │  │                  │  │ • Users      │   │
    │  │ • Cache        │  │                  │  │ • Metadata   │   │
    │  │ • Rate limits  │  │                  │  │ • History    │   │
    │  └────────────────┘  │                  │  └──────────────┘   │
    └──────────────────────┘                  └─────────────────────┘
                                                        │
                                              ┌─────────▼──────────┐
                                              │  Object Storage    │
                                              │  ┌──────────────┐  │
                                              │  │ S3 / GCS     │  │
                                              │  │              │  │
                                              │  │ • Transcripts│  │
                                              │  │ • Metadata   │  │
                                              │  └──────────────┘  │
                                              └────────────────────┘
```

---

## 📦 Componentes Detallados

### 1. Edge / CDN Layer

**Responsabilidad:** Primera línea de defensa y optimización

**Tecnología Recomendada:** CloudFlare Workers

**Funciones:**
```javascript
// CloudFlare Worker example
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  // Rate limiting global
  const ip = request.headers.get('CF-Connecting-IP')
  const rateLimitKey = `rate:${ip}`

  if (await isRateLimited(rateLimitKey)) {
    return new Response('Too Many Requests', { status: 429 })
  }

  // DDoS protection patterns
  if (await detectSuspiciousPattern(request)) {
    return new Response('Forbidden', { status: 403 })
  }

  // Forward to origin
  return fetch(request)
}
```

**Beneficios:**
- ✅ DDoS mitigation automática
- ✅ SSL/TLS offloading
- ✅ Caching de responses estáticas
- ✅ Geolocation routing (latencia óptima)

---

### 2. API Gateway

**Responsabilidad:** Orquestación y seguridad

**Tecnología Recomendada:** Kong Gateway (open-source) o AWS API Gateway

**Configuración Kong:**
```yaml
# kong.yml
services:
  - name: youtube-extract-mcp
    url: http://mcp-servers:8000
    routes:
      - name: mcp-endpoint
        paths:
          - /mcp/endpoint
        methods:
          - POST
      - name: mcp-sse
        paths:
          - /mcp/sse
        methods:
          - GET

plugins:
  - name: oauth2
    config:
      enable_authorization_code: true
      enable_client_credentials: true
      mandatory_scope: true
      scopes:
        - youtube:extract
        - youtube:history

  - name: rate-limiting
    config:
      minute: 60
      hour: 1000
      policy: redis
      redis_host: redis-cluster

  - name: correlation-id
    config:
      header_name: X-Request-ID
      generator: uuid

  - name: request-transformer
    config:
      add:
        headers:
          - X-User-Id: $(oauth.user_id)
```

---

### 3. MCP Server Fleet

**Responsabilidad:** Core business logic

**Tecnología:** FastAPI + Uvicorn + Docker + Kubernetes

#### Estructura de Código

```
mcp-server/
├── src/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   │
│   ├── transports/
│   │   ├── __init__.py
│   │   ├── stdio.py            # Backward compatibility
│   │   └── http.py             # HTTP + SSE transport
│   │
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── youtube.py          # Core extraction logic
│   │   └── playlist.py         # Playlist processing
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py             # Token validation
│   │   ├── rate_limit.py       # Per-user rate limiting
│   │   ├── logging.py          # Structured logging
│   │   └── tracing.py          # Distributed tracing
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── cache.py            # Redis caching layer
│   │   ├── database.py         # PostgreSQL operations
│   │   └── object_store.py     # S3/GCS operations
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # User model
│   │   ├── transcript.py       # Transcript model
│   │   └── session.py          # Session model
│   │
│   └── utils/
│       ├── __init__.py
│       ├── metrics.py          # Prometheus metrics
│       └── validators.py       # Input validation
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── load/
│
├── docker/
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   └── docker-compose.yml
│
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── hpa.yaml               # Horizontal Pod Autoscaler
│   ├── configmap.yaml
│   └── secrets.yaml
│
├── terraform/
│   ├── main.tf
│   ├── vpc.tf
│   ├── gke.tf                 # Google Kubernetes Engine
│   └── redis.tf
│
├── requirements.txt
├── pyproject.toml
└── README.md
```

#### FastAPI Application (main.py)

```python
from fastapi import FastAPI, Header, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse
from prometheus_fastapi_instrumentator import Instrumentator
import structlog

from .middleware import auth, rate_limit, logging as log_middleware
from .storage import cache, database
from .extractors import youtube
from .models import session as session_model

# Structured logging
logger = structlog.get_logger()

# FastAPI app
app = FastAPI(
    title="YouTube Extract MCP Server",
    version="2.0.0",
    docs_url="/docs"
)

# Middleware stack
app.add_middleware(log_middleware.StructuredLoggingMiddleware)
app.add_middleware(auth.OAuthMiddleware)
app.add_middleware(rate_limit.RateLimitMiddleware)

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Session storage (Redis)
session_store = session_model.SessionStore(cache.redis_client)

# Dependency injection
async def get_user_id(authorization: str = Header(...)) -> str:
    """Extract and validate user ID from OAuth token"""
    return await auth.validate_token(authorization)

async def get_session(
    mcp_session_id: str = Header(None),
    user_id: str = Depends(get_user_id)
) -> session_model.Session:
    """Get or create session"""
    if not mcp_session_id:
        session = await session_store.create_session(user_id)
    else:
        session = await session_store.get_session(mcp_session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(status_code=403, detail="Invalid session")

    return session

# MCP Endpoints
@app.post("/mcp/endpoint")
async def mcp_request(
    request: dict,
    session: session_model.Session = Depends(get_session)
):
    """Handle MCP JSON-RPC requests"""
    logger.info("mcp_request", method=request.get("method"))

    # Route to appropriate handler
    method = request.get("method")
    params = request.get("params", {})

    if method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})

        if tool_name == "youtube_extract_video":
            result = await youtube.extract_video(
                url=tool_args["url"],
                user_id=session.user_id,
                **tool_args
            )
        elif tool_name == "youtube_extract_playlist":
            result = await youtube.extract_playlist(
                url=tool_args["playlist_url"],
                user_id=session.user_id,
                **tool_args
            )
        else:
            raise HTTPException(status_code=400, detail="Unknown tool")

    elif method == "tools/list":
        result = await get_tools_list()

    else:
        raise HTTPException(status_code=400, detail="Unknown method")

    return {
        "jsonrpc": "2.0",
        "id": request.get("id"),
        "result": result
    }

@app.get("/mcp/sse")
async def sse_stream(
    session: session_model.Session = Depends(get_session)
):
    """Server-sent events for notifications"""
    async def event_generator():
        async for notification in session.notifications():
            yield {
                "data": notification.json()
            }

    return EventSourceResponse(event_generator())

# Health checks
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/readiness")
async def readiness():
    """Readiness check (dependencies)"""
    redis_ok = await cache.ping()
    db_ok = await database.ping()

    if not (redis_ok and db_ok):
        raise HTTPException(status_code=503, detail="Dependencies unhealthy")

    return {"status": "ready"}
```

#### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: youtube-extract-mcp
  labels:
    app: youtube-extract-mcp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: youtube-extract-mcp
  template:
    metadata:
      labels:
        app: youtube-extract-mcp
    spec:
      containers:
      - name: mcp-server
        image: gcr.io/project/youtube-extract-mcp:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: mcp-config
              key: redis_url
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: mcp-secrets
              key: database_url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /readiness
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: youtube-extract-mcp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: youtube-extract-mcp
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
```

---

### 4. State Management (Redis)

**Responsabilidad:** Sessions, caching, rate limiting

**Esquema de Datos:**

```redis
# Sessions
SET session:{session_id} '{"user_id":"user123","created_at":1699123456}'
EXPIRE session:{session_id} 3600

# Caching transcriptions
SET transcript:{video_id} '{...transcript_data...}'
EXPIRE transcript:{video_id} 86400  # 24h

# Rate limiting
INCR rate_limit:{user_id}:minute
EXPIRE rate_limit:{user_id}:minute 60

# User quotas
HINCRBY user:{user_id}:usage requests_today 1
HINCRBY user:{user_id}:usage videos_extracted 1
```

**Configuración Redis Cluster:**
```yaml
# redis-cluster configuration
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 5000
appendonly yes
maxmemory 2gb
maxmemory-policy allkeys-lru
```

---

### 5. Persistent Storage (PostgreSQL)

**Responsabilidad:** User data, metadata, history

**Schema:**

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    subscription_tier VARCHAR(50) DEFAULT 'free',
    quota_daily_requests INT DEFAULT 100,
    quota_monthly_videos INT DEFAULT 1000
);

-- Transcripts metadata
CREATE TABLE transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    video_id VARCHAR(20) NOT NULL,
    video_title TEXT,
    channel_name VARCHAR(255),
    language VARCHAR(10),
    duration_seconds INT,
    extracted_at TIMESTAMP DEFAULT NOW(),
    source_method VARCHAR(50),  -- yt-dlp / youtube-transcript-api
    s3_path TEXT,  -- Object storage path
    INDEX idx_user_id (user_id),
    INDEX idx_video_id (video_id),
    INDEX idx_extracted_at (extracted_at)
);

-- Usage logs
CREATE TABLE usage_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    tool_name VARCHAR(100),
    request_id UUID,
    latency_ms INT,
    success BOOLEAN,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id_created (user_id, created_at)
);

-- API keys (for programmatic access)
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    key_hash VARCHAR(64) NOT NULL,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

---

## 🔐 Seguridad y Compliance

### OAuth 2.1 Implementation

**Protected Resource Metadata:**

```json
// GET /.well-known/oauth-protected-resource
{
  "resource": "https://youtube-extract.example.com",
  "authorization_servers": [
    "https://auth.example.com"
  ],
  "bearer_methods_supported": ["header"],
  "resource_documentation": "https://docs.youtube-extract.example.com"
}
```

**Token Validation:**

```python
# src/middleware/auth.py
import jwt
from jwt import PyJWKClient

class OAuthMiddleware:
    def __init__(self, jwks_url: str):
        self.jwk_client = PyJWKClient(jwks_url)

    async def validate_token(self, authorization: str) -> str:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401)

        token = authorization[7:]

        try:
            # Get signing key
            signing_key = self.jwk_client.get_signing_key_from_jwt(token)

            # Verify token
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience="youtube-extract-mcp",
                issuer="https://auth.example.com"
            )

            # Extract user ID
            user_id = claims["sub"]
            return user_id

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidAudienceError:
            raise HTTPException(status_code=401, detail="Invalid audience")
        except Exception as e:
            logger.error("token_validation_failed", error=str(e))
            raise HTTPException(status_code=401, detail="Invalid token")
```

### Data Isolation (Multi-tenancy)

**Principio:** Todo query incluye `user_id`

```python
# src/extractors/youtube.py
async def extract_video(url: str, user_id: str, **kwargs):
    # Check user quota
    usage_today = await database.get_usage(user_id, period="today")
    user_quota = await database.get_user_quota(user_id)

    if usage_today >= user_quota:
        raise HTTPException(status_code=429, detail="Quota exceeded")

    # Extract video (core logic unchanged)
    result = await _extract_video_internal(url, **kwargs)

    # Save with user isolation
    await database.save_transcript(
        user_id=user_id,  # CRITICAL: always scope by user
        video_id=result["video_id"],
        data=result
    )

    # Log usage
    await database.increment_usage(user_id)

    return result
```

---

## 📊 Observabilidad

### Structured Logging (structlog)

```python
# Example log output (JSON)
{
  "event": "mcp_request",
  "timestamp": "2025-11-05T12:34:56.789Z",
  "level": "info",
  "user_id": "user_123",
  "request_id": "abc-def-ghi",
  "method": "youtube_extract_video",
  "url": "https://youtube.com/watch?v=...",
  "latency_ms": 4523,
  "cache_hit": false
}
```

### Metrics (Prometheus)

```python
# src/utils/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
mcp_requests_total = Counter(
    "mcp_requests_total",
    "Total MCP requests",
    ["method", "status"]
)

mcp_request_duration_seconds = Histogram(
    "mcp_request_duration_seconds",
    "MCP request duration",
    ["method"]
)

# Business metrics
videos_extracted_total = Counter(
    "videos_extracted_total",
    "Total videos extracted",
    ["source_method"]  # yt-dlp / youtube-transcript-api
)

active_users_gauge = Gauge(
    "active_users",
    "Currently active users"
)
```

### Distributed Tracing (OpenTelemetry)

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

async def extract_video(url: str, user_id: str):
    with tracer.start_as_current_span("extract_video") as span:
        span.set_attribute("user_id", user_id)
        span.set_attribute("video_url", url)

        # Cache check
        with tracer.start_as_current_span("cache_check"):
            cached = await cache.get(url)

        if cached:
            span.set_attribute("cache_hit", True)
            return cached

        # Extraction
        with tracer.start_as_current_span("yt_dlp_extract"):
            result = await _yt_dlp_extract(url)

        return result
```

---

## 🚀 Deployment Pipeline

### CI/CD (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest tests/ --cov

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: |
          docker build -t gcr.io/$PROJECT/youtube-extract-mcp:$SHA .
          docker push gcr.io/$PROJECT/youtube-extract-mcp:$SHA

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to GKE
        run: |
          kubectl set image deployment/youtube-extract-mcp \
            mcp-server=gcr.io/$PROJECT/youtube-extract-mcp:$SHA
          kubectl rollout status deployment/youtube-extract-mcp
```

---

## 💰 Estimación de Costos Detallada

### Escenario: 10,000 Usuarios Activos

**Cómputo (Google Cloud Run):**
- Requests: 10,000 users × 20 req/day × 30 = 6M req/month
- CPU time: 6M × 5s avg = 30M seconds
- Memory: 512MB per request

```
CPU: 30M vCPU-seconds × $0.024 / 1000 = $720
Memory: 30M GB-seconds × $0.0024 / 1000 = $72
Requests: 6M × $0.40 / 1M = $2.40
Total Compute: ~$795/month
```

**Redis (Managed):**
- 8GB RAM cluster (HA): $200/month

**PostgreSQL (CloudSQL):**
- 2 vCPU, 8GB RAM, 100GB SSD: $180/month

**Object Storage (GCS):**
- 500GB transcripts: $10/month
- Egress: 100GB × $0.12 = $12/month

**CloudFlare:**
- Pro plan: $20/month

**Monitoring (Datadog):**
- $15/host × 3 = $45/month

**Total Monthly Cost: ~$1,262**
**Cost per Active User: $0.13/month**

---

**Última actualización:** 2025-11-05
**Próximo documento:** [03-extension-architecture.md](./03-extension-architecture.md)
