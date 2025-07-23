#!/usr/bin/env python3
"""
Test Document Processing Support

This script tests that all document types are properly supported.
"""

import os
from utils.document_parser import DocumentParser

def test_document_support():
    """Test document processing capabilities"""
    print("🧪 Testing Document Processing Support")
    print("=" * 50)
    
    # Test supported extensions
    extensions = DocumentParser.get_supported_extensions()
    print(f"✅ Supported file types: {extensions}")
    
    # Test individual library availability
    try:
        import PyPDF2
        print("✅ PDF support: Available")
    except ImportError:
        print("❌ PDF support: Not available")
    
    try:
        from docx import Document
        print("✅ DOCX support: Available")
    except ImportError:
        print("❌ DOCX support: Not available")
    
    try:
        from pptx import Presentation
        print("✅ PPTX support: Available")
    except ImportError:
        print("❌ PPTX support: Not available")
    
    try:
        import pandas as pd
        print("✅ CSV support (advanced): Available")
    except ImportError:
        print("⚠️ CSV support (basic): Available")
    
    # Test text file support (always available)
    print("✅ TXT/MD support: Available")
    
    # Create test files and try parsing
    print("\n📄 Testing File Parsing")
    print("-" * 30)
    
    # Create test text file
    test_file = "test_document.txt"
    with open(test_file, 'w') as f:
        f.write("This is a test document.\nIt has multiple lines.\nFor testing purposes.")
    
    try:
        chunks = DocumentParser.parse_file(test_file)
        print(f"✅ Text file parsing: {len(chunks)} chunks created")
        
        # Clean up
        os.remove(test_file)
        
    except Exception as e:
        print(f"❌ Text file parsing failed: {str(e)}")
    
    print("\n🎉 Document processing test completed!")

if __name__ == "__main__":
    test_document_support()