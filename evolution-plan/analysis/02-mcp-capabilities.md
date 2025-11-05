# Capacidades del Protocolo MCP

**Versión del Protocolo:** 2025-03-26
**Fecha de Análisis:** 2025-11-05

---

## 📖 ¿Qué es MCP?

El **Model Context Protocol (MCP)** es un protocolo abierto creado por Anthropic en 2024 para permitir integración bidireccional entre aplicaciones LLM y fuentes de datos/herramientas externas.

### Principios Fundamentales

1. **Estandarización**: Protocolo único para múltiples integraciones
2. **Bidireccionalidad**: Comunicación cliente ↔ servidor
3. **Extensibilidad**: Fácil agregar nuevas capacidades
4. **Seguridad**: Autenticación y autorización integradas

---

## 🔧 Primitivas del Protocolo

MCP define tres primitivas principales:

### 1. **Tools** (Herramientas)

Funciones que el servidor expone al cliente (LLM) para ejecutar acciones.

**Ejemplo actual en nuestro servidor:**
```python
youtube_extract_video(
    url: str,
    language: str = "auto",
    include_timestamps: bool = True,
    format: str = "text",
    save_locally: bool = False
)
```

**Características:**
- Firma de función clara con tipos
- Descripción legible para el LLM
- Validación de parámetros
- Respuesta estructurada (JSON-RPC)

### 2. **Resources** (Recursos)

Datos que el servidor puede proveer al cliente de forma estática o dinámica.

**Uso potencial en nuestro servidor:**
- Lista de transcripciones guardadas localmente
- Historial de videos procesados
- Estadísticas de uso
- Configuración actual

**No implementado actualmente** ⚠️

### 3. **Prompts** (Plantillas)

Plantillas reutilizables para interacciones comunes.

**Uso potencial:**
- "Extrae y resume esta playlist"
- "Compara transcripciones de dos videos"
- "Genera índice temático de playlist"

**No implementado actualmente** ⚠️

---

## 🚀 Métodos de Transporte

### Comparación Detallada

| Aspecto | stdio | HTTP+SSE (Deprecated) | Streamable HTTP (Current) |
|---------|-------|----------------------|---------------------------|
| **Status** | ✅ Recomendado local | ⚠️ Deprecado | ✅ Standard 2025 |
| **Versión desde** | Todas | 2024-11-05 | 2025-03-26 |
| **Lifecycle** | Subprocess | Proceso independiente | Proceso independiente |
| **Concurrencia** | 1 cliente | Múltiples | Múltiples |
| **Streaming** | stdin/stdout | SSE separado | SSE integrado en HTTP |
| **Complejidad** | 🟢 Baja | 🟡 Media | 🟡 Media |
| **Uso típico** | Desktop local | Web services | Web services modernos |

### stdio Transport (Actual)

**Especificación Técnica:**

```
┌─────────────────────────────────────────────┐
│ Cliente (Claude Desktop)                    │
│                                             │
│ 1. Spawn: subprocess.Popen()               │
│ 2. Write: stdin (newline-delimited JSON)   │
│ 3. Read: stdout (newline-delimited JSON)   │
│ 4. Logs: stderr (UTF-8 text)               │
│ 5. Exit: wait for process termination      │
└─────────────────────────────────────────────┘
```

**Requisitos MCP:**
- Mensajes JSON-RPC delimitados por `\n`
- **MUST NOT** contener newlines embebidos
- stdout solo para mensajes MCP válidos
- stderr para logging (opcional, ignorable)

**Ventajas:**
- ✅ Simplicidad máxima
- ✅ No requiere networking
- ✅ Fácil debugging (stdin/stdout visible)
- ✅ Gestión automática de lifecycle

**Desventajas:**
- ❌ Solo 1 cliente por proceso
- ❌ No compartible entre máquinas
- ❌ No escalable horizontalmente

### Streamable HTTP Transport (Target)

**Especificación Técnica:**

```
┌──────────────────────────────────────────────────┐
│ Cliente (Claude / Otros)                         │
│                                                  │
│ ┌─────────────────────┐   ┌──────────────────┐ │
│ │ Client→Server       │   │ Server→Client    │ │
│ │                     │   │                  │ │
│ │ HTTP POST           │   │ HTTP GET (SSE)   │ │
│ │ /mcp/endpoint       │   │ /mcp/sse         │ │
│ │                     │   │                  │ │
│ │ Headers:            │   │ Headers:         │ │
│ │ - Accept: json+sse  │   │ - Mcp-Session-Id │ │
│ │ - Mcp-Session-Id    │   │                  │ │
│ │                     │   │                  │ │
│ │ Body: JSON-RPC      │   │ Body: SSE stream │ │
│ └─────────────────────┘   └──────────────────┘ │
└──────────────────────────────────────────────────┘
           │                          │
           ▼                          ▼
┌──────────────────────────────────────────────────┐
│ Servidor MCP (Remoto)                            │
│                                                  │
│ • Manejo de sesiones (Mcp-Session-Id)           │
│ • Validación de Origin (anti-rebinding)          │
│ • Respuesta JSON o SSE stream                   │
│ • Múltiples conexiones concurrentes             │
└──────────────────────────────────────────────────┘
```

**Cliente → Servidor (HTTP POST):**
```http
POST /mcp/endpoint HTTP/1.1
Host: youtube-extract.example.com
Content-Type: application/json
Accept: application/json, text/event-stream
Mcp-Session-Id: abc123xyz
Authorization: Bearer <oauth-token>

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "youtube_extract_video",
    "arguments": {
      "url": "https://youtube.com/watch?v=..."
    }
  }
}
```

**Servidor → Cliente (Respuesta):**

Opción A: JSON simple
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 1,
  "result": { ... }
}
```

Opción B: SSE Stream (para progreso)
```http
HTTP/1.1 200 OK
Content-Type: text/event-stream

data: {"jsonrpc":"2.0","method":"notifications/progress","params":{"progress":25}}

data: {"jsonrpc":"2.0","method":"notifications/progress","params":{"progress":50}}

data: {"jsonrpc":"2.0","id":1,"result":{ ... }}
```

**Servidor → Cliente (Server-initiated, HTTP GET):**
```http
GET /mcp/sse HTTP/1.1
Host: youtube-extract.example.com
Mcp-Session-Id: abc123xyz
Authorization: Bearer <oauth-token>

---
HTTP/1.1 200 OK
Content-Type: text/event-stream

data: {"jsonrpc":"2.0","method":"notifications/tools/list_changed"}

data: {"jsonrpc":"2.0","method":"notifications/resources/updated"}
```

**Requisitos de Seguridad:**
- ✅ Validación de `Origin` header (anti DNS rebinding)
- ✅ Binding a localhost para deployments locales
- ✅ HTTPS obligatorio para deployments remotos
- ✅ OAuth 2.1 para autenticación remota

**Ventajas:**
- ✅ Múltiples clientes concurrentes
- ✅ Servidor puede ser remoto
- ✅ Escalabilidad horizontal
- ✅ Compatible con load balancers
- ✅ Streaming de progreso nativo

**Desventajas:**
- ❌ Mayor complejidad implementación
- ❌ Requiere gestión de sesiones
- ❌ Networking puede fallar

---

## 🔐 Autenticación y Autorización

### OAuth 2.1 (Spec MCP 2025-03-26)

**Flujo de Autorización:**

```
┌────────────┐                                  ┌──────────────┐
│  Cliente   │                                  │ Auth Server  │
│   (MCP)    │                                  │  (OAuth 2.1) │
└──────┬─────┘                                  └──────┬───────┘
       │                                                │
       │ 1. Discovery: GET /.well-known/oauth-         │
       │    protected-resource                         │
       │─────────────────────────────────────────────> │
       │                                                │
       │ 2. Metadata Response:                         │
       │    {authorization_endpoint, token_endpoint}   │
       │ <──────────────────────────────────────────── │
       │                                                │
       │ 3. Dynamic Client Registration (optional)     │
       │─────────────────────────────────────────────> │
       │                                                │
       │ 4. Authorization Code + PKCE                  │
       │─────────────────────────────────────────────> │
       │                                                │
       │ 5. Access Token + Refresh Token               │
       │ <──────────────────────────────────────────── │
       │                                                │
┌──────▼─────┐                                  ┌──────────────┐
│  Cliente   │                                  │ MCP Server   │
│   (MCP)    │                                  │   (Remoto)   │
└──────┬─────┘                                  └──────┬───────┘
       │                                                │
       │ 6. MCP Request + Bearer Token                 │
       │─────────────────────────────────────────────> │
       │                                                │
       │    Authorization: Bearer <access-token>       │
       │                                                │
       │ 7. Token Validation + Response                │
       │ <──────────────────────────────────────────── │
       │                                                │
```

**Componentes Necesarios:**

1. **Protected Resource Metadata (PRM)**
   - Endpoint: `/.well-known/oauth-protected-resource`
   - Especifica authorization server
   - Declara scopes requeridos

2. **Token Validation Middleware**
   - Verifica firma JWT contra JWKS
   - Valida claims (exp, aud, iss)
   - Extrae identidad de usuario

3. **Resource Indicators**
   - Previene reutilización de tokens
   - Especifica recursos autorizados
   - Mejora seguridad multi-tenant

**Implementación Recomendada:**

```python
# Pseudocódigo de middleware OAuth
async def validate_oauth_token(request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise Unauthorized()

    token = auth_header[7:]

    # Validar JWT
    claims = await jwt.verify(
        token,
        jwks_endpoint="https://auth.example.com/.well-known/jwks.json"
    )

    # Validar claims
    if claims["exp"] < now():
        raise TokenExpired()
    if claims["aud"] != "youtube-extract-mcp":
        raise InvalidAudience()

    # Extraer usuario
    user_id = claims["sub"]
    return user_id
```

---

## 🌐 Lifecycle y Capacidades

### Handshake de Inicialización

```
Cliente                                   Servidor
  │                                          │
  │  1. initialize (protocol_version)        │
  │ ──────────────────────────────────────>  │
  │                                          │
  │  2. Capabilities negotiation             │
  │     - tools: true/false                  │
  │     - resources: true/false              │
  │     - prompts: true/false                │
  │     - logging: true/false                │
  │ <──────────────────────────────────────  │
  │                                          │
  │  3. initialized notification             │
  │ ──────────────────────────────────────>  │
  │                                          │
  │  4. Ready for operations                 │
  │                                          │
```

**Capabilities Actuales (YouTube Extract):**
- ✅ `tools: true` - 4 herramientas
- ❌ `resources: false` - No implementado
- ❌ `prompts: false` - No implementado
- ✅ `logging: true` - stderr logs

**Capabilities Target (Evolución):**
- ✅ `tools: true` - 6+ herramientas (agregar cache, stats)
- ✅ `resources: true` - Transcripciones, historial
- ✅ `prompts: true` - Plantillas de uso común
- ✅ `logging: true` - Structured logs
- ✅ `sampling: false` - No aplica (no LLM en servidor)

### Notificaciones del Servidor

El servidor puede enviar notificaciones al cliente:

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/progress",
  "params": {
    "progress": 50,
    "total": 100,
    "message": "Extracting transcription..."
  }
}
```

**Tipos de Notificaciones:**
- `notifications/progress` - Progreso de operación larga
- `notifications/tools/list_changed` - Herramientas modificadas
- `notifications/resources/list_changed` - Recursos actualizados
- `notifications/resources/updated` - Recurso específico cambió

**Uso en YouTube Extract:**
- ✅ Progreso de playlist (50 videos → notificar cada 10%)
- ✅ Cache invalidation (transcripción actualizada)
- ✅ Cambios en configuración

---

## 📊 Comparación con Otros Protocolos

| Característica | MCP | LSP | DAP | REST API |
|----------------|-----|-----|-----|----------|
| **Propósito** | LLM ↔ Tools | Editor ↔ Language | Debugger ↔ Runtime | General Web |
| **Bidireccional** | ✅ Sí | ✅ Sí | ✅ Sí | ⚠️ Limitado |
| **Streaming** | ✅ SSE | ✅ Custom | ✅ Custom | ⚠️ Chunked |
| **Stateful** | ✅ Sesiones | ✅ Workspace | ✅ Debug session | ❌ Stateless |
| **Notificaciones** | ✅ Server-push | ✅ Server-push | ✅ Events | ❌ Polling |
| **Estandarización** | 🟡 Emergente | ✅ Maduro | ✅ Maduro | ✅ Universal |

**Ventaja de MCP:** Diseñado específicamente para casos de uso de IA

---

## 🎯 Capacidades No Utilizadas (Oportunidades)

### 1. Resources API

**Descripción:** Exponer datos estructurados al LLM

**Implementación Potencial:**
```python
@server.list_resources()
async def list_resources():
    return [
        types.Resource(
            uri="youtube://transcripts/recent",
            name="Recent Transcriptions",
            mimeType="application/json"
        ),
        types.Resource(
            uri="youtube://stats/usage",
            name="Usage Statistics",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def read_resource(uri: str):
    if uri == "youtube://transcripts/recent":
        # Return last 10 transcriptions
        return recent_transcriptions()
```

**Beneficios:**
- Claude puede descubrir automáticamente datos disponibles
- Mejor contexto para conversaciones
- Facilita análisis de historial

### 2. Prompts API

**Descripción:** Plantillas reutilizables

**Implementación Potencial:**
```python
@server.list_prompts()
async def list_prompts():
    return [
        types.Prompt(
            name="summarize_playlist",
            description="Summarize all videos in a playlist",
            arguments=[
                types.PromptArgument(
                    name="playlist_url",
                    description="YouTube playlist URL",
                    required=True
                )
            ]
        )
    ]
```

**Beneficios:**
- UX mejorada (prompts pre-diseñados)
- Mejores prácticas embebidas
- Onboarding más rápido

### 3. Sampling API

**Descripción:** Servidor puede llamar al LLM para sub-tareas

**No aplicable a YouTube Extract** (no necesitamos LLM en servidor)

---

## 💡 Recomendaciones para Evolución

### Fase 1: Maximizar stdio (Actual)
✅ **Completado** - Servidor funcionando perfectamente

### Fase 2: Agregar HTTP Transport
**Prioridad:** 🔴 Alta
**Esfuerzo:** 3-4 semanas
**Impacto:** 🚀 Game changer

**Pasos:**
1. Implementar Streamable HTTP server (FastAPI/Flask)
2. Mantener backward compatibility con stdio
3. Agregar session management
4. Testing local (localhost:8000)

### Fase 3: Implementar OAuth 2.1
**Prioridad:** 🟡 Media
**Esfuerzo:** 2-3 semanas
**Impacto:** 🔒 Seguridad remota

**Pasos:**
1. Seleccionar Auth provider (Auth0, Cognito, Keycloak)
2. Implementar PRM endpoint
3. Token validation middleware
4. Multi-tenant data isolation

### Fase 4: Extender Capabilities
**Prioridad:** 🟢 Baja
**Esfuerzo:** 2-3 semanas
**Impacto:** ✨ Enhanced UX

**Pasos:**
1. Implementar Resources API (historial, stats)
2. Implementar Prompts API (templates comunes)
3. Notificaciones de progreso (playlists)

---

## 📚 Referencias Técnicas

- [MCP Specification 2025-03-26](https://spec.modelcontextprotocol.io/specification/2025-03-26/)
- [Transport Specification](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports)
- [OAuth 2.1 (RFC 9110)](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1)
- [JSON-RPC 2.0](https://www.jsonrpc.org/specification)

---

**Última actualización:** 2025-11-05
**Próximo documento:** [../architecture/01-transport-options.md](../architecture/01-transport-options.md)
