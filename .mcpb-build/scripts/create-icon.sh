#!/bin/bash
#
# Icon Creation Helper Script
# Creates a 128x128 PNG icon for the .mcpb package
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$(dirname "$SCRIPT_DIR")"
ICON_SVG="$BUILD_DIR/icon.svg"
ICON_PNG="$BUILD_DIR/icon.png"

echo "🎨 YouTube Extract MCP - Icon Creation Script"
echo "=============================================="
echo ""

# Check if SVG exists
if [ ! -f "$ICON_SVG" ]; then
    echo "❌ Error: icon.svg not found at $ICON_SVG"
    exit 1
fi

echo "✅ Found SVG: $ICON_SVG"
echo ""

# Try different conversion methods
if command -v convert &> /dev/null; then
    echo "🔧 Using ImageMagick (convert)..."
    convert "$ICON_SVG" -resize 128x128 "$ICON_PNG"
    echo "✅ Icon created with ImageMagick"

elif command -v inkscape &> /dev/null; then
    echo "🔧 Using Inkscape..."
    inkscape "$ICON_SVG" \
        --export-type=png \
        --export-width=128 \
        --export-height=128 \
        --export-filename="$ICON_PNG"
    echo "✅ Icon created with Inkscape"

elif command -v rsvg-convert &> /dev/null; then
    echo "🔧 Using rsvg-convert..."
    rsvg-convert -w 128 -h 128 "$ICON_SVG" -o "$ICON_PNG"
    echo "✅ Icon created with rsvg-convert"

elif command -v python3 &> /dev/null; then
    echo "🔧 Attempting with Python (cairosvg)..."
    python3 -c "
import sys
try:
    import cairosvg
    cairosvg.svg2png(url='$ICON_SVG', write_to='$ICON_PNG', output_width=128, output_height=128)
    print('✅ Icon created with Python cairosvg')
except ImportError:
    print('⚠️  cairosvg not installed')
    print('   Install with: pip install cairosvg')
    sys.exit(1)
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
    "

else
    echo "❌ No suitable SVG converter found!"
    echo ""
    echo "Please install one of:"
    echo "  • ImageMagick:  brew install imagemagick  (macOS)"
    echo "                  apt install imagemagick   (Linux)"
    echo "  • Inkscape:     brew install inkscape     (macOS)"
    echo "                  apt install inkscape      (Linux)"
    echo "  • rsvg:         brew install librsvg      (macOS)"
    echo "                  apt install librsvg2-bin  (Linux)"
    echo "  • cairosvg:     pip install cairosvg      (Python)"
    echo ""
    echo "Alternative: Use online converter"
    echo "  1. Go to https://cloudconvert.com/svg-to-png"
    echo "  2. Upload $ICON_SVG"
    echo "  3. Set size to 128x128"
    echo "  4. Save as $ICON_PNG"
    exit 1
fi

# Verify icon was created
if [ -f "$ICON_PNG" ]; then
    SIZE=$(file "$ICON_PNG" | grep -o '[0-9]* x [0-9]*' | head -1)
    echo ""
    echo "✅ Icon successfully created:"
    echo "   Location: $ICON_PNG"
    echo "   Size: $SIZE"

    # Verify it's 128x128
    if [[ "$SIZE" == "128 x 128" ]]; then
        echo "   ✅ Correct dimensions"
    else
        echo "   ⚠️  Warning: Expected 128 x 128, got $SIZE"
    fi
else
    echo "❌ Icon file was not created"
    exit 1
fi

echo ""
echo "🎉 Icon creation complete!"
