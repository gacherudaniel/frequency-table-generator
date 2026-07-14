#!/bin/bash
# Quick packaging script for distribution

echo "=================================================="
echo "Frequency Table Generator - Package for Distribution"
echo "=================================================="
echo ""

# Create release directory
RELEASE_DIR="FrequencyTableGenerator_v1.0_$(uname -m)"
echo "Creating release package: $RELEASE_DIR"

mkdir -p "$RELEASE_DIR"

# Copy executable
echo "✓ Copying executable..."
cp dist/FrequencyTableGenerator "$RELEASE_DIR/"

# Copy documentation
echo "✓ Copying documentation..."
cp USER_GUIDE.md "$RELEASE_DIR/"
cp dist/README.txt "$RELEASE_DIR/"

# Create launcher script
echo "✓ Creating launcher script..."
cat > "$RELEASE_DIR/run.sh" << 'EOF'
#!/bin/bash
# Frequency Table Generator Launcher
cd "$(dirname "$0")"

# Make sure executable has permission
chmod +x FrequencyTableGenerator

# Run the application
./FrequencyTableGenerator
EOF

chmod +x "$RELEASE_DIR/run.sh"

# Create archive
ARCHIVE_NAME="${RELEASE_DIR}.tar.gz"
echo "✓ Creating archive: $ARCHIVE_NAME"
tar -czf "$ARCHIVE_NAME" "$RELEASE_DIR/"

echo ""
echo "=================================================="
echo "✅ Package created successfully!"
echo "=================================================="
echo ""
echo "Distribution package: $ARCHIVE_NAME"
echo "Size: $(du -h "$ARCHIVE_NAME" | cut -f1)"
echo ""
echo "To share with users:"
echo "  1. Send them: $ARCHIVE_NAME"
echo "  2. Users extract with: tar -xzf $ARCHIVE_NAME"
echo "  3. Users run with: cd $RELEASE_DIR && ./run.sh"
echo ""
echo "Or they can run the executable directly:"
echo "  ./FrequencyTableGenerator"
echo ""
echo "=================================================="
