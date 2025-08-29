#!/usr/bin/env python3
"""
Test script for Voyage AI Embeddings System
Verifies basic functionality without requiring API calls
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing module imports...")
    
    try:
        import numpy as np
        print("  ✓ numpy imported successfully")
    except ImportError as e:
        print(f"  ✗ numpy import failed: {e}")
        return False
    
    try:
        import sklearn
        print("  ✓ scikit-learn imported successfully")
    except ImportError as e:
        print(f"  ✗ scikit-learn import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("  ✓ pandas imported successfully")
    except ImportError as e:
        print(f"  ✗ pandas import failed: {e}")
        return False
    
    try:
        import requests
        print("  ✓ requests imported successfully")
    except ImportError as e:
        print(f"  ✗ requests import failed: {e}")
        return False
    
    return True

def test_file_structure():
    """Test if all required files exist"""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        "voyage_extractor.py",
        "ai_content_analyzer.py", 
        "config.yaml",
        "requirements.txt",
        "README.md"
    ]
    
    all_exist = True
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"  ✓ {file_name} exists")
        else:
            print(f"  ✗ {file_name} missing")
            all_exist = False
    
    return all_exist

def test_config_parsing():
    """Test if configuration file can be parsed"""
    print("\n🔍 Testing configuration parsing...")
    
    try:
        import yaml
        print("  ✓ PyYAML available")
        
        with open("config.yaml", 'r') as f:
            config = yaml.safe_load(f)
        
        required_keys = ['voyage_ai', 'extraction', 'analysis', 'ai_keywords', 'output']
        for key in required_keys:
            if key in config:
                print(f"  ✓ {key} configuration section found")
            else:
                print(f"  ✗ {key} configuration section missing")
                return False
        
        print("  ✓ Configuration file parsed successfully")
        return True
        
    except ImportError:
        print("  ⚠ PyYAML not available (optional)")
        return True
    except Exception as e:
        print(f"  ✗ Configuration parsing failed: {e}")
        return False

def test_code_syntax():
    """Test if Python files have valid syntax"""
    print("\n🔍 Testing code syntax...")
    
    python_files = ["voyage_extractor.py", "ai_content_analyzer.py"]
    
    for file_name in python_files:
        try:
            with open(file_name, 'r') as f:
                compile(f.read(), file_name, 'exec')
            print(f"  ✓ {file_name} syntax is valid")
        except SyntaxError as e:
            print(f"  ✗ {file_name} syntax error: {e}")
            return False
        except Exception as e:
            print(f"  ✗ {file_name} error: {e}")
            return False
    
    return True

def test_api_key_environment():
    """Test if Voyage AI API key environment variable is set"""
    print("\n🔍 Testing API key environment...")
    
    api_key = os.getenv('VOYAGE_API_KEY')
    if api_key:
        print(f"  ✓ VOYAGE_API_KEY is set (length: {len(api_key)})")
        return True
    else:
        print("  ⚠ VOYAGE_API_KEY not set")
        print("  To set it, run: export VOYAGE_API_KEY='your-api-key-here'")
        return False

def test_university_profiles_access():
    """Test if university profiles directory is accessible"""
    print("\n🔍 Testing university profiles access...")
    
    profiles_dir = Path("../docs/university-profiles")
    if profiles_dir.exists():
        markdown_files = list(profiles_dir.glob("*.md"))
        print(f"  ✓ University profiles directory accessible")
        print(f"  ✓ Found {len(markdown_files)} markdown files")
        return True
    else:
        print("  ✗ University profiles directory not found")
        print(f"  Expected path: {profiles_dir.absolute()}")
        return False

def main():
    """Run all tests"""
    print("🚀 Voyage AI Embeddings System - System Test")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("File Structure", test_file_structure),
        ("Configuration", test_config_parsing),
        ("Code Syntax", test_code_syntax),
        ("API Key Environment", test_api_key_environment),
        ("University Profiles Access", test_university_profiles_access)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ✗ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Set your Voyage AI API key: export VOYAGE_API_KEY='your-key'")
        print("2. Run basic analysis: python voyage_extractor.py")
        print("3. Run AI analysis: python ai_content_analyzer.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above before proceeding.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
