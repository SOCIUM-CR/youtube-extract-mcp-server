# Requisitos de Seguridad y Compliance

**Versión:** 1.0
**Fecha:** 2025-11-05
**Target:** Todas las fases (con diferentes niveles)

---

## 🎯 Niveles de Seguridad por Fase

### Fase 1: Local (.mcpb) - Seguridad Básica
- Sandboxing de Claude Desktop
- Validación de inputs
- Sanitización de filesystem

### Fase 2: HTTP Local - Seguridad Media
- Origin validation
- localhost-only binding
- Session management

### Fase 3: Remoto - Seguridad Enterprise
- OAuth 2.1 authentication
- Multi-tenant isolation
- Encryption en tránsito y reposo
- Rate limiting + DDoS protection
- Audit logging
- Compliance (GDPR, SOC 2)

---

## 🔐 Autenticación y Autorización (Fase 3)

### OAuth 2.1 Implementation

#### Flujo de Autorización Completo

```
┌─────────────┐                                           ┌──────────────┐
│   Cliente   │                                           │ Auth Server  │
│ (MCP Client)│                                           │  (Auth0/     │
│             │                                           │   Cognito)   │
└──────┬──────┘                                           └──────┬───────┘
       │                                                          │
       │ 1. Discovery: GET /.well-known/oauth-protected-resource │
       │────────────────────────────────────────────────────────>│
       │                                                          │
       │ 2. Metadata Response:                                   │
       │    {                                                     │
       │      "authorization_endpoint": "https://auth.../oauth", │
       │      "token_endpoint": "https://auth.../token",         │
       │      "jwks_uri": "https://auth....well-known/jwks.json" │
       │    }                                                     │
       │<────────────────────────────────────────────────────────│
       │                                                          │
       │ 3. Authorization Request + PKCE                         │
       │    GET /oauth/authorize?                                │
       │      response_type=code&                                │
       │      client_id=youtube-extract-mcp&                     │
       │      redirect_uri=https://app.../callback&              │
       │      scope=youtube:extract youtube:history&             │
       │      code_challenge=HASH(verifier)&                     │
       │      code_challenge_method=S256                         │
       │────────────────────────────────────────────────────────>│
       │                                                          │
       │ 4. User Authentication + Consent                        │
       │<────────────────────────────────────────────────────────│
       │                                                          │
       │ 5. Authorization Code                                   │
       │    Redirect: https://app.../callback?code=ABC123        │
       │<────────────────────────────────────────────────────────│
       │                                                          │
       │ 6. Token Request                                        │
       │    POST /oauth/token                                    │
       │    {                                                    │
       │      "grant_type": "authorization_code",                │
       │      "code": "ABC123",                                  │
       │      "code_verifier": "original_verifier",              │
       │      "redirect_uri": "https://app.../callback"          │
       │    }                                                    │
       │────────────────────────────────────────────────────────>│
       │                                                          │
       │ 7. Access Token + Refresh Token                         │
       │    {                                                    │
       │      "access_token": "eyJhbGci...",                     │
       │      "refresh_token": "refresh123",                     │
       │      "expires_in": 3600,                                │
       │      "token_type": "Bearer"                             │
       │    }                                                    │
       │<────────────────────────────────────────────────────────│
       │                                                          │
┌──────▼──────┐                                           ┌──────────────┐
│   Cliente   │                                           │  MCP Server  │
│             │                                           │   (Remoto)   │
└──────┬──────┘                                           └──────┬───────┘
       │                                                          │
       │ 8. MCP Request + Bearer Token                           │
       │    POST /mcp/endpoint                                   │
       │    Authorization: Bearer eyJhbGci...                    │
       │────────────────────────────────────────────────────────>│
       │                                                          │
       │ 9. Token Validation                                     │
       │    ├─ Verify JWT signature (JWKS)                       │
       │    ├─ Validate exp, aud, iss                            │
       │    └─ Extract user_id from sub claim                    │
       │                                                          │
       │ 10. Authorized Response                                 │
       │<────────────────────────────────────────────────────────│
       │                                                          │
```

#### PKCE (Proof Key for Code Exchange)

**¿Por qué PKCE?**
Protege contra interception attacks en el flujo de authorization code.

**Implementación:**

```python
import hashlib
import secrets
import base64

# Client side (al iniciar authorization)
def generate_pkce_pair():
    # 1. Generar code_verifier aleatorio
    code_verifier = base64.urlsafe_b64encode(
        secrets.token_bytes(32)
    ).decode('utf-8').rstrip('=')

    # 2. Generar code_challenge (SHA256 hash)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')

    return code_verifier, code_challenge

# Authorization request
verifier, challenge = generate_pkce_pair()
auth_url = (
    f"{auth_server}/oauth/authorize?"
    f"response_type=code&"
    f"client_id={client_id}&"
    f"redirect_uri={redirect_uri}&"
    f"scope=youtube:extract&"
    f"code_challenge={challenge}&"
    f"code_challenge_method=S256"
)

# Token exchange (después de recibir authorization code)
token_response = requests.post(
    f"{auth_server}/oauth/token",
    data={
        "grant_type": "authorization_code",
        "code": authorization_code,
        "code_verifier": verifier,  # Server valida: SHA256(verifier) == challenge
        "redirect_uri": redirect_uri
    }
)
```

#### Token Validation (Server-side)

```python
# src/middleware/auth.py
import jwt
from jwt import PyJWKClient
from functools import lru_cache
from typing import Dict, Any

class TokenValidator:
    def __init__(self, jwks_url: str, audience: str, issuer: str):
        self.jwk_client = PyJWKClient(jwks_url, cache_keys=True)
        self.audience = audience
        self.issuer = issuer

    @lru_cache(maxsize=1000)
    def get_signing_key(self, token: str):
        """Cache signing keys por kid"""
        return self.jwk_client.get_signing_key_from_jwt(token)

    async def validate_token(self, authorization: str) -> Dict[str, Any]:
        """
        Valida token OAuth 2.1 y retorna claims
        Raises: HTTPException si inválido
        """
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Missing or invalid Authorization header"
            )

        token = authorization[7:]  # Remove "Bearer "

        try:
            # 1. Obtener signing key (cached)
            signing_key = self.get_signing_key(token)

            # 2. Validar JWT
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256", "ES256"],  # Solo algoritmos asimétricos
                audience=self.audience,
                issuer=self.issuer,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_aud": True,
                    "verify_iss": True,
                    "require": ["exp", "iat", "sub", "aud"]
                }
            )

            # 3. Validaciones adicionales
            # Resource Indicator (previene token reuse)
            if "resource" in claims and claims["resource"] != self.audience:
                raise HTTPException(
                    status_code=403,
                    detail="Token not valid for this resource"
                )

            # Scope validation
            scopes = claims.get("scope", "").split()
            if "youtube:extract" not in scopes:
                raise HTTPException(
                    status_code=403,
                    detail="Insufficient scopes"
                )

            # 4. Extraer user_id
            user_id = claims["sub"]

            # 5. Rate limit check (per-user)
            if await self.is_rate_limited(user_id):
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded"
                )

            return {
                "user_id": user_id,
                "scopes": scopes,
                "claims": claims
            }

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"}
            )

        except jwt.InvalidAudienceError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token audience"
            )

        except jwt.InvalidIssuerError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token issuer"
            )

        except Exception as e:
            logger.error("token_validation_failed", error=str(e))
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    async def is_rate_limited(self, user_id: str) -> bool:
        """Check rate limit from Redis"""
        # Ver sección Rate Limiting
        pass
```

---

## 🛡️ Multi-Tenant Data Isolation

### Principio: Query-Level Isolation

**Regla de oro:** TODAS las queries incluyen `user_id` como filtro.

```python
# ❌ MAL: Query sin user_id
async def get_transcripts():
    return await db.fetch("SELECT * FROM transcripts")

# ✅ BIEN: Query con user_id obligatorio
async def get_transcripts(user_id: str):
    return await db.fetch(
        "SELECT * FROM transcripts WHERE user_id = $1",
        user_id
    )
```

### Row-Level Security (PostgreSQL)

```sql
-- Habilitar RLS en tabla transcripts
ALTER TABLE transcripts ENABLE ROW LEVEL SECURITY;

-- Policy: users solo ven sus propios datos
CREATE POLICY user_isolation ON transcripts
    FOR ALL
    USING (user_id = current_setting('app.current_user_id')::uuid);

-- Application debe setear user_id en session
-- Antes de cada query:
SET LOCAL app.current_user_id = 'user-uuid-here';
```

**Implementación en código:**

```python
async def execute_with_user_context(user_id: str, query: str, *args):
    """Execute query with RLS context"""
    async with db.transaction():
        # Set user context
        await db.execute(
            "SET LOCAL app.current_user_id = $1",
            user_id
        )
        # Execute actual query (RLS applies automatically)
        result = await db.fetch(query, *args)
        return result
```

---

## 🚫 Rate Limiting

### Estrategia Multi-Layer

```
┌────────────────────────────────────────┐
│  Layer 1: Global Rate Limit            │
│  (CloudFlare / Edge)                   │
│  • 10,000 req/s global                 │
│  • Per-IP: 100 req/min                 │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│  Layer 2: Per-User Rate Limit          │
│  (API Gateway / App)                   │
│  • Free tier: 100 req/day              │
│  • Pro tier: 10,000 req/day            │
│  • Enterprise: unlimited               │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│  Layer 3: Resource Quotas              │
│  (Application Logic)                   │
│  • Videos extracted: 1,000/month       │
│  • Playlists: 50/month                 │
│  • Storage: 10GB                       │
└────────────────────────────────────────┘
```

### Implementación (Redis + Token Bucket)

```python
# src/middleware/rate_limit.py
import time
from typing import Optional

class TokenBucketRateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def check_rate_limit(
        self,
        user_id: str,
        max_tokens: int = 100,
        refill_rate: int = 10,  # tokens/minute
        window: int = 60  # seconds
    ) -> tuple[bool, Optional[int]]:
        """
        Token bucket algorithm
        Returns: (allowed: bool, retry_after: Optional[int])
        """
        key = f"rate_limit:{user_id}"
        now = time.time()

        # Lua script para atomicidad
        lua_script = """
        local key = KEYS[1]
        local max_tokens = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])

        local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(bucket[1]) or max_tokens
        local last_refill = tonumber(bucket[2]) or now

        -- Refill tokens
        local elapsed = now - last_refill
        local new_tokens = math.min(
            max_tokens,
            tokens + (elapsed * refill_rate / 60)
        )

        -- Check if request allowed
        if new_tokens >= 1 then
            new_tokens = new_tokens - 1
            redis.call('HMSET', key, 'tokens', new_tokens, 'last_refill', now)
            redis.call('EXPIRE', key, 3600)
            return {1, new_tokens}  -- Allowed
        else
            return {0, new_tokens}  -- Denied
        end
        """

        result = await self.redis.eval(
            lua_script,
            keys=[key],
            args=[max_tokens, refill_rate, now]
        )

        allowed = result[0] == 1
        remaining_tokens = result[1]

        if not allowed:
            # Calculate retry_after
            tokens_needed = 1 - remaining_tokens
            retry_after = int((tokens_needed / refill_rate) * 60)
            return False, retry_after

        return True, None

# Middleware FastAPI
from fastapi import Request, HTTPException

async def rate_limit_middleware(request: Request, call_next):
    user_id = request.state.user_id  # Seteado por auth middleware

    # Obtener tier del usuario
    user_tier = await get_user_tier(user_id)
    limits = {
        "free": {"max_tokens": 100, "refill_rate": 10},
        "pro": {"max_tokens": 10000, "refill_rate": 1000},
        "enterprise": {"max_tokens": float("inf"), "refill_rate": float("inf")}
    }

    if user_tier != "enterprise":
        limiter = TokenBucketRateLimiter(redis_client)
        allowed, retry_after = await limiter.check_rate_limit(
            user_id,
            **limits[user_tier]
        )

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limits[user_tier]["max_tokens"]),
                    "X-RateLimit-Remaining": "0"
                }
            )

    response = await call_next(request)
    return response
```

---

## 🔒 Encryption

### En Tránsito (TLS/HTTPS)

**Requirements:**
- TLS 1.3 obligatorio
- Certificados válidos (Let's Encrypt / CloudFlare)
- HSTS enabled
- No downgrade a HTTP

```python
# FastAPI con TLS
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=443,
        ssl_keyfile="/path/to/key.pem",
        ssl_certfile="/path/to/cert.pem",
        ssl_version=ssl.PROTOCOL_TLSv1_3,  # Solo TLS 1.3
        headers=[
            ("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        ]
    )
```

### En Reposo (Database)

**PostgreSQL encryption:**

```sql
-- Column-level encryption para datos sensibles
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt on write
INSERT INTO users (email_encrypted, api_key_encrypted)
VALUES (
    pgp_sym_encrypt('user@example.com', 'encryption-key'),
    pgp_sym_encrypt('api-key-secret', 'encryption-key')
);

-- Decrypt on read
SELECT
    pgp_sym_decrypt(email_encrypted::bytea, 'encryption-key') AS email,
    pgp_sym_decrypt(api_key_encrypted::bytea, 'encryption-key') AS api_key
FROM users
WHERE id = 'user-id';
```

**Better: Usar Google Cloud KMS**

```python
from google.cloud import kms

class EncryptionService:
    def __init__(self, project_id: str, location: str, key_ring: str, key: str):
        self.client = kms.KeyManagementServiceClient()
        self.key_name = (
            f"projects/{project_id}/locations/{location}/"
            f"keyRings/{key_ring}/cryptoKeys/{key}"
        )

    async def encrypt(self, plaintext: str) -> str:
        """Encrypt data using Cloud KMS"""
        response = self.client.encrypt(
            request={
                "name": self.key_name,
                "plaintext": plaintext.encode("utf-8")
            }
        )
        return base64.b64encode(response.ciphertext).decode("utf-8")

    async def decrypt(self, ciphertext: str) -> str:
        """Decrypt data using Cloud KMS"""
        response = self.client.decrypt(
            request={
                "name": self.key_name,
                "ciphertext": base64.b64decode(ciphertext)
            }
        )
        return response.plaintext.decode("utf-8")
```

---

## 📋 Audit Logging

### Qué Loggear

| Evento | Nivel | Datos |
|--------|-------|-------|
| User login/logout | INFO | user_id, timestamp, IP |
| Token issued/refreshed | INFO | user_id, scopes, expiry |
| API call | INFO | user_id, tool, params (sanitized), latency |
| Authorization denied | WARN | user_id, resource, reason |
| Rate limit exceeded | WARN | user_id, limit, retry_after |
| Data access | INFO | user_id, resource_type, resource_id |
| Data modification | INFO | user_id, resource, old_value, new_value |
| Security event | ERROR | type, details, IP, user_agent |

### Structured Audit Log (JSON)

```python
import structlog

audit_logger = structlog.get_logger("audit")

# Ejemplo: Video extraction
audit_logger.info(
    "video_extracted",
    user_id="user_123",
    video_id="dQw4w9WgXcQ",
    language="es",
    source_method="yt-dlp",
    duration_seconds=5.2,
    success=True,
    timestamp="2025-11-05T12:34:56.789Z",
    request_id="abc-def-ghi",
    ip_address="203.0.113.42",
    user_agent="Claude Desktop/0.7.0"
)

# Output (JSON):
{
  "event": "video_extracted",
  "level": "info",
  "user_id": "user_123",
  "video_id": "dQw4w9WgXcQ",
  "language": "es",
  "source_method": "yt-dlp",
  "duration_seconds": 5.2,
  "success": true,
  "timestamp": "2025-11-05T12:34:56.789Z",
  "request_id": "abc-def-ghi",
  "ip_address": "203.0.113.42",
  "user_agent": "Claude Desktop/0.7.0"
}
```

---

## 🌍 Compliance

### GDPR (General Data Protection Regulation)

**Requisitos:**

1. **Right to Access** - Usuario puede descargar sus datos
```python
@app.get("/api/user/data")
async def get_user_data(user_id: str = Depends(get_user_id)):
    """Export all user data (GDPR compliance)"""
    transcripts = await db.fetch_all_user_transcripts(user_id)
    usage_logs = await db.fetch_all_user_logs(user_id)

    return {
        "user_id": user_id,
        "transcripts": transcripts,
        "usage_logs": usage_logs,
        "export_date": datetime.utcnow()
    }
```

2. **Right to Deletion** - Usuario puede eliminar sus datos
```python
@app.delete("/api/user/account")
async def delete_user_account(user_id: str = Depends(get_user_id)):
    """Delete all user data (GDPR right to erasure)"""
    # Soft delete (marca como eliminado, purga después de 30 días)
    await db.execute(
        "UPDATE users SET deleted_at = NOW() WHERE id = $1",
        user_id
    )
    # Anonymize logs (mantener métricas agregadas)
    await db.execute(
        "UPDATE usage_logs SET user_id = NULL WHERE user_id = $1",
        user_id
    )
    # Schedule physical deletion (background job)
    await schedule_data_purge(user_id, delay_days=30)
```

3. **Data Minimization** - Solo guardar datos necesarios
4. **Purpose Limitation** - Usar datos solo para propósito declarado
5. **Storage Limitation** - No guardar indefinidamente

### SOC 2 Type II (Para clientes enterprise)

**Controles requeridos:**

- ✅ Access control (OAuth 2.1)
- ✅ Encryption (TLS + at-rest)
- ✅ Audit logging (structured logs)
- ✅ Incident response plan
- ✅ Vendor management (third-party deps)
- ✅ Change management (CI/CD pipeline)
- ✅ Availability monitoring (99.9% uptime)

---

## 🚨 Incident Response

### Security Incident Playbook

**1. Detection:**
- Anomaly detection (Datadog alerts)
- Failed auth attempts spike
- Unusual data access patterns

**2. Containment:**
```python
# Emergency: Revoke todos los tokens de un usuario
async def emergency_revoke_user_tokens(user_id: str):
    # Agregar user a blacklist
    await redis.sadd("token_blacklist:users", user_id)
    await redis.expire("token_blacklist:users", 86400)  # 24h

    # Notificar al usuario
    await send_security_notification(user_id, "tokens_revoked")
```

**3. Investigation:**
- Query audit logs
- Identificar scope del breach
- Documentar timeline

**4. Recovery:**
- Patch vulnerability
- Deploy fix
- Verificar no más explotación

**5. Post-mortem:**
- Root cause analysis
- Preventive measures
- Update security policies

---

## ✅ Security Checklist (Pre-Production)

### Application Security
- [ ] OAuth 2.1 con PKCE implementado
- [ ] Token validation con JWKS
- [ ] Multi-tenant isolation verificado
- [ ] Rate limiting configurado
- [ ] Input validation en todos endpoints
- [ ] Output sanitization (prevenir XSS)
- [ ] SQL injection protección (prepared statements)
- [ ] CORS configurado correctamente

### Infrastructure Security
- [ ] TLS 1.3 habilitado
- [ ] HSTS configurado
- [ ] Secrets en KMS/Secrets Manager (no hardcoded)
- [ ] Database encryption at-rest
- [ ] VPC / private networking
- [ ] Firewall rules (solo puertos necesarios)
- [ ] DDoS protection (CloudFlare)

### Operational Security
- [ ] Audit logging habilitado
- [ ] Alerting configurado (security events)
- [ ] Backup strategy definida
- [ ] Incident response plan documentado
- [ ] Security monitoring (SIEM)
- [ ] Penetration testing ejecutado
- [ ] Dependency scanning (Snyk/Dependabot)
- [ ] GDPR compliance verificado

---

**Última actualización:** 2025-11-05
**Próximo documento:** [../roadmap/01-implementation-phases.md](../roadmap/01-implementation-phases.md)
