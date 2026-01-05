#!/bin/bash

# Image Optimization Script
# Converts images to WebP format with quality optimization

echo "🖼️  Starting image optimization..."

# Check if cwebp is installed
if ! command -v cwebp &> /dev/null; then
    echo "❌ cwebp not found. Installing..."

    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install webp
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update
        sudo apt-get install -y webp
    else
        echo "❌ Unsupported OS. Please install webp manually."
        exit 1
    fi
fi

# Find and convert images
IMAGES_DIR="${1:-.}"
OUTPUT_DIR="${2:-$IMAGES_DIR}"

echo "📂 Scanning directory: $IMAGES_DIR"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Counter for stats
TOTAL=0
CONVERTED=0
SAVINGS=0

# Convert PNG images
for img in "$IMAGES_DIR"/*.png; do
    if [ -f "$img" ]; then
        filename=$(basename "$img" .png)
        output="$OUTPUT_DIR/$filename.webp"

        echo "Converting: $img → $output"

        # Get original size
        original_size=$(wc -c < "$img")

        # Convert with quality 85 (good balance)
        cwebp -q 85 "$img" -o "$output" 2>&1 | grep -v "^Saving"

        if [ -f "$output" ]; then
            # Get new size
            new_size=$(wc -c < "$output")
            saved=$((original_size - new_size))
            percent=$((100 - (new_size * 100 / original_size)))

            echo "  ✅ Saved: $saved bytes ($percent% reduction)"

            CONVERTED=$((CONVERTED + 1))
            SAVINGS=$((SAVINGS + saved))
        fi

        TOTAL=$((TOTAL + 1))
    fi
done

# Convert JPG images
for img in "$IMAGES_DIR"/*.jpg "$IMAGES_DIR"/*.jpeg; do
    if [ -f "$img" ]; then
        filename=$(basename "$img")
        filename="${filename%.*}"
        output="$OUTPUT_DIR/$filename.webp"

        echo "Converting: $img → $output"

        original_size=$(wc -c < "$img")
        cwebp -q 85 "$img" -o "$output" 2>&1 | grep -v "^Saving"

        if [ -f "$output" ]; then
            new_size=$(wc -c < "$output")
            saved=$((original_size - new_size))
            percent=$((100 - (new_size * 100 / original_size)))

            echo "  ✅ Saved: $saved bytes ($percent% reduction)"

            CONVERTED=$((CONVERTED + 1))
            SAVINGS=$((SAVINGS + saved))
        fi

        TOTAL=$((TOTAL + 1))
    fi
done

# Generate summary
echo ""
echo "═══════════════════════════════════════"
echo "📊 Optimization Summary"
echo "═══════════════════════════════════════"
echo "Total images found:    $TOTAL"
echo "Successfully converted: $CONVERTED"
echo "Total space saved:     $((SAVINGS / 1024)) KB"
if [ $TOTAL -gt 0 ]; then
    avg_reduction=$((SAVINGS * 100 / (TOTAL * 1024)))
    echo "Average reduction:     ~${avg_reduction}%"
fi
echo "═══════════════════════════════════════"
echo ""
echo "✅ Image optimization complete!"
echo ""
echo "💡 Next steps:"
echo "1. Update HTML to use .webp images"
echo "2. Keep original images as fallback"
echo "3. Test in different browsers"
