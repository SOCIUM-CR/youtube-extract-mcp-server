# Opciones de Hosting y Deployment

**Versión:** 1.0
**Fecha:** 2025-11-05
**Target:** Fase 3 del Roadmap

---

## 🎯 Criterios de Evaluación

| Criterio | Peso | Descripción |
|----------|------|-------------|
| **Auto-scaling** | 🔴 Alto | Capacidad de escalar horizontal automáticamente |
| **Cold start latency** | 🟡 Medio | Tiempo de inicio de instancia fría |
| **Costo operativo** | 🔴 Alto | Costo mensual estimado para carga típica |
| **Complejidad setup** | 🟡 Medio | Dificultad de configuración inicial |
| **Observabilidad** | 🟡 Medio | Logging, metrics, tracing integrados |
| **Vendor lock-in** | 🟢 Bajo | Facilidad de migración a otra plataforma |

---

## 🏢 Opción 1: Google Cloud Run

### Descripción

**Serverless container platform** que ejecuta contenedores HTTP en auto-scaling completo.

### Arquitectura

```
┌───────────────────────────────────────────────┐
│  Google Cloud Run                             │
│                                               │
│  ┌─────────────────────────────────────────┐ │
│  │  Service: youtube-extract-mcp           │ │
│  │                                         │ │
│  │  Revision: youtube-extract-mcp-v1      │ │
│  │  ├─ Container: gcr.io/project/mcp:v1   │ │
│  │  ├─ CPU: 1 vCPU                        │ │
│  │  ├─ Memory: 512 MB                     │ │
│  │  ├─ Concurrency: 80 requests/instance │ │
│  │  └─ Min instances: 1                   │ │
│  │     Max instances: 100                 │ │
│  └─────────────────────────────────────────┘ │
│                                               │
│  Auto-scaling based on:                      │
│  • Request load                              │
│  • CPU utilization                           │
│  • Memory utilization                        │
└───────────────────────────────────────────────┘
```

### Pros

- ✅ **Zero ops** - No gestión de servidores
- ✅ **Pay-per-use** - Solo pagas por tiempo de ejecución
- ✅ **Auto-scaling** - De 0 a N instancias automático
- ✅ **Built-in HTTPS** - SSL/TLS automático
- ✅ **Cloud IAM** - Integración con OAuth/OIDC
- ✅ **Cold start < 1s** - Para containers optimizados
- ✅ **Logging integrado** - Cloud Logging automático

### Cons

- ⚠️ **Request timeout** - Max 60 min (suficiente para nuestro caso)
- ⚠️ **Stateless** - Requiere Redis para sesiones
- ⚠️ **Vendor lock-in** - Específico de GCP

### Configuración

```yaml
# cloud-run.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: youtube-extract-mcp
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "100"
        autoscaling.knative.dev/target: "70"
    spec:
      containers:
      - image: gcr.io/project-id/youtube-extract-mcp:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: mcp-secrets
              key: redis_url
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: mcp-secrets
              key: database_url
        resources:
          limits:
            cpu: "1000m"
            memory: "512Mi"
```

### Deployment

```bash
# Build container
docker build -t gcr.io/project-id/youtube-extract-mcp:latest .
docker push gcr.io/project-id/youtube-extract-mcp:latest

# Deploy to Cloud Run
gcloud run deploy youtube-extract-mcp \
  --image gcr.io/project-id/youtube-extract-mcp:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \  # O --no-allow-unauthenticated para OAuth
  --min-instances 1 \
  --max-instances 100 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300s
```

### Costos Estimados

**Escenario: 10,000 usuarios, 20 req/día cada uno**

```
Requests: 10,000 × 20 × 30 = 6M req/month
Avg duration: 5s
vCPU-seconds: 6M × 5 = 30M
GB-seconds: 6M × 0.5 × 5 = 15M

Costs:
- vCPU: 30M × $0.000024 = $720
- Memory: 15M × $0.0000025 = $37.50
- Requests: 6M × $0.0000004 = $2.40
- Networking: $10 (egress)

Total: ~$770/month
Cost per user: $0.077/month
```

### Recomendación: ⭐⭐⭐⭐⭐ (Excelente para nuestro caso)

---

## 🏢 Opción 2: AWS Lambda + API Gateway

### Descripción

**Serverless functions** con API Gateway como front-end HTTP.

### Arquitectura

```
┌───────────────────────────────────────────────┐
│  AWS API Gateway                              │
│  ├─ POST /mcp/endpoint → Lambda               │
│  └─ GET  /mcp/sse      → Lambda (streaming)   │
└─────────────────┬─────────────────────────────┘
                  │
┌─────────────────▼─────────────────────────────┐
│  AWS Lambda                                   │
│  ┌─────────────────────────────────────────┐ │
│  │  Function: youtube-extract-mcp          │ │
│  │  Runtime: Python 3.11                   │ │
│  │  Memory: 512 MB                         │ │
│  │  Timeout: 300s                          │ │
│  │  Reserved concurrency: 100              │ │
│  └─────────────────────────────────────────┘ │
└───────────────────────────────────────────────┘
```

### Pros

- ✅ **Serverless** - Zero gestión de infraestructura
- ✅ **Pay-per-invocation** - Solo pagas por ejecución
- ✅ **Integración AWS** - IAM, Cognito, etc.
- ✅ **Free tier generoso** - 1M requests/mes gratis
- ✅ **VPC integration** - Acceso a recursos privados

### Cons

- ❌ **Cold start alto** - 1-3 segundos para Python
- ❌ **Package size limit** - 250MB (puede ser limitante con deps)
- ❌ **SSE limitado** - Requiere workarounds
- ⚠️ **Complejidad** - Más piezas móviles (API Gateway, Lambda, IAM)

### Deployment

```yaml
# serverless.yml (Serverless Framework)
service: youtube-extract-mcp

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  memorySize: 512
  timeout: 300
  environment:
    REDIS_URL: ${ssm:/mcp/redis/url}
    DATABASE_URL: ${ssm:/mcp/database/url}

functions:
  mcpRequest:
    handler: src/handlers.mcp_request
    events:
      - http:
          path: mcp/endpoint
          method: post
          cors: true
          authorizer:
            type: aws_iam

  mcpSSE:
    handler: src/handlers.mcp_sse
    events:
      - http:
          path: mcp/sse
          method: get
          cors: true
```

```bash
# Deploy
serverless deploy --stage production
```

### Costos Estimados

```
Requests: 6M/month
Avg duration: 5s
Memory: 512MB

Costs:
- Lambda invocations: (6M - 1M free) × $0.20/1M = $1.00
- Lambda compute: 5M × 5s × 512MB × $0.0000166667 = $208
- API Gateway: 6M × $1.00/1M = $6.00

Total: ~$215/month
Cost per user: $0.022/month
```

### Recomendación: ⭐⭐⭐⚪⚪ (Bueno pero cold start problemático)

---

## 🏢 Opción 3: Cloudflare Workers + Durable Objects

### Descripción

**Edge computing** con ejecución en red global de Cloudflare.

### Arquitectura

```
┌───────────────────────────────────────────────┐
│  Cloudflare Workers (Edge)                    │
│  Deployed to 200+ locations globally          │
│                                               │
│  ┌─────────────────────────────────────────┐ │
│  │  Worker: youtube-extract-mcp            │ │
│  │  Runtime: JavaScript/Python (soon)      │ │
│  │  CPU: 50ms per request (paid)           │ │
│  │  Memory: 128MB                          │ │
│  └─────────────────────────────────────────┘ │
└─────────────────┬─────────────────────────────┘
                  │
┌─────────────────▼─────────────────────────────┐
│  Durable Objects                              │
│  (Stateful coordination)                      │
│                                               │
│  • Session management                         │
│  • SSE connection persistence                 │
│  • Rate limiting state                        │
└───────────────────────────────────────────────┘
```

### Pros

- ✅ **Zero cold start** - Instante
- ✅ **Global edge** - Latencia mínima worldwide
- ✅ **Built-in OAuth** - Soporte nativo
- ✅ **Durable Objects** - Estado persistente para SSE
- ✅ **Costos bajos** - $5/mes plan paid

### Cons

- ❌ **CPU limit** - 50ms per request (paid), restrictivo para yt-dlp
- ❌ **Runtime limitado** - No Python nativo (aún)
- ❌ **Complejidad** - Modelo de programación diferente
- ⚠️ **No ideal para long-running** - Nuestras extracciones toman 3-8s

### Recomendación: ⭐⭐⚪⚪⚪ (No ideal para nuestro workload)

---

## 🏢 Opción 4: Kubernetes (GKE / EKS / AKS)

### Descripción

**Container orchestration** con control total de infraestructura.

### Arquitectura

```
┌───────────────────────────────────────────────┐
│  Kubernetes Cluster                           │
│                                               │
│  ┌─────────────────────────────────────────┐ │
│  │  Ingress Controller (Nginx)             │ │
│  │  ├─ TLS termination                     │ │
│  │  └─ Load balancing                      │ │
│  └──────────────┬──────────────────────────┘ │
│                 │                             │
│  ┌──────────────▼──────────────────────────┐ │
│  │  Service: youtube-extract-mcp           │ │
│  │  Type: ClusterIP                        │ │
│  └──────────────┬──────────────────────────┘ │
│                 │                             │
│  ┌──────────────▼──────────────────────────┐ │
│  │  Deployment: youtube-extract-mcp        │ │
│  │  ├─ Replicas: 3 (min)                   │ │
│  │  ├─ HPA: up to 50 replicas              │ │
│  │  └─ Rolling updates                     │ │
│  └─────────────────────────────────────────┘ │
│                                               │
│  ┌─────────────────────────────────────────┐ │
│  │  Supporting Services                    │ │
│  │  ├─ Redis (StatefulSet)                 │ │
│  │  ├─ PostgreSQL (External CloudSQL)      │ │
│  │  └─ Prometheus (Monitoring)             │ │
│  └─────────────────────────────────────────┘ │
└───────────────────────────────────────────────┘
```

### Pros

- ✅ **Control total** - Máxima flexibilidad
- ✅ **Portable** - Funciona en cualquier cloud
- ✅ **Ecosistema rico** - Helm charts, operators
- ✅ **Observabilidad** - Prometheus, Grafana nativos
- ✅ **No cold start** - Instancias siempre calientes

### Cons

- ❌ **Complejidad alta** - Requiere expertise K8s
- ❌ **Overhead operacional** - Cluster management
- ❌ **Costo mínimo alto** - ~$200/mes solo cluster
- ❌ **Over-engineering** - Para nuestro caso

### Costos Estimados

```
GKE Autopilot (managed):
- 3 nodes (e2-standard-2): $150/month
- Load balancer: $18/month
- Persistent disks: $20/month
- CloudSQL: $180/month
- Redis (Memorystore): $150/month

Total: ~$518/month (sin tráfico)
```

### Recomendación: ⭐⭐⚪⚪⚪ (Overkill para nuestro tamaño)

---

## 🏢 Opción 5: Heroku (PaaS)

### Descripción

**Platform as a Service** tradicional con deployment simplificado.

### Pros

- ✅ **Simplicidad máxima** - Git push to deploy
- ✅ **Add-ons** - Redis, PostgreSQL integrados
- ✅ **Free tier** - Para prototyping

### Cons

- ❌ **Costo alto escala** - $25-50/dyno
- ❌ **Sleep dyno** - Free tier duerme (cold start)
- ⚠️ **Menos control** - Opciones limitadas

### Costos Estimados

```
- Standard dyno (1x): $25/month
- Redis mini: $15/month
- PostgreSQL mini: $9/month

Total: ~$49/month (1 dyno, limitado)

Para producción (3 dynos): $150/month
```

### Recomendación: ⭐⭐⭐⚪⚪ (Bueno para MVP, caro para escala)

---

## 📊 Comparación Final

| Plataforma | Auto-scale | Cold Start | Costo (10K users) | Complejidad | Score |
|------------|------------|------------|-------------------|-------------|-------|
| **Cloud Run** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **$770/mes** | ⭐⭐⭐⭐ | **23/25** |
| Lambda | ⭐⭐⭐⭐⭐ | ⭐⭐⚪⚪⚪ | $215/mes | ⭐⭐⭐⚪ | 17/25 |
| CF Workers | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | N/A (no viable) | ⭐⭐⚪⚪ | 12/25 |
| Kubernetes | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | $1,200/mes | ⭐⚪⚪⚪ | 14/25 |
| Heroku | ⭐⭐⭐⚪⚪ | ⭐⭐⭐⚪⚪ | $150/mes (limitado) | ⭐⭐⭐⭐⭐ | 16/25 |

---

## 🎯 Recomendación Final

### **Google Cloud Run** (Ganador)

**Justificación:**

1. **Best fit técnico:**
   - Container-based (fácil migración futura)
   - Auto-scaling perfecto para carga variable
   - Cold start < 1s (aceptable)
   - Timeout 60min (más que suficiente)

2. **Costo-beneficio:**
   - Pay-per-use real
   - $770/mes para 10,000 usuarios
   - Escala linealmente

3. **Developer experience:**
   - Simple deployment (`gcloud run deploy`)
   - Logging/monitoring integrado
   - CI/CD fácil (Cloud Build)

4. **Preparación futura:**
   - Si crece mucho → migrar a GKE
   - Mismo Docker container

### Estrategia de Implementación

**Fase 1: MVP (Mes 1-2)**
- Deploy a Cloud Run
- 1 región (us-central1)
- Min instances: 0 (máximo savings)
- PostgreSQL pequeño

**Fase 2: Optimización (Mes 3-4)**
- Multi-región (us, europe, asia)
- Min instances: 1 (reduce latencia)
- Redis caching
- CDN para assets

**Fase 3: Escala (Mes 6+)**
- Considerar GKE si > 50K usuarios
- O mantener Cloud Run (puede escalar a millones)

---

## 🔧 Setup Inicial Recomendado

```bash
# 1. Crear proyecto GCP
gcloud projects create youtube-extract-mcp

# 2. Habilitar APIs
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable redis.googleapis.com

# 3. Crear Redis instance
gcloud redis instances create mcp-redis \
  --size=1 \
  --region=us-central1 \
  --tier=basic

# 4. Crear CloudSQL PostgreSQL
gcloud sql instances create mcp-postgres \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# 5. Deploy app
gcloud run deploy youtube-extract-mcp \
  --image gcr.io/PROJECT/youtube-extract-mcp:latest \
  --region us-central1 \
  --platform managed

# 6. Setup CI/CD (Cloud Build)
gcloud builds submit --config cloudbuild.yaml
```

---

**Última actualización:** 2025-11-05
**Próximo documento:** [02-security-requirements.md](./02-security-requirements.md)
