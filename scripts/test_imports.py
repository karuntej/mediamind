#!/usr/bin/env python3
"""
Test script to verify that imports from src work correctly
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_imports():
    """Test importing from src module"""
    try:
        print("🔧 Testing imports from src module...")
        
        # Test importing from src.storage
        from src.storage import list_pdfs, download_pdf, presigned_url
        print("✅ Successfully imported from src.storage")
        
        # Test the functions
        pdfs = list(list_pdfs())
        print(f"📄 Found {len(pdfs)} PDFs in storage")
        
        if pdfs:
            print("   PDF keys:")
            for pdf in pdfs[:3]:  # Show first 3
                print(f"   - {pdf}")
        
        print("🎉 All imports working correctly!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n💡 Make sure you're running with PYTHONPATH=.")
        print("   Example: PYTHONPATH=. python scripts/test_imports.py")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_imports() 