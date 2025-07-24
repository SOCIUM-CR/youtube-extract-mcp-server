# YouTube Extract MCP Server (Servidor MCP para Extracción de YouTube)

Un servidor MCP de Python autocontenido para la extracción robusta de transcripciones de YouTube, gestionado con `uv`.

## Características

- **Detección automática de idioma**
- **Persistencia de archivos locales**
- **Configuración global**
- **Formatos de transcripción duales** (texto plano y con marcas de tiempo)
- **Procesamiento de listas de reproducción**

## Prerrequisitos

- **uv**: Un gestor de paquetes de Python rápido. Si no lo tienes, instálalo según tu sistema operativo:

  **macOS / Linux:**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

  **Windows (usando PowerShell):**
  ```powershell
  irm https://astral.sh/uv/install.ps1 | iex
  ```

## Instalación

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/SOCIUM-CR/youtube-extract-mcp-server.git
    cd youtube-extract-mcp-server
    ```

2.  **Instala las dependencias (opcional):**
    `uv` instalará las dependencias automáticamente al ejecutar el script. Si deseas instalarlas manualmente, puedes hacerlo con:
    ```bash
    uv pip install -r requirements.txt
    ```

## Configuración para Claude Desktop

1.  Encuentra tu archivo de configuración de Claude Desktop:

    **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
    **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
    **Linux:** `~/.config/Claude/claude_desktop_config.json`

2.  Agrega esta configuración de servidor. **Es crucial** que reemplaces las rutas de ejemplo con las **rutas absolutas** en tu sistema.

    ```json
    {
      "mcpServers": {
        "youtube-extract-mlx": {
          "command": "/ruta/absoluta/a/tu/uv",
          "args": [
            "--directory",
            "/ruta/absoluta/al/proyecto/",
            "run",
            "youtube_extract_mcp.py"
          ],
          "cwd": "/ruta/absoluta/al/proyecto/"
        }
      }
    }
    ```

    *   `command`: La ruta absoluta a tu ejecutable `uv`. Puedes encontrarla ejecutando `which uv` en tu terminal.
    *   `args`: El primer argumento (`--directory`) debe ser la ruta absoluta a la carpeta de este proyecto. El resto de argumentos no deben ser modificados.
    *   `cwd`: El directorio de trabajo, que debe ser la misma ruta absoluta a la carpeta de este proyecto.

3.  Reinicia Claude Desktop para que los cambios surtan efecto.

## Uso

### Herramientas Disponibles

- `youtube_extract_video`: Extrae los metadatos y la transcripción de un video.
- `configure_output_directory`: Establece el directorio local donde se guardarán las transcripciones.
- `show_current_config`: Muestra la configuración global actual.
- `youtube_extract_playlist`: Extrae las transcripciones de una lista de reproducción completa de YouTube.

### Ejemplo

```bash
# 1. Configura un directorio para guardar las transcripciones
configure_output_directory ~/MisTranscripciones

# 2. Extrae un video y guárdalo localmente
youtube_extract_video url="https://www.youtube.com/watch?v=dQw4w9WgXcQ" save_locally=true

# 3. Extrae una lista de reproducción completa
youtube_extract_playlist playlist_url="https://www.youtube.com/playlist?list=PL-osiE80TeTucQ0nA_cItCgpcin0U-unE"
```

## Licencia

Este proyecto está bajo la Licencia MIT.
