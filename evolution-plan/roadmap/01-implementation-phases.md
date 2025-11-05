# Fases de Implementación

**Versión:** 1.0
**Fecha:** 2025-11-05
**Timeline Total:** 14-20 semanas

---

## 🎯 Estrategia General

**Enfoque:** Evolutivo e incremental con entregables valiosos en cada fase.

**Principios:**
1. **No breaking changes** - Backward compatibility siempre
2. **User value first** - Priorizar lo que ayuda más a usuarios
3. **Learn and adapt** - Feedback loop rápido
4. **Ship early, iterate** - MVP en cada fase

---

## 📦 Fase 1: Extensión Claude Desktop (.mcpb)

**Duración:** 2-3 semanas
**Esfuerzo:** 40-60 horas
**Prioridad:** 🔴 P0 (Crítico)
**Objetivo:** Eliminar barrera de entrada con instalación one-click

### Milestones

#### Milestone 1.1: Preparación y Setup (Semana 1)
**Tareas:**

- [ ] **Instalar y configurar MCPB CLI**
  ```bash
  npm install -g @anthropic-ai/mcpb
  mcpb --version
  ```
  **Tiempo:** 0.5h

- [ ] **Crear manifest.json inicial**
  ```bash
  cd youtube-extract-mcp-server
  mcpb init
  ```
  Completar wizard interactivo con metadata del proyecto.
  **Tiempo:** 1h

- [ ] **Diseñar y crear icon.png**
  - Dimensiones: 128x128 pixels
  - Formato: PNG con transparencia
  - Estilo: Flat design, colores corporativos
  - Herramientas: Figma / Canva
  **Tiempo:** 2-3h

- [ ] **Estructura de carpetas para .mcpb**
  ```bash
  mkdir -p .mcpb-build/server
  mkdir -p .mcpb-build/scripts
  cp youtube_extract_mcp.py .mcpb-build/server/
  cp playlist_processor.py .mcpb-build/server/
  cp icon.png .mcpb-build/
  cp README.md .mcpb-build/
  ```
  **Tiempo:** 0.5h

- [ ] **Personalizar manifest.json**
  - Agregar user_config (output_directory)
  - Definir todas las herramientas con params
  - Configurar mcp_config con uv
  - Agregar metadata completa
  **Tiempo:** 3-4h

**Entregable:** Estructura base del paquete .mcpb
**Checkpoint:** Validar manifest (`mcpb validate`)

---

#### Milestone 1.2: Testing Local (Semana 2)
**Tareas:**

- [ ] **Empaquetar primera versión**
  ```bash
  cd .mcpb-build
  mcpb pack
  ```
  **Tiempo:** 0.5h

- [ ] **Testing en macOS**
  - Instalar en Claude Desktop local
  - Verificar configuración de output_directory
  - Test youtube_extract_video
  - Test youtube_extract_playlist (small)
  - Test configuración post-instalación
  **Tiempo:** 4-6h

- [ ] **Testing en Windows** (VM o máquina física)
  - Repetir tests de macOS
  - Verificar paths con backslashes
  - Verificar instalación de uv en Windows
  **Tiempo:** 4-6h

- [ ] **Testing en Linux** (opcional, baja prioridad)
  **Tiempo:** 2-3h

- [ ] **Documentar edge cases encontrados**
  - Crear bug tracker (GitHub issues)
  - Documentar workarounds temporales
  **Tiempo:** 2h

**Entregable:** youtube-extract-mcp-1.0.0-beta.mcpb testeado
**Checkpoint:** 100% funcional en macOS + Windows

---

#### Milestone 1.3: Refinamiento y Release (Semana 3)
**Tareas:**

- [ ] **Crear documentación de usuario**
  - README dentro del .mcpb
  - Screenshots de instalación
  - Guía de troubleshooting
  **Tiempo:** 4h

- [ ] **Crear CHANGELOG.md**
  - Historial de versiones
  - Breaking changes (ninguno)
  **Tiempo:** 1h

- [ ] **Release final 1.0.0**
  ```bash
  mcpb pack --production
  ```
  **Tiempo:** 0.5h

- [ ] **Publicar en GitHub Releases**
  ```bash
  gh release create v1.0.0 \
    youtube-extract-mcp-1.0.0.mcpb \
    --title "YouTube Extract MCP v1.0.0 - Claude Desktop Extension" \
    --notes-file RELEASE_NOTES.md
  ```
  **Tiempo:** 1h

- [ ] **Submit a Anthropic Extension Directory**
  - Completar submission form
  - Upload .mcpb + screenshots
  - Privacy policy + ToS
  **Tiempo:** 3-4h

- [ ] **Promoción inicial**
  - Post en foros relevantes (Reddit, Discord)
  - Tweet de lanzamiento
  - GitHub announcement
  **Tiempo:** 2h

**Entregable:** Extension publicada y disponible
**Checkpoint:** >= 10 instalaciones exitosas

---

### Métricas de Éxito Fase 1

| Métrica | Target |
|---------|--------|
| Instalaciones exitosas | >= 50 |
| Tiempo promedio instalación | < 3 minutos |
| Tasa de error instalación | < 10% |
| GitHub stars | >= 20 |
| User feedback positivo | >= 80% |

---

## 🔌 Fase 2: Transporte HTTP Local

**Duración:** 3-4 semanas
**Esfuerzo:** 80-100 horas
**Prioridad:** 🟡 P1 (Alta)
**Objetivo:** Preparar arquitectura para deployment remoto

### Milestones

#### Milestone 2.1: Arquitectura HTTP (Semana 1)
**Tareas:**

- [ ] **Refactorizar código core**
  - Separar lógica de negocio de transporte
  - Crear `src/core/extractor.py` (transport-agnostic)
  - Mover stdio a `src/transports/stdio.py`
  **Tiempo:** 8-10h

- [ ] **Implementar HTTP transport (FastAPI)**
  ```python
  # src/transports/http.py
  from fastapi import FastAPI
  from sse_starlette.sse import EventSourceResponse

  app = FastAPI()

  @app.post("/mcp/endpoint")
  async def mcp_request(request: dict):
      # Handle JSON-RPC
      pass

  @app.get("/mcp/sse")
  async def sse_stream():
      # Server-sent events
      pass
  ```
  **Tiempo:** 12-15h

- [ ] **Session management**
  - In-memory sessions (dict)
  - Session ID generation
  - TTL management
  **Tiempo:** 6-8h

- [ ] **Origin validation** (seguridad localhost)
  ```python
  @app.middleware("http")
  async def validate_origin(request, call_next):
      origin = request.headers.get("origin")
      if origin and not origin.startswith("http://localhost"):
          return Response(status_code=403)
      return await call_next(request)
  ```
  **Tiempo:** 2h

**Entregable:** Servidor HTTP funcionando localmente
**Checkpoint:** curl requests funcionan

---

#### Milestone 2.2: Integración con Cliente (Semana 2)
**Tareas:**

- [ ] **Configuración Claude Desktop para HTTP**
  ```json
  {
    "mcpServers": {
      "youtube-extract-http": {
        "transport": "http",
        "url": "http://localhost:8000/mcp/endpoint",
        "sseUrl": "http://localhost:8000/mcp/sse"
      }
    }
  }
  ```
  **Tiempo:** 1h

- [ ] **Testing con Claude Desktop**
  - Iniciar servidor HTTP en background
  - Configurar Claude Desktop
  - Test todas las herramientas
  **Tiempo:** 4-6h

- [ ] **Soporte dual transport**
  ```python
  # main.py
  if __name__ == "__main__":
      parser = argparse.ArgumentParser()
      parser.add_argument("--transport", choices=["stdio", "http"])
      args = parser.parse_args()

      if args.transport == "stdio":
          run_stdio_server()
      else:
          run_http_server()
  ```
  **Tiempo:** 3-4h

- [ ] **Actualizar manifest.json (.mcpb)**
  - Agregar opción de HTTP local
  - Documentar ambos modos
  **Tiempo:** 2h

**Entregable:** Dual transport funcionando
**Checkpoint:** stdio y HTTP ambos operacionales

---

#### Milestone 2.3: Testing y Optimización (Semana 3-4)
**Tareas:**

- [ ] **Suite de tests HTTP**
  ```python
  # tests/test_http_transport.py
  from fastapi.testclient import TestClient

  def test_mcp_request():
      client = TestClient(app)
      response = client.post("/mcp/endpoint", json={
          "jsonrpc": "2.0",
          "id": 1,
          "method": "tools/call",
          "params": {...}
      })
      assert response.status_code == 200
  ```
  **Tiempo:** 8-10h

- [ ] **Load testing**
  ```bash
  # Usar locust o k6
  k6 run load_test.js
  ```
  - Objetivo: 100 req/s sin errores
  **Tiempo:** 4-6h

- [ ] **Optimizaciones de performance**
  - Async optimization
  - Connection pooling
  - Request caching
  **Tiempo:** 8-10h

- [ ] **Documentación HTTP transport**
  - API reference
  - Deployment guide (systemd, launchd)
  - Troubleshooting guide
  **Tiempo:** 6-8h

**Entregable:** HTTP transport production-ready
**Checkpoint:** Load testing passed

---

### Métricas de Éxito Fase 2

| Métrica | Target |
|---------|--------|
| Concurrency support | >= 10 clients |
| Throughput | >= 100 req/min |
| Latency p95 | < 300ms |
| Test coverage | >= 80% |
| Zero regressions | stdio sigue funcionando 100% |

---

## ☁️ Fase 3: Deployment Remoto

**Duración:** 6-8 semanas
**Esfuerzo:** 150-200 horas
**Prioridad:** 🟢 P2 (Media)
**Objetivo:** SaaS multi-tenant en Google Cloud Run

### Milestones

#### Milestone 3.1: OAuth 2.1 Implementation (Semana 1-2)
**Tareas:**

- [ ] **Seleccionar Auth provider**
  - Evaluar: Auth0, Google Identity, Cognito
  - Decisión: Auth0 (más simple para MVP)
  **Tiempo:** 4h

- [ ] **Setup Auth0**
  - Crear tenant
  - Configurar application (MCP Server)
  - Definir scopes: youtube:extract, youtube:history
  **Tiempo:** 3-4h

- [ ] **Implementar Protected Resource Metadata**
  ```python
  @app.get("/.well-known/oauth-protected-resource")
  async def prm():
      return {
          "resource": "https://youtube-extract.example.com",
          "authorization_servers": [
              "https://youtube-extract.auth0.com"
          ]
      }
  ```
  **Tiempo:** 2h

- [ ] **Token validation middleware**
  - JWT verification con JWKS
  - Claims validation
  - Caching de signing keys
  **Tiempo:** 10-12h

- [ ] **Testing OAuth flow**
  - Authorization code + PKCE
  - Token refresh
  - Revocation
  **Tiempo:** 6-8h

**Entregable:** OAuth 2.1 funcionando
**Checkpoint:** Token validation con latencia < 50ms

---

#### Milestone 3.2: Multi-Tenant Architecture (Semana 3-4)
**Tareas:**

- [ ] **User management**
  ```sql
  CREATE TABLE users (
      id UUID PRIMARY KEY,
      email VARCHAR(255) UNIQUE,
      subscription_tier VARCHAR(50) DEFAULT 'free',
      created_at TIMESTAMP DEFAULT NOW()
  );
  ```
  **Tiempo:** 4h

- [ ] **Query-level isolation**
  - Refactorizar todas las queries para incluir user_id
  - Implementar RLS en PostgreSQL
  **Tiempo:** 12-15h

- [ ] **Rate limiting per-user**
  - Token bucket con Redis
  - Tier-based limits (free, pro, enterprise)
  **Tiempo:** 8-10h

- [ ] **Storage isolation**
  - S3/GCS paths con user_id prefix
  - Presigned URLs para acceso seguro
  **Tiempo:** 6-8h

- [ ] **Testing multi-tenant**
  - Test user A no ve datos de user B
  - Load testing con múltiples usuarios
  **Tiempo:** 8-10h

**Entregable:** Multi-tenancy completo y seguro
**Checkpoint:** Pen testing passed (no data leaks)

---

#### Milestone 3.3: Cloud Infrastructure (Semana 5-6)
**Tareas:**

- [ ] **Setup Google Cloud Project**
  ```bash
  gcloud projects create youtube-extract-mcp
  gcloud config set project youtube-extract-mcp
  ```
  **Tiempo:** 1h

- [ ] **Provisionar recursos**
  - Cloud Run service
  - CloudSQL PostgreSQL
  - Redis (Memorystore)
  - Cloud Storage bucket
  **Tiempo:** 4-6h (con Terraform)

- [ ] **Dockerfile optimization**
  ```dockerfile
  FROM python:3.11-slim
  # Multi-stage build
  # Layer caching optimization
  # Security hardening
  ```
  **Tiempo:** 4-6h

- [ ] **CI/CD pipeline (GitHub Actions)**
  - Build on push
  - Run tests
  - Deploy to Cloud Run (staging)
  - Manual approval para production
  **Tiempo:** 8-10h

- [ ] **Monitoring setup**
  - Cloud Logging
  - Cloud Monitoring dashboards
  - Alerting rules
  **Tiempo:** 6-8h

**Entregable:** Infrastructure as Code + CI/CD
**Checkpoint:** Automated deployment working

---

#### Milestone 3.4: Production Launch (Semana 7-8)
**Tareas:**

- [ ] **Security hardening**
  - Secrets in Secret Manager
  - IAM roles configurados
  - Network policies (VPC)
  - DDoS protection (CloudFlare)
  **Tiempo:** 8-10h

- [ ] **Performance optimization**
  - Database indexing
  - Redis caching strategy
  - CDN configuration
  **Tiempo:** 6-8h

- [ ] **Load testing production**
  - Simular 1,000 concurrent users
  - Verificar auto-scaling
  **Tiempo:** 4-6h

- [ ] **Documentation completa**
  - API reference (OpenAPI/Swagger)
  - User guide
  - Admin guide
  - Runbook (incident response)
  **Tiempo:** 12-15h

- [ ] **Beta launch**
  - Invitar 100 beta testers
  - Recoger feedback
  - Iterar rápido
  **Tiempo:** 2 semanas (concurrent)

- [ ] **Public launch**
  - Announcement
  - Marketing push
  - Support channels setup
  **Tiempo:** 4h

**Entregable:** Production system live
**Checkpoint:** 99.9% uptime first month

---

### Métricas de Éxito Fase 3

| Métrica | Target |
|---------|--------|
| Uptime | >= 99.9% |
| Latency p95 | < 500ms |
| Concurrent users | >= 100 |
| OAuth token validation | < 50ms |
| Zero security incidents | ✅ |
| User satisfaction (NPS) | >= 40 |

---

## 🚀 Fase 4: Optimización y Escala (Futuro)

**Duración:** Continua
**Prioridad:** 🔵 P3 (Baja inicialmente)

### Áreas de Mejora

**Performance:**
- [ ] Caching aggressive de transcripciones
- [ ] CDN para assets estáticos
- [ ] Database read replicas
- [ ] Background job processing (playlists grandes)

**Features:**
- [ ] Resources API (historial, stats)
- [ ] Prompts API (templates)
- [ ] Webhooks (notifications)
- [ ] Bulk operations API

**Observabilidad:**
- [ ] Distributed tracing (OpenTelemetry)
- [ ] Custom Datadog dashboards
- [ ] User analytics
- [ ] Cost monitoring

**Compliance:**
- [ ] SOC 2 Type II audit
- [ ] GDPR automation (data export, deletion)
- [ ] HIPAA compliance (si requerido)

---

## 📅 Timeline Visual

```
Mes 1          Mes 2          Mes 3          Mes 4          Mes 5-6
│              │              │              │              │
├─ Fase 1 ─────┤              │              │              │
│  .mcpb       │              │              │              │
│  Extension   │              │              │              │
│              │              │              │              │
│      ├───────┴─ Fase 2 ─────┤              │              │
│      │         HTTP Local    │              │              │
│      │                       │              │              │
│      │               ├───────┴───── Fase 3 ────────────────┤
│      │               │       Deployment Remoto             │
│      │               │                                     │
│      │               │                  ├──────────────────┴─────>
│      │               │                  │ Fase 4: Optimización
│      │               │                  │ (Continua)
│      │               │                  │
▼      ▼               ▼                  ▼
v1.0   v1.1            v2.0               v2.1+
(stdio) (+HTTP)        (OAuth + Cloud)    (Scale)
```

---

## 👥 Recursos Necesarios

### Fase 1: .mcpb Extension
**Equipo:** 1 developer
**Skills:** Python, MCP, packaging
**Tiempo:** Part-time (50%)

### Fase 2: HTTP Transport
**Equipo:** 1 developer
**Skills:** Python, FastAPI, HTTP/SSE
**Tiempo:** Full-time

### Fase 3: Remote Deployment
**Equipo:** 1-2 developers + 0.5 DevOps
**Skills:** Python, FastAPI, OAuth, GCP, K8s/Cloud Run, PostgreSQL, Redis
**Tiempo:** Full-time

### Fase 4: Optimización
**Equipo:** Variable (según prioridades)

---

## 💰 Estimación de Costos

### Desarrollo (One-time)

| Fase | Horas | Costo/hora | Total |
|------|-------|------------|-------|
| Fase 1 | 60h | $75 | $4,500 |
| Fase 2 | 100h | $75 | $7,500 |
| Fase 3 | 200h | $85 | $17,000 |
| **Total** | **360h** | | **$29,000** |

### Operacional (Mensual)

| Ítem | Costo (0-100 users) | Costo (1K users) | Costo (10K users) |
|------|---------------------|------------------|-------------------|
| Cloud Run | $0 | $50 | $770 |
| PostgreSQL | $0 (free tier) | $25 | $180 |
| Redis | $0 (free tier) | $15 | $200 |
| Storage | $0 | $5 | $20 |
| Auth0 | $0 | $0 | $35 |
| Monitoring | $0 | $0 | $45 |
| **Total** | **$0** | **$95** | **$1,250** |

---

**Última actualización:** 2025-11-05
**Próximo documento:** [02-priorities.md](./02-priorities.md)
