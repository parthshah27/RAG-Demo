#!/usr/bin/env python3
"""
🚀 Hackathon Quick-Start Script
Setup and switch between ANY domain in seconds
"""

import json
import argparse
import os
import sys
from pathlib import Path
import shutil
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / ".chroma"

def create_quick_config(domain_name: str, description: str = None):
    """Create a config file for a new domain in seconds"""
    config = {
        "domain": domain_name.lower(),
        "title": f"🤖 {domain_name} Assistant",
        "description": description or f"AI-powered {domain_name} data analyst",
        "system_prompt": f"You are an expert {domain_name} data analyst. Use the provided data to answer questions accurately and suggest actionable insights.",
        "query_enhancement_prompt": f"The user is asking about {domain_name} data. Provide specific, relevant insights based on the context.",
        "data_paths": [
            "data/*.csv",
            "data/**/*.csv"
        ],
        "demo_responses": {
            "analysis": f"I can analyze {domain_name} data for you. Upload your CSV files to data/ folder and ask specific questions.",
            "help": f"I'm ready to help with {domain_name} analysis. What would you like to know?",
            "data": f"Please provide {domain_name} data in CSV format in the data/ folder."
        }
    }
    
    config_file = CONFIG_DIR / f"config.{domain_name.lower()}.json"
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Created config: config/{config_file.name}")
    return config_file

def list_domains():
    """List all available domain configs"""
    configs = sorted(CONFIG_DIR.glob("config.*.json"))
    
    if not configs:
        print("❌ No domain configs found!")
        return
    
    print("\n" + "="*60)
    print("📚 AVAILABLE DOMAINS")
    print("="*60)
    
    for config_file in configs:
        domain = config_file.stem.replace("config.", "")
        try:
            with open(config_file) as f:
                data = json.load(f)
                print(f"\n🔹 {domain.upper()}")
                print(f"   Title: {data.get('title', 'N/A')}")
                print(f"   Desc:  {data.get('description', 'N/A')}")
        except:
            print(f"   ❌ Error reading {config_file.name}")

def switch_domain(domain_name: str, keep_data: bool = False):
    """Switch to a different domain and reset ChromaDB"""
    config_file = CONFIG_DIR / f"config.{domain_name.lower()}.json"
    
    if not config_file.exists():
        print(f"❌ Domain '{domain_name}' not found!")
        print(f"   Expected: config/{config_file.name}")
        list_domains()
        return False
    
    # Reset ChromaDB
    if CHROMA_DIR.exists() and not keep_data:
        print(f"🗑️  Clearing ChromaDB cache...")
        shutil.rmtree(CHROMA_DIR)
        CHROMA_DIR.mkdir(exist_ok=True)
    
    # Set environment variable
    env_file = BASE_DIR / ".env"
    update_env_var(env_file, "CONFIG_FILE", f"config.{domain_name.lower()}.json")
    
    print(f"✅ Switched to domain: {domain_name.upper()}")
    print(f"   Config: config/{config_file.name}")
    print(f"   Set CONFIG_FILE in .env")
    
    # Show next steps
    print(f"\n📋 Next steps:")
    print(f"   1. Place your {domain_name} data in data/ folder (CSV format)")
    print(f"   2. Set DEMO_MODE=False in .env (if using OpenAI API)")
    print(f"   3. Run: python -m uvicorn app.main:app --reload")
    print(f"   4. Frontend: npm start\n")

def update_env_var(env_file: Path, key: str, value: str):
    """Update or add an environment variable"""
    lines = []
    found = False
    
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                if line.startswith(f"{key}="):
                    lines.append(f"{key}={value}\n")
                    found = True
                else:
                    lines.append(line)
    
    if not found:
        lines.append(f"{key}={value}\n")
    
    with open(env_file, "w") as f:
        f.writelines(lines)

def generate_quick_data(domain_name: str, rows: int = 100):
    """Generate synthetic data for quick testing"""
    print(f"\n🔄 Generating {rows} sample {domain_name} records...")
    
    from generate_synthetic_data import (
        generate_manufacturing_data, 
        generate_retail_data, 
        generate_healthcare_data
    )
    
    domain_lower = domain_name.lower()
    
    try:
        if domain_lower == "manufacturing":
            df = generate_manufacturing_data(rows)
        elif domain_lower == "retail":
            df = generate_retail_data(rows)
        elif domain_lower == "healthcare":
            df = generate_healthcare_data(rows)
        else:
            print(f"⚠️  No generator for '{domain_name}' - skipping synthetic data")
            return
        
        output_file = DATA_DIR / f"{domain_lower}_data.csv"
        df.to_csv(output_file, index=False)
        print(f"✅ Generated: data/{output_file.name}")
        print(f"   {len(df)} records with {len(df.columns)} columns")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def summary():
    """Show system ready status"""
    print("\n" + "="*60)
    print("📊 SYSTEM STATUS")
    print("="*60)
    
    # Check configs
    configs = list(CONFIG_DIR.glob("config.*.json"))
    print(f"✅ Domains configured: {len(configs)}")
    
    # Check data
    data_files = list(DATA_DIR.glob("**/*.csv"))
    print(f"✅ Data files: {len(data_files)}")
    
    # Check ChromaDB
    if CHROMA_DIR.exists() and list(CHROMA_DIR.glob("**/*")):
        print(f"✅ ChromaDB cache: Active ({len(list(CHROMA_DIR.glob('**/*')))} items)")
    else:
        print(f"⚠️  ChromaDB cache: Empty (will index on first query)")
    
    # Check env
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        with open(env_file) as f:
            content = f.read()
            if "OPENAI_API_KEY" in content and "sk-" in content:
                print(f"✅ OpenAI API key configured")
            else:
                print(f"⚠️  OpenAI API key missing (set DEMO_MODE=True for testing)")
    
    print("="*60 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description="🚀 Hackathon Quick-Start - Switch domains in seconds",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
USAGE EXAMPLES:
  # List all domains
  python quickstart.py --list

  # Switch to manufacturing domain
  python quickstart.py --switch manufacturing

  # Create a new domain
  python quickstart.py --create "supply_chain" --desc "Supply chain optimization"

  # Generate sample data and switch
  python quickstart.py --switch retail --generate 500

  # Show system status
  python quickstart.py --status
        """
    )
    
    parser.add_argument("--list", action="store_true", help="List available domains")
    parser.add_argument("--switch", metavar="DOMAIN", help="Switch to a domain")
    parser.add_argument("--create", metavar="DOMAIN", help="Create new domain config")
    parser.add_argument("--desc", metavar="DESC", help="Description for new domain")
    parser.add_argument("--generate", metavar="NUM", type=int, help="Generate sample data (rows)")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--keep-data", action="store_true", help="Keep ChromaDB when switching (faster)")
    
    args = parser.parse_args()
    
    if args.list:
        list_domains()
    
    elif args.status:
        summary()
    
    elif args.create:
        create_quick_config(args.create, args.desc)
        if args.generate:
            generate_quick_data(args.create, args.generate)
    
    elif args.switch:
        switch_domain(args.switch, args.keep_data)
        if args.generate:
            generate_quick_data(args.switch, args.generate)
        summary()
    
    else:
        # Default: show status
        summary()
        print("💡 Quick start guide:")
        print("   python quickstart.py --list           # See available domains")
        print("   python quickstart.py --switch DOMAIN  # Switch domains fast")
        print("   python quickstart.py --create DOMAIN  # Create new domain")
        print("   python quickstart.py --status         # Check system status\n")

if __name__ == "__main__":
    main()