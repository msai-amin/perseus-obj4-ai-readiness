#!/bin/bash

echo "UML Diagram Image Generator"
echo "=========================="
echo ""

# Check if HTML files exist
echo "Checking for HTML files..."
if [ -f "knowledge_graph_uml_diagram.html" ]; then
    echo "✓ knowledge_graph_uml_diagram.html found"
else
    echo "✗ knowledge_graph_uml_diagram.html not found"
fi

if [ -f "simplified_uml_diagram.html" ]; then
    echo "✓ simplified_uml_diagram.html found"
else
    echo "✗ simplified_uml_diagram.html not found"
fi

if [ -f "technology_focused_uml_diagram.html" ]; then
    echo "✓ technology_focused_uml_diagram.html found"
else
    echo "✗ technology_focused_uml_diagram.html not found"
fi

echo ""
echo "Image Generation Methods:"
echo "========================"
echo ""

echo "Method 1: Python Scripts"
echo "------------------------"
echo "1. Install dependencies:"
echo "   pip install selenium"
echo "   # Also install Chrome and ChromeDriver"
echo ""
echo "2. Run the Python script:"
echo "   python generate_uml_images.py"
echo "   # or"
echo "   python generate_uml_images_simple.py"
echo ""

echo "Method 2: Manual Browser Screenshots"
echo "-----------------------------------"
echo "1. Open each HTML file in your web browser:"
echo "   - knowledge_graph_uml_diagram.html"
echo "   - simplified_uml_diagram.html"
echo "   - technology_focused_uml_diagram.html"
echo ""
echo "2. Wait for the diagrams to render completely"
echo ""
echo "3. Take screenshots:"
echo "   - Use browser's built-in screenshot feature"
echo "   - Or use system screenshot tools"
echo "   - Focus on the diagram container area"
echo ""

echo "Method 3: Browser Developer Tools"
echo "--------------------------------"
echo "1. Open HTML file in Chrome/Firefox"
echo "2. Right-click on diagram → Inspect Element"
echo "3. Find the .diagram-container element"
echo "4. Right-click → Screenshot element"
echo ""

echo "Method 4: Print to PDF"
echo "---------------------"
echo "1. Open HTML file in browser"
echo "2. Press Ctrl+P (Cmd+P on Mac)"
echo "3. Select 'Save as PDF'"
echo "4. Save with descriptive name"
echo ""

echo "Method 5: Online Mermaid Editor"
echo "------------------------------"
echo "1. Go to https://mermaid.live/"
echo "2. Copy Mermaid code from HTML files"
echo "3. Export as PNG/SVG/PDF"
echo ""

# Create output directory
mkdir -p uml_images

echo "Expected Output Files:"
echo "====================="
echo "- uml_images/complete_uml_model.png"
echo "- uml_images/simplified_uml_model.png"
echo "- uml_images/technology_focused_uml_model.png"
echo ""

echo "Quick Start (Manual Method):"
echo "==========================="
echo "1. Open knowledge_graph_uml_diagram.html in your browser"
echo "2. Wait for the diagram to load"
echo "3. Take a screenshot of the diagram area"
echo "4. Save as 'uml_images/complete_uml_model.png'"
echo "5. Repeat for other HTML files"
echo ""

echo "Troubleshooting:"
echo "==============="
echo "- If diagrams don't render, check browser console for errors"
echo "- Ensure JavaScript is enabled in your browser"
echo "- Try different browsers (Chrome, Firefox, Safari)"
echo "- Check that Mermaid.js CDN is accessible"
echo ""

echo "For automated generation, try:"
echo "python generate_uml_images.py"
echo "or"
echo "python generate_uml_images_simple.py" 