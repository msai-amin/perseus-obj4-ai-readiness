#!/usr/bin/env python3
"""
UML Diagram Image Generator
Generates PNG images from HTML UML diagrams using Selenium and Chrome WebDriver.
"""

import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_chrome_driver():
    """Setup Chrome WebDriver with appropriate options for screenshot generation."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")  # Set window size
    chrome_options.add_argument("--force-device-scale-factor=2")  # High DPI
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up Chrome WebDriver: {e}")
        print("Please ensure Chrome and ChromeDriver are installed.")
        return None

def wait_for_mermaid_rendering(driver, timeout=30):
    """Wait for Mermaid diagrams to render completely."""
    try:
        # Wait for Mermaid to be loaded and diagrams to render
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "mermaid"))
        )
        # Additional wait to ensure rendering is complete
        time.sleep(3)
        return True
    except Exception as e:
        print(f"Error waiting for Mermaid rendering: {e}")
        return False

def generate_png_from_html(html_file, output_file, driver):
    """Generate PNG image from HTML file containing Mermaid diagram."""
    try:
        # Get absolute path to HTML file
        html_path = os.path.abspath(html_file)
        file_url = f"file://{html_path}"
        
        print(f"Loading {html_file}...")
        driver.get(file_url)
        
        # Wait for Mermaid to render
        if not wait_for_mermaid_rendering(driver):
            print(f"Failed to render Mermaid diagram in {html_file}")
            return False
        
        # Find the diagram container
        diagram_element = driver.find_element(By.CLASS_NAME, "diagram-container")
        
        # Take screenshot of the diagram container
        print(f"Generating PNG: {output_file}")
        diagram_element.screenshot(output_file)
        
        print(f"Successfully generated: {output_file}")
        return True
        
    except Exception as e:
        print(f"Error generating PNG from {html_file}: {e}")
        return False

def generate_all_uml_images():
    """Generate PNG images for all UML diagrams."""
    
    # Setup Chrome WebDriver
    driver = setup_chrome_driver()
    if not driver:
        return False
    
    try:
        # Create output directory
        output_dir = "uml_images"
        os.makedirs(output_dir, exist_ok=True)
        
        # List of HTML files to convert
        html_files = [
            ("knowledge_graph_uml_diagram.html", "complete_uml_model.png"),
            ("simplified_uml_diagram.html", "simplified_uml_model.png"),
            ("technology_focused_uml_diagram.html", "technology_focused_uml_model.png")
        ]
        
        success_count = 0
        total_count = len(html_files)
        
        for html_file, png_file in html_files:
            if os.path.exists(html_file):
                output_path = os.path.join(output_dir, png_file)
                if generate_png_from_html(html_file, output_path, driver):
                    success_count += 1
            else:
                print(f"HTML file not found: {html_file}")
        
        print(f"\nGeneration complete: {success_count}/{total_count} images generated successfully")
        print(f"Images saved in: {output_dir}/")
        
        return success_count == total_count
        
    finally:
        driver.quit()

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        from selenium import webdriver
        print("✓ Selenium is installed")
    except ImportError:
        print("✗ Selenium is not installed. Install with: pip install selenium")
        return False
    
    try:
        # Check if Chrome is available
        result = subprocess.run(['google-chrome', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Chrome browser is available")
        else:
            print("✗ Chrome browser not found")
            return False
    except FileNotFoundError:
        print("✗ Chrome browser not found")
        return False
    
    try:
        # Check if ChromeDriver is available
        result = subprocess.run(['chromedriver', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ ChromeDriver is available")
        else:
            print("✗ ChromeDriver not found")
            return False
    except FileNotFoundError:
        print("✗ ChromeDriver not found")
        return False
    
    return True

def main():
    """Main function to generate UML diagram images."""
    print("UML Diagram Image Generator")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("\nPlease install missing dependencies:")
        print("1. Install Selenium: pip install selenium")
        print("2. Install Chrome browser")
        print("3. Install ChromeDriver: https://chromedriver.chromium.org/")
        return
    
    print("\nStarting image generation...")
    
    # Generate images
    success = generate_all_uml_images()
    
    if success:
        print("\n✓ All UML diagram images generated successfully!")
        print("\nGenerated files:")
        print("- uml_images/complete_uml_model.png")
        print("- uml_images/simplified_uml_model.png") 
        print("- uml_images/technology_focused_uml_model.png")
    else:
        print("\n✗ Some images failed to generate. Check the error messages above.")

if __name__ == "__main__":
    main() 