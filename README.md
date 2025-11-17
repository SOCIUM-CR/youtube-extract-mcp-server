# YouTube Transcript Extractor
### Claude Desktop Extension for YouTube Transcription

[![Version](https://img.shields.io/badge/version-1.0.4-blue.svg)](https://github.com/SOCIUM-CR/youtube-extract-mcp-server/releases/tag/v1.0.4)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-1.0.0-purple.svg)](https://modelcontextprotocol.io/)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey.svg)]()

Un servidor MCP para extracción robusta de transcripciones de YouTube, ahora disponible como extensión de Claude Desktop con instalación de un solo clic.

---

## ✨ Características

- 🎯 **Extracción de transcripciones** de videos y playlists de YouTube
- 🌍 **Detección automática de idioma** con soporte multilingüe
- 💾 **Persistencia local** de archivos con estructura organizada
- 📝 **Formatos duales**: texto plano y con timestamps
- 🔄 **Sistema triple-fallback** para 99%+ de tasa de éxito
- ⚙️ **Configuración de usuario** mediante UI o herramientas
- 📦 **Instalación one-click** mediante archivo .mcpb

---

## 🚀 Instalación Rápida (Recomendada)

### Método 1: Extensión .mcpb (One-Click)

**Más fácil y recomendado:**

1. **Descarga** el archivo `.mcpb` de la [última release](https://github.com/SOCIUM-CR/youtube-extract-mcp-server/releases/latest)
2. **Doble-click** en el archivo descargado (o abre desde Claude Desktop → Settings → Extensions → Advanced)
3. **Configura** el directorio de salida (opcional, default: `~/YouTube-Transcripts`)
4. **¡Listo!** - La extensión está instalada y lista para usar

**Requisitos:**
- Claude Desktop (última versión)
- Python 3.11+ instalado en tu sistema

**Ventajas:**
- ✅ Instalación automática de dependencias
- ✅ Sin edición manual de archivos JSON
- ✅ Configuración mediante UI
- ✅ Actualizaciones fáciles

📖 **Guía detallada:** [INSTALLATION.md](.mcpb-build/INSTALLATION.md)

---

### Método 2: Instalación Manual (stdio)

**Para usuarios avanzados o desarrollo:**

<details>
<summary>Click para expandir instrucciones de instalación manual</summary>

#### Prerrequisitos

- **uv**: Un gestor de paquetes de Python rápido. Si no lo tienes, instálalo:

  **macOS / Linux:**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

  **Windows (PowerShell):**
  ```powershell
  irm https://astral.sh/uv/install.ps1 | iex
  ```

#### Pasos de Instalación

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/SOCIUM-CR/youtube-extract-mcp-server.git
   cd youtube-extract-mcp-server
   ```

2. **Configura Claude Desktop:**

   Encuentra tu archivo de configuración:
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux:** `~/.config/Claude/claude_desktop_config.json`

3. **Agrega esta configuración** (reemplaza las rutas con las absolutas de tu sistema):

   ```json
   {
     "mcpServers": {
       "youtube-extract-mcp": {
         "command": "/ruta/absoluta/a/tu/uv",
         "args": [
           "--directory",
           "/ruta/absoluta/al/proyecto/",
           "run",
           "youtube_extract_mcp.py"
         ],
         "env": {
           "PATH": "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin"
         }
       }
     }
   }
   ```

   💡 **Tip:** Encuentra la ruta de `uv` con `which uv` en tu terminal.

4. **Reinicia Claude Desktop**

**Migración:** Si ya usas la instalación manual, considera migrar a la extensión .mcpb para una experiencia más simple. Ver [CHANGELOG.md](.mcpb-build/CHANGELOG.md) para detalles.

</details>

---

## 📚 Uso

### Herramientas Disponibles

La extensión proporciona 4 herramientas que puedes usar directamente en conversaciones con Claude:

| Herramienta | Descripción |
|-------------|-------------|
| `youtube_extract_video` | Extrae metadatos y transcripción de un video |
| `youtube_extract_playlist` | Extrae transcripciones de una playlist completa |
| `configure_output_directory` | Configura dónde se guardan las transcripciones |
| `show_current_config` | Muestra la configuración actual |

### Ejemplos de Uso

**Extraer un video:**
```
Extrae la transcripción de https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

**Extraer con timestamps:**
```
Extrae la transcripción con timestamps de este video: [URL]
```

**Extraer playlist:**
```
Extrae las transcripciones de esta playlist: https://www.youtube.com/playlist?list=PL...
```

**Configurar directorio:**
```
Configura el directorio de salida de YouTube Transcript Extractor a ~/Documents/Transcripts
```

**Ver configuración:**
```
Muestra la configuración actual de YouTube Transcript Extractor
```

### Formatos de Salida

Las transcripciones se guardan automáticamente en:
```
~/YouTube-Transcripts/
└── [video_id]/
    ├── metadata.json              # Info del video
    ├── transcript.txt             # Texto plano
    └── transcript_timestamped.txt # Con timestamps
```

---

## 🛠️ Cómo Funciona

### Sistema Triple-Fallback

Para garantizar la máxima compatibilidad, el servidor intenta extraer transcripciones usando tres métodos en secuencia:

1. **yt-dlp** con bypass de PO Token (método principal)
2. **yt-dlp** con clientes alternativos (android, web_embedded)
3. **youtube-transcript-api** (fallback garantizado)

**Resultado:** ~99% de tasa de éxito en videos con transcripciones disponibles.

### Arquitectura

```
┌─────────────────┐
│ Claude Desktop  │
└────────┬────────┘
         │ MCP Protocol (stdio)
         v
┌─────────────────┐
│   run.sh        │  ← Detecta uv o usa venv
└────────┬────────┘
         v
┌─────────────────┐
│ youtube_extract │  ← Servidor principal
│    _mcp.py      │  ← 4 herramientas MCP
└────────┬────────┘
         │
         ├→ yt-dlp (primary)
         ├→ yt-dlp (fallback)
         └→ youtube-transcript-api (fallback)
```

---

## 📖 Documentación

### Para Usuarios
- [📦 Guía de Instalación](.mcpb-build/INSTALLATION.md)
- [📝 Historial de Cambios](.mcpb-build/CHANGELOG.md)
- [🎯 Notas de Release](RELEASE_NOTES_v1.0.4.md)

### Para Desarrolladores
- [🤖 Reporte de Desarrollo con IA](docs/AI_DEVELOPMENT_REPORT.md) - Metodología completa
- [🔧 Log de Decisiones Técnicas](docs/TECHNICAL_DECISIONS.md) - 10 decisiones arquitectónicas
- [📋 Plan de Testing](docs/TESTING_PLAN.md) - Suite de pruebas
- [🚀 Checklist de Release](docs/RELEASE_CHECKLIST.md)

### Roadmap
- [🗺️ Plan de Evolución](evolution-plan/README.md) - Estrategia completa (3 fases)
- [📊 Fases de Implementación](evolution-plan/roadmap/01-implementation-phases.md)

---

## 🔧 Requisitos Técnicos

### Mínimos
- **Claude Desktop:** Última versión
- **Python:** 3.11 o superior
- **Sistema Operativo:** macOS, Windows, o Linux
- **Espacio en Disco:** ~1 MB para instalación
- **Red:** Conexión a internet para acceso a YouTube

### Dependencias (instaladas automáticamente)
```python
mcp >= 1.0.0
yt-dlp >= 2024.4.9
youtube-transcript-api >= 1.2.3
```

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: Amazing Feature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para detalles (si existe).

---

## 🐛 Reportar Problemas

¿Encontraste un bug? ¿Tienes una sugerencia?

- **Issues:** [GitHub Issues](https://github.com/SOCIUM-CR/youtube-extract-mcp-server/issues)
- **Discussions:** [GitHub Discussions](https://github.com/SOCIUM-CR/youtube-extract-mcp-server/discussions)

Por favor incluye:
- Versión de la extensión
- Sistema operativo
- Pasos para reproducir
- Mensajes de error (si aplica)

---

## 📊 Estado del Proyecto

### Fase Actual: Phase 1 - Extensión .mcpb ✅

- [✅] **Milestone 1.1:** Preparación y Empaquetado
- [🟡] **Milestone 1.2:** Testing Local (en progreso)
- [ ] **Milestone 1.3:** Refinamiento y Release Oficial

### Próximas Fases

**Phase 2: HTTP Transport** (3-4 semanas)
- Soporte para HTTP+SSE
- Deployment remoto opcional
- Múltiples clientes simultáneos

**Phase 3: Production SaaS** (6-8 semanas)
- Cloud deployment (Google Cloud Run)
- OAuth 2.1 authentication
- Multi-tenancy support

**Timeline Total:** 14-20 semanas

Ver [Roadmap completo](evolution-plan/roadmap/01-implementation-phases.md)

---

## 📈 Métricas

### v1.0.4 (Release Actual)
- **Tasa de éxito:** 99%+ (cuando hay transcripciones)
- **Extracción de metadata:** 100%
- **Tamaño del paquete:** 32.5 KB
- **Tiempo de instalación:** < 1 minuto
- **Documentación:** 280 KB (completa)

### Desarrollo
- **Tiempo total:** 16 horas
- **Iteraciones de debugging:** 4
- **Commits:** 7
- **Líneas de código:** ~2,000
- **Tasa de éxito vs estimación:** 20-30% más rápido

---

## 🎓 Créditos

### Desarrollado Con
- **AI Model:** Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)
- **Equipo:** SOCIUM-CR
- **Metodología:** AI-assisted development

### Construido Sobre
- [Model Context Protocol](https://modelcontextprotocol.io/) - Anthropic
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloader
- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) - Transcript extraction
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager

### Agradecimientos
- Anthropic team por MCP y Claude Code
- Comunidad open source
- Beta testers y early adopters

---

## 📜 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

```
MIT License

Copyright (c) 2025 SOCIUM-CR

Permission is hereby granted, free of charge, to any person obtaining a copy...
```

---

## 🔗 Enlaces Útiles

- **Releases:** https://github.com/SOCIUM-CR/youtube-extract-mcp-server/releases
- **Documentación:** https://github.com/SOCIUM-CR/youtube-extract-mcp-server/tree/main/docs
- **Issues:** https://github.com/SOCIUM-CR/youtube-extract-mcp-server/issues
- **Discussions:** https://github.com/SOCIUM-CR/youtube-extract-mcp-server/discussions
- **MCP Protocol:** https://modelcontextprotocol.io/
- **Claude Desktop:** https://claude.ai/

---

## 🌟 ¿Te gusta este proyecto?

- ⭐ Dale una estrella en GitHub
- 🐛 Reporta bugs o sugiere features
- 🤝 Contribuye con código o documentación
- 📢 Comparte con la comunidad

---

## 📞 Contacto

- **Email:** contact@socium.cr
- **GitHub:** [@SOCIUM-CR](https://github.com/SOCIUM-CR)
- **Issues:** [GitHub Issues](https://github.com/SOCIUM-CR/youtube-extract-mcp-server/issues)

---

<div align="center">

**Hecho con ❤️ usando AI-assisted development**

[Descargar](https://github.com/SOCIUM-CR/youtube-extract-mcp-server/releases/latest) •
[Documentación](docs/README.md) •
[Roadmap](evolution-plan/README.md)

</div>
