#!/usr/bin/env python3
"""
System Health Check - Verify hackathon setup is ready
Run this to ensure everything works before starting
"""

import os
import sys
import json
from pathlib import Path
import subprocess

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

def check_python():
    """Check Python version"""
    version = sys.version_info
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_directories():
    """Check all required directories exist"""
    dirs = {
        'config': BASE_DIR / 'config',
        'data': BASE_DIR / 'data',
        'app': BASE_DIR / 'app',
        'scripts': BASE_DIR / 'scripts',
    }
    
    all_good = True
    for name, path in dirs.items():
        if path.exists():
            print(f"✅ {name}/ exists")
        else:
            print(f"❌ {name}/ missing!")
            all_good = False
    
    return all_good

def check_files():
    """Check critical files exist"""
    files = {
        'requirements.txt': BASE_DIR / 'requirements.txt',
        'app/main.py': BASE_DIR / 'app' / 'main.py',
        'app/rag.py': BASE_DIR / 'app' / 'rag.py',
        '.env.example': BASE_DIR / '.env.example',
        'config/template.json': BASE_DIR / 'config' / 'template.json',
        'scripts/quickstart.py': BASE_DIR / 'scripts' / 'quickstart.py',
    }
    
    all_good = True
    for name, path in files.items():
        if path.exists():
            print(f"✅ {name}")
        else:
            print(f"❌ {name} missing!")
            all_good = False
    
    return all_good

def check_packages():
    """Check required packages are installed"""
    packages = ['fastapi', 'uvicorn', 'openai', 'chromadb', 'pandas', 'dotenv']
    all_good = True
    
    for pkg in packages:
        try:
            __import__(pkg.replace('-', '_'))
            print(f"✅ {pkg}")
        except ImportError:
            print(f"❌ {pkg} - run: pip install -r requirements.txt")
            all_good = False
    
    return all_good

def check_config():
    """Check configuration"""
    config_file = BASE_DIR / 'config' / 'template.json'
    
    try:
        with open(config_file) as f:
            config = json.load(f)
            print(f"✅ Config template loaded")
            return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def check_chromadb():
    """Check ChromaDB setup"""
    chroma_dir = BASE_DIR / '.chroma'
    
    try:
        import chromadb
        print(f"✅ ChromaDB imported")
        
        if chroma_dir.exists():
            items = len(list(chroma_dir.glob('**/*')))
            print(f"✅ ChromaDB cache exists ({items} items)")
        else:
            print(f"⚠️  ChromaDB cache empty (will create on first run)")
        
        return True
    except Exception as e:
        print(f"❌ ChromaDB error: {e}")
        return False

def check_env():
    """Check .env setup"""
    env_file = BASE_DIR / '.env'
    
    if env_file.exists():
        print(f"✅ .env file exists")
        
        # Check for critical vars
        with open(env_file) as f:
            content = f.read()
            
        if 'OPENAI_API_KEY' in content:
            if 'sk-' in content:
                print(f"✅ OpenAI API key configured")
            else:
                print(f"⚠️  OpenAI API key placeholder (update before use)")
        else:
            print(f"⚠️  No OPENAI_API_KEY set")
        
        if 'CONFIG_FILE' in content:
            print(f"✅ CONFIG_FILE variable set")
        else:
            print(f"⚠️  CONFIG_FILE not set (will use default)")
        
        return True
    else:
        print(f"⚠️  .env not found (copy from .env.example)")
        return False

def check_rag_module():
    """Test RAG module loads correctly"""
    try:
        # Set a simple config
        os.environ['CONFIG_FILE'] = 'config/template.json'
        os.environ['DEMO_MODE'] = 'True'
        
        from app.rag import CONFIG, collection, COLLECTION_NAME
        print(f"✅ RAG module loads")
        print(f"   Domain: {CONFIG.get('domain')}")
        print(f"   Collection: {COLLECTION_NAME}")
        return True
    except Exception as e:
        print(f"❌ RAG module error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🏥 HACKATHON SYSTEM HEALTH CHECK")
    print("="*60)
    
    checks = [
        ("Python Version", check_python),
        ("Directories", check_directories),
        ("Critical Files", check_files),
        ("Python Packages", check_packages),
        ("Configuration", check_config),
        ("ChromaDB", check_chromadb),
        ("Environment Setup", check_env),
        ("RAG Module", check_rag_module),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 {name}:")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error during check: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        symbol = "✅" if result else "❌"
        print(f"{symbol} {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🚀 System ready for hackathon! You can now:")
        print("   1. python scripts/quickstart.py --list")
        print("   2. python scripts/quickstart.py --switch your_domain")
        print("   3. python -m uvicorn app.main:app --reload")
    else:
        print("\n⚠️  Fix the issues above before starting!")
        print("   Common fixes:")
        print("   - pip install -r requirements.txt")
        print("   - cp .env.example .env")
        print("   - Edit .env with your OPENAI_API_KEY")
    
    print("="*60 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)