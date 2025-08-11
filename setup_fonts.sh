#!/bin/bash
# Setup IPA Gothic font for P4Mgr

set -e

echo "=== IPA Gothic Font Setup Script ==="
echo

# Create fonts directory if it doesn't exist
FONTS_DIR="fonts"
if [ ! -d "$FONTS_DIR" ]; then
    echo "Creating fonts directory..."
    mkdir -p "$FONTS_DIR"
fi

# Define URLs and paths
FONT_URL="https://moji.or.jp/wp-content/ipafont/IPAfont/IPAfont00303.zip"
ZIP_FILE="IPAfont00303.zip"
TEMP_DIR="temp_font_extract"

# Download the font zip file
echo "Downloading IPA font package..."
if command -v wget &> /dev/null; then
    wget -O "$ZIP_FILE" "$FONT_URL"
elif command -v curl &> /dev/null; then
    curl -L -o "$ZIP_FILE" "$FONT_URL"
else
    echo "Error: Neither wget nor curl is installed. Please install one of them."
    exit 1
fi

# Create temporary extraction directory
mkdir -p "$TEMP_DIR"

# Extract the zip file
echo "Extracting font files..."
unzip -q "$ZIP_FILE" -d "$TEMP_DIR"

# Find and copy ipag.ttf
echo "Copying ipag.ttf to fonts directory..."
IPAG_FILE=$(find "$TEMP_DIR" -name "ipag.ttf" -type f | head -n 1)

if [ -z "$IPAG_FILE" ]; then
    echo "Error: ipag.ttf not found in the archive"
    # List contents to help debug
    echo "Archive contents:"
    find "$TEMP_DIR" -name "*.ttf" -type f
    exit 1
fi

cp "$IPAG_FILE" "$FONTS_DIR/ipag.ttf"
echo "Successfully copied ipag.ttf to $FONTS_DIR/"

# Clean up
echo "Cleaning up temporary files..."
rm -rf "$TEMP_DIR"
rm -f "$ZIP_FILE"

echo
echo "=== Font setup completed successfully! ==="
echo "IPA Gothic font is now available at: $FONTS_DIR/ipag.ttf"

# Set appropriate permissions
chmod 644 "$FONTS_DIR/ipag.ttf"

echo
echo "You can now run P4Mgr with Japanese font support."