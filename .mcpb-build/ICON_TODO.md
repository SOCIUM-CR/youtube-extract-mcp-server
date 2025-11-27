# Icon Creation TODO

## Required

The `.mcpb` package requires a PNG icon with the following specifications:
- **Format:** PNG
- **Dimensions:** 128x128 pixels
- **File name:** `icon.png`

## Current Status

✅ SVG design created (`icon.svg`)
⏳ PNG conversion pending (requires external tool)

## Design Concept

The icon represents:
- **Red background** - YouTube brand color (#FF0000)
- **White circle** - Play button background
- **Red triangle** - YouTube play button
- **Document icon** (bottom right) - Transcription output
- **Arrow** - Video → Transcript transformation

## How to Convert

### Option 1: Using ImageMagick
```bash
cd .mcpb-build
convert icon.svg -resize 128x128 icon.png
```

### Option 2: Using Inkscape
```bash
inkscape icon.svg --export-type=png --export-width=128 --export-height=128 --export-filename=icon.png
```

### Option 3: Using Online Tool
1. Go to https://cloudconvert.com/svg-to-png
2. Upload `icon.svg`
3. Set dimensions to 128x128
4. Download as `icon.png`

### Option 4: Using Figma/Design Tool
1. Open `icon.svg` in Figma
2. Export as PNG at 128x128
3. Save as `icon.png`

## Temporary Workaround

For testing purposes, you can use a simple colored rectangle:
```bash
python3 -c "from PIL import Image; img = Image.new('RGB', (128, 128), '#FF0000'); img.save('icon.png')"
```

Or create manually with any image editor at 128x128 pixels.
