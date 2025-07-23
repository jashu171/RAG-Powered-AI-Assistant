#!/usr/bin/env python3
"""
Check if required imports are working
"""

import sys
print(f"Python executable: {sys.executable}")
print(f"Virtual environment: {sys.prefix}")

print("\nTesting imports:")

try:
    import PyPDF2
    print("✅ PyPDF2 imported successfully")
except ImportError as e:
    print(f"❌ PyPDF2 import failed: {e}")

try:
    from docx import Document
    print("✅ python-docx imported successfully")
except ImportError as e:
    print(f"❌ python-docx import failed: {e}")

try:
    from pptx import Presentation
    print("✅ python-pptx imported successfully")
except ImportError as e:
    print(f"❌ python-pptx import failed: {e}")

try:
    import pandas as pd
    print("✅ pandas imported successfully")
except ImportError as e:
    print(f"❌ pandas import failed: {e}")

print("\nInstalled packages:")
import subprocess
result = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
print(result.stdout)