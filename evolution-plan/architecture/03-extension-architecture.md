# Arquitectura de Extensión Claude Desktop (.mcpb)

**Versión:** 1.0
**Fecha:** 2025-11-05
**Target:** Fase 1 del Roadmap (Prioridad P0)

---

## 🎯 Objetivo

Transformar el servidor actual en una **Claude Desktop Extension** (.mcpb) que permita instalación con un solo click, eliminando la barrera de entrada técnica.

---

## 📦 ¿Qué es un .mcpb?

Un archivo `.mcpb` (MCP Bundle) es un **archivo ZIP** que contiene:

1. **manifest.json** - Metadata y configuración
2. **Código fuente del servidor** - Scripts Python/Node.js/binario
3. **Dependencias (opcional)** - Si no se gestionan dinámicamente

Claude Desktop incluye un **runtime Node.js integrado**, eliminando la necesidad de instalación externa para servidores Node.js.

---

## 🏗️ Estructura Propuesta

### Estructura del Paquete

```
youtube-extract-mcp.mcpb (ZIP)
│
├── manifest.json              # REQUERIDO: Metadata y configuración
├── icon.png                   # Icono de la extensión (128x128)
├── README.md                  # Documentación del usuario
│
├── server/
│   ├── youtube_extract_mcp.py # Servidor principal
│   ├── playlist_processor.py  # Módulo de playlists
│   └── requirements.txt       # Dependencias Python
│
└── scripts/
    ├── install.sh             # Script de instalación (Unix)
    └── install.ps1            # Script de instalación (Windows)
```

---

## 📄 Manifest Specification

### manifest.json Completo

```json
{
  "mcpb_version": "0.1",
  "name": "youtube-extract-mcp",
  "display_name": "YouTube Transcript Extractor",
  "version": "1.0.0",
  "description": "Robust YouTube transcription extraction with triple-fallback system. Supports videos and playlists with automatic language detection.",
  "author": {
    "name": "SOCIUM-CR",
    "email": "contact@socium.cr",
    "url": "https://github.com/SOCIUM-CR"
  },
  "homepage": "https://github.com/SOCIUM-CR/youtube-extract-mcp-server",
  "license": "MIT",
  "icon": "icon.png",

  "server": {
    "type": "python",
    "entry_point": "${__dirname}/server/youtube_extract_mcp.py",
    "mcp_config": {
      "command": "uv",
      "args": [
        "--directory",
        "${__dirname}/server",
        "run",
        "youtube_extract_mcp.py"
      ],
      "env": {
        "YOUTUBE_EXTRACT_OUTPUT_DIR": "${user_config.output_directory}",
        "PYTHONUNBUFFERED": "1"
      }
    }
  },

  "user_config": {
    "output_directory": {
      "type": "string",
      "display_name": "Output Directory",
      "description": "Local directory where transcriptions will be saved",
      "default": "${HOME}/YouTube-Transcripts",
      "required": false,
      "secure": false
    }
  },

  "permissions": {
    "network": true,
    "filesystem": {
      "read": true,
      "write": true,
      "directories": ["${user_config.output_directory}"]
    }
  },

  "requirements": {
    "claude_desktop_version": ">=0.7.0",
    "operating_systems": ["macos", "windows", "linux"],
    "python_version": ">=3.11"
  },

  "tools": [
    {
      "name": "youtube_extract_video",
      "description": "Extract transcription from a single YouTube video",
      "parameters": {
        "url": {
          "type": "string",
          "description": "YouTube video URL",
          "required": true
        },
        "language": {
          "type": "string",
          "description": "Preferred language code (e.g., 'en', 'es', 'auto')",
          "default": "auto"
        },
        "include_timestamps": {
          "type": "boolean",
          "description": "Include timestamps in transcription",
          "default": true
        },
        "save_locally": {
          "type": "boolean",
          "description": "Save transcription to local directory",
          "default": false
        }
      }
    },
    {
      "name": "youtube_extract_playlist",
      "description": "Extract transcriptions from entire YouTube playlist",
      "parameters": {
        "playlist_url": {
          "type": "string",
          "description": "YouTube playlist URL",
          "required": true
        },
        "max_videos": {
          "type": "number",
          "description": "Maximum number of videos to process",
          "default": 50
        }
      }
    },
    {
      "name": "configure_output_directory",
      "description": "Set the local directory for saving transcriptions",
      "parameters": {
        "directory_path": {
          "type": "string",
          "description": "Absolute path to output directory",
          "required": true
        }
      }
    },
    {
      "name": "show_current_config",
      "description": "Display current configuration settings"
    }
  ],

  "changelog": "https://github.com/SOCIUM-CR/youtube-extract-mcp-server/blob/main/CHANGELOG.md",
  "documentation": "https://github.com/SOCIUM-CR/youtube-extract-mcp-server/blob/main/README.md"
}
```

### Explicación de Campos Clave

#### 1. **server.type**

Opciones: `"node"`, `"python"`, `"binary"`

**Nuestra elección:** `"python"`

**Implicaciones:**
- Claude Desktop **no** incluye Python (a diferencia de Node.js)
- Requiere que el usuario tenga Python instalado
- **Solución:** Usar `uv` que gestiona el entorno automáticamente

#### 2. **Template Literals**

El manifest soporta variables dinámicas:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `${__dirname}` | Directorio de instalación de la extensión | `/Users/user/Library/Application Support/Claude/extensions/youtube-extract-mcp` |
| `${HOME}` | Directorio home del usuario | `/Users/user` |
| `${user_config.KEY}` | Valor de configuración del usuario | `${user_config.output_directory}` |

**Ejemplo de uso:**
```json
{
  "args": [
    "--directory",
    "${__dirname}/server",  // Se resuelve en runtime
    "run",
    "youtube_extract_mcp.py"
  ]
}
```

#### 3. **user_config**

Define inputs que el usuario configura durante instalación:

```json
{
  "user_config": {
    "output_directory": {
      "type": "string",
      "display_name": "Output Directory",
      "description": "Where to save transcriptions",
      "default": "${HOME}/YouTube-Transcripts",
      "required": false,
      "secure": false  // No se almacena en keychain
    }
  }
}
```

**Para API keys (sensibles):**
```json
{
  "user_config": {
    "api_key": {
      "type": "string",
      "display_name": "API Key",
      "secure": true,  // Se almacena en OS keychain
      "required": true
    }
  }
}
```

---

## 🛠️ Proceso de Creación

### Paso 1: Instalar MCPB CLI

```bash
npm install -g @anthropic-ai/mcpb
```

### Paso 2: Inicializar Manifest

```bash
cd youtube-extract-mcp-server
mcpb init
```

**Wizard interactivo:**
```
? Extension name: youtube-extract-mcp
? Display name: YouTube Transcript Extractor
? Version: 1.0.0
? Description: Robust YouTube transcription extraction...
? Author name: SOCIUM-CR
? Author email: contact@socium.cr
? License: MIT
? Server type: (Use arrow keys)
  ❯ python
    node
    binary
? Entry point: server/youtube_extract_mcp.py
```

Esto genera un `manifest.json` base que podemos personalizar.

### Paso 3: Configurar Estructura

```bash
# Crear estructura de carpetas
mkdir -p server scripts

# Copiar archivos del servidor
cp youtube_extract_mcp.py server/
cp playlist_processor.py server/

# Crear icon.png (128x128)
# Diseñar icono representativo (ej: logo YouTube + texto)
```

### Paso 4: Adaptar Código (Si necesario)

**Cambios mínimos requeridos:**

```python
# server/youtube_extract_mcp.py

# Cambio 1: Detectar directorio de instalación
import os
from pathlib import Path

# Antes:
# self.temp_dir = Path(tempfile.gettempdir()) / "youtube-extract-mcp"

# Después:
extension_dir = Path(__file__).parent.parent  # .mcpb installation dir
self.temp_dir = extension_dir / "temp"
self.temp_dir.mkdir(exist_ok=True)

# Cambio 2: Configuración desde environment (inyectada por manifest)
self.output_directory = os.getenv(
    "YOUTUBE_EXTRACT_OUTPUT_DIR",
    str(Path.home() / "YouTube-Transcripts")
)
```

**Nota:** El código actual ya es compatible, solo necesita verificación.

### Paso 5: Validar y Empaquetar

```bash
# Validar manifest
mcpb validate

# Output esperado:
# ✅ Manifest is valid
# ✅ Entry point exists
# ✅ All required fields present
# ✅ Icon dimensions correct (128x128)

# Empaquetar
mcpb pack

# Output:
# 📦 Creating package...
# ✅ youtube-extract-mcp-1.0.0.mcpb created (2.3 MB)
```

### Paso 6: Testing Local

```bash
# Opción 1: Instalar en Claude Desktop
# 1. Abrir Claude Desktop
# 2. Settings > Extensions > Advanced settings
# 3. "Install Extension..." > Seleccionar .mcpb

# Opción 2: CLI testing
mcpb test youtube-extract-mcp-1.0.0.mcpb
```

---

## 🧪 Testing Strategy

### Test Matrix

| OS | Python | uv | Claude Desktop | Status |
|----|--------|----|----|--------|
| macOS 14 | 3.11 | latest | 0.7.0+ | ✅ |
| macOS 14 | 3.12 | latest | 0.7.0+ | ✅ |
| Windows 11 | 3.11 | latest | 0.7.0+ | ⏳ |
| Windows 11 | 3.12 | latest | 0.7.0+ | ⏳ |
| Ubuntu 22.04 | 3.11 | latest | 0.7.0+ | ⏳ |

### Checklist de Testing

**Pre-instalación:**
- [ ] Manifest válido (`mcpb validate`)
- [ ] Icon correcto (128x128 PNG)
- [ ] README completo
- [ ] Tamaño < 10MB

**Post-instalación:**
- [ ] Extensión aparece en lista
- [ ] Configuración de output_directory funciona
- [ ] Todas las herramientas listadas en Claude
- [ ] `youtube_extract_video` funciona
- [ ] `youtube_extract_playlist` funciona
- [ ] Archivos se guardan en directorio configurado
- [ ] Logs visibles en Claude Desktop console

**Edge cases:**
- [ ] Instalación sin Python (error claro)
- [ ] Instalación sin uv (auto-instala en primera ejecución)
- [ ] Cambio de output_directory post-instalación
- [ ] Desinstalación limpia (no deja archivos)

---

## 📤 Distribución

### Opción 1: GitHub Releases (Inmediato)

```bash
# Crear release en GitHub
gh release create v1.0.0 \
  youtube-extract-mcp-1.0.0.mcpb \
  --title "YouTube Extract MCP v1.0.0" \
  --notes "First .mcpb release. One-click installation for Claude Desktop."
```

**Instalación por usuarios:**
1. Descargar `.mcpb` desde GitHub releases
2. Doble click en archivo
3. Claude Desktop abre automáticamente
4. Click "Install"

### Opción 2: Anthropic Extension Directory (Oficial)

**Proceso de submisión:**

1. **Preparación:**
   - ✅ Extensión testeada en macOS + Windows
   - ✅ README completo con screenshots
   - ✅ Iconografía profesional
   - ✅ Changelog mantenido

2. **Submission Form:**
   ```
   URL: https://anthropic.com/submit-extension
   Campos requeridos:
   - Extension name
   - .mcpb file upload
   - Category: Productivity / Content
   - Description (500 chars)
   - Screenshots (3-5)
   - Support email
   - Terms of Service URL
   - Privacy Policy URL
   ```

3. **Review Process:**
   - Security scan (automated)
   - Functionality testing (Anthropic team)
   - UX review
   - Approval: 1-2 semanas

4. **Publicación:**
   - Aparece en Claude Desktop Extension Directory
   - Usuarios descubren y instalan desde UI

**Beneficios del Directory:**
- ✅ Discoverability masiva
- ✅ Auto-updates gestionadas por Claude
- ✅ Credibilidad (verificado por Anthropic)
- ✅ Mejor UX (todo desde UI)

### Opción 3: Distribución Corporativa

Para empresas que quieren deployment interno:

```bash
# Configurar enterprise extension repository
# (Requiere Claude Desktop Enterprise)
{
  "extensionRepositories": [
    "https://extensions.company.com/mcp/"
  ]
}
```

---

## 🔄 Actualización y Versionamiento

### Estrategia de Versioning (SemVer)

```
MAJOR.MINOR.PATCH

1.0.0 → Initial release
1.0.1 → Bug fix (triple fallback)
1.1.0 → New feature (cache support)
2.0.0 → Breaking change (HTTP transport)
```

### Proceso de Actualización

**Para usuarios con auto-update (Directory):**
```json
{
  "manifest.json": {
    "version": "1.1.0",  // Incrementar
    "changelog_url": "..."  // Link a changelog
  }
}
```

Claude Desktop detecta automáticamente y notifica al usuario.

**Para usuarios con instalación manual:**
- Publicar nuevo `.mcpb` en GitHub releases
- Usuario descarga y reinstala (no breaking)

---

## 🎨 UI/UX Considerations

### Icono de la Extensión

**Requisitos:**
- Formato: PNG
- Dimensiones: 128x128 pixels
- Transparencia: Opcional
- Estilo: Flat design, colores distintivos

**Propuesta conceptual:**
```
┌─────────────────┐
│                 │
│   📹 → 📝       │   (YouTube icon → Document)
│                 │
│ YouTube Extract │
│                 │
└─────────────────┘
```

### Texto de Descripción (Display en Directory)

**Short (100 chars):**
> Extract YouTube transcriptions with 99% success rate. Videos & playlists supported.

**Long (500 chars):**
> YouTube Transcript Extractor provides robust, reliable transcription extraction from YouTube videos and playlists. Features triple-fallback system (yt-dlp + youtube-transcript-api) ensuring 99%+ success rate, automatic language detection, dual formats (plain text + timestamps), and local file persistence. Perfect for content creators, researchers, and anyone needing reliable YouTube transcriptions.

### Screenshots para Directory

**Screenshot 1: Extension in action**
- Claude Desktop con extensión activa
- Ejemplo de extracción de video

**Screenshot 2: Configuration**
- Panel de configuración de output directory

**Screenshot 3: Results**
- Transcripción extraída con metadata

---

## 📊 Métricas de Éxito

| Métrica | Baseline (Actual) | Target (.mcpb) |
|---------|-------------------|----------------|
| Tiempo de instalación | 15-30 min | < 2 min |
| Tasa de éxito instalación | ~15% | 90%+ |
| Usuarios técnicos requeridos | Sí | No |
| Configuración manual | Sí (JSON editing) | No (UI wizard) |
| Actualizaciones | Manual (git pull) | Automáticas |

---

## 🚀 Roadmap de Extensión

### v1.0.0 (Fase 1) - stdio local
- ✅ Manifest completo
- ✅ Empaquetado .mcpb
- ✅ Testing macOS + Windows
- ✅ GitHub releases
- ⏳ Submit a Anthropic Directory

### v1.1.0 (Fase 2) - Enhancements
- Cache de transcripciones (Redis local)
- Stats de uso
- Progreso de playlists (notifications)

### v2.0.0 (Fase 3) - HTTP transport
- Soporte HTTP local
- Configuración de puerto
- Multi-client support

---

## 📚 Recursos y Referencias

- [MCPB Specification](https://github.com/anthropics/mcpb)
- [Claude Desktop Extensions Documentation](https://www.anthropic.com/engineering/desktop-extensions)
- [MCPB CLI Tool](https://www.npmjs.com/package/@anthropic-ai/mcpb)
- [Extension Submission Form](https://anthropic.com/submit-extension)

---

**Última actualización:** 2025-11-05
**Próximo documento:** [../deployment/01-hosting-options.md](../deployment/01-hosting-options.md)
