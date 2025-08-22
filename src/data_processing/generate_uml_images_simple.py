#!/usr/bin/env python3
"""
Simple UML Diagram Image Generator
Alternative approach using different libraries for generating PNG images.
"""

import os
import subprocess
import sys

def check_puppeteer():
    """Check if Puppeteer is available for screenshot generation."""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Node.js is available")
            return True
        else:
            print("✗ Node.js not found")
            return False
    except FileNotFoundError:
        print("✗ Node.js not found")
        return False

def create_puppeteer_script():
    """Create a Node.js script to generate screenshots using Puppeteer."""
    script_content = '''
const puppeteer = require('puppeteer');
const path = require('path');

async function generateScreenshots() {
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 2 });
    
    const htmlFiles = [
        'knowledge_graph_uml_diagram.html',
        'simplified_uml_diagram.html', 
        'technology_focused_uml_diagram.html'
    ];
    
    const outputDir = 'uml_images';
    
    for (const htmlFile of htmlFiles) {
        if (require('fs').existsSync(htmlFile)) {
            console.log(`Processing ${htmlFile}...`);
            
            const filePath = path.resolve(htmlFile);
            await page.goto(`file://${filePath}`, { waitUntil: 'networkidle0' });
            
            // Wait for Mermaid to render
            await page.waitForSelector('.mermaid', { timeout: 30000 });
            await page.waitForTimeout(3000); // Additional wait for rendering
            
            // Find diagram container and take screenshot
            const diagramElement = await page.$('.diagram-container');
            if (diagramElement) {
                const outputPath = path.join(outputDir, htmlFile.replace('.html', '.png'));
                await diagramElement.screenshot({ path: outputPath });
                console.log(`Generated: ${outputPath}`);
            } else {
                console.log(`No diagram container found in ${htmlFile}`);
            }
        } else {
            console.log(`File not found: ${htmlFile}`);
        }
    }
    
    await browser.close();
    console.log('Screenshot generation complete!');
}

generateScreenshots().catch(console.error);
'''
    
    with open('generate_screenshots.js', 'w') as f:
        f.write(script_content)
    
    return 'generate_screenshots.js'

def install_puppeteer():
    """Install Puppeteer if not already installed."""
    try:
        # Check if puppeteer is installed
        result = subprocess.run(['node', '-e', "require('puppeteer')"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Puppeteer is already installed")
            return True
        else:
            print("Installing Puppeteer...")
            subprocess.run(['npm', 'install', 'puppeteer'], check=True)
            print("✓ Puppeteer installed successfully")
            return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install Puppeteer: {e}")
        return False
    except FileNotFoundError:
        print("✗ npm not found. Please install Node.js and npm.")
        return False

def generate_images_with_puppeteer():
    """Generate images using Puppeteer."""
    print("Setting up Puppeteer for screenshot generation...")
    
    # Install Puppeteer if needed
    if not install_puppeteer():
        return False
    
    # Create output directory
    os.makedirs('uml_images', exist_ok=True)
    
    # Create the Node.js script
    script_file = create_puppeteer_script()
    
    try:
        # Run the script
        print("Generating screenshots...")
        subprocess.run(['node', script_file], check=True)
        
        # Clean up the script file
        os.remove(script_file)
        
        print("\n✓ Screenshots generated successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error generating screenshots: {e}")
        return False

def create_manual_instructions():
    """Create manual instructions for generating images."""
    instructions = """
MANUAL IMAGE GENERATION INSTRUCTIONS
====================================

If the automated script doesn't work, you can generate the PNG images manually:

Method 1: Browser Screenshot
1. Open each HTML file in a web browser:
   - knowledge_graph_uml_diagram.html
   - simplified_uml_diagram.html
   - technology_focused_uml_diagram.html

2. Wait for the diagrams to render completely

3. Take screenshots of the diagram containers:
   - Right-click on the diagram area
   - Select "Inspect Element" to identify the diagram container
   - Use browser developer tools to take element screenshots
   - Or use browser's built-in screenshot functionality

Method 2: Browser Print to PDF
1. Open each HTML file in Chrome/Firefox
2. Press Ctrl+P (Cmd+P on Mac) to open print dialog
3. Select "Save as PDF" or "Print to PDF"
4. Save with descriptive names

Method 3: Online Mermaid Editor
1. Go to https://mermaid.live/
2. Copy the Mermaid code from the HTML files
3. Export as PNG/SVG/PDF

Expected Output Files:
- complete_uml_model.png
- simplified_uml_model.png
- technology_focused_uml_model.png

"""
    
    with open('manual_image_generation.txt', 'w') as f:
        f.write(instructions)
    
    print("Manual instructions saved to: manual_image_generation.txt")

def main():
    """Main function to generate UML diagram images."""
    print("UML Diagram Image Generator")
    print("=" * 40)
    
    # Check if Node.js is available
    if check_puppeteer():
        print("\nAttempting to generate images with Puppeteer...")
        if generate_images_with_puppeteer():
            print("\n✓ Images generated successfully!")
            print("\nGenerated files:")
            print("- uml_images/complete_uml_model.png")
            print("- uml_images/simplified_uml_model.png")
            print("- uml_images/technology_focused_uml_model.png")
            return
        else:
            print("\n✗ Puppeteer method failed.")
    
    # Fallback to manual instructions
    print("\nAutomated generation failed. Creating manual instructions...")
    create_manual_instructions()
    
    print("\nAlternative approaches:")
    print("1. Use the Selenium script: python generate_uml_images.py")
    print("2. Follow manual instructions: manual_image_generation.txt")
    print("3. Open HTML files directly in browser and take screenshots")

if __name__ == "__main__":
    main() 