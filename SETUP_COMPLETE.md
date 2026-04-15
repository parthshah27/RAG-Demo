# ✅ HACKATHON SETUP COMPLETE!

Your RAG system is now **fully optimized for 3.5-hour hackathon mode**. Here's what's been set up:

## 🎯 What Changed

### 1. **Persistent ChromaDB (Disk-Based)**
- ✅ Automatic data persistence to `.chroma/` folder
- ✅ **No re-indexing on restart** - instant startup!
- ✅ Switch between domains without losing embeddings

### 2. **Config Folder System**
- ✅ All configs in `config/` folder
- ✅ Add new domains instantly: `config/config.your_domain.json`
- ✅ Generic domain support - **works with ANY problem type**

### 3. **Quick-Start Tools**
- ✅ `quickstart.py` - Switch domains in 10 seconds
- ✅ `health_check.py` - Verify system is ready
- ✅ Generic templates for any domain

### 4. **Better Data Handling**
- ✅ Automatic CSV encoding detection (UTF-8, Latin-1, CP1252)
- ✅ Batch embedding processing (no API overload)
- ✅ Flexible data path resolution

## 🚀 GETTING STARTED (Choose One Path)

### Path A: Start With Existing Domain
```bash
cd backend

# See available domains
python scripts/quickstart.py --list

# Switch to a domain (clears cache)
python scripts/quickstart.py --switch manufacturing

# Your .env is now set to this domain
```

### Path B: Create Brand New Domain (For Hackathon Problem)
```bash
cd backend

# Create config for the problem given
python scripts/quickstart.py --create "problem_name" \
  --desc "Problem description"

# Switch to it
python scripts/quickstart.py --switch problem_name

# Generate test data
python scripts/quickstart.py --switch problem_name --generate 500
```

### Path C: Just Start (Uses Generic Template)
```bash
cd backend

# Everything works out of the box
python -m uvicorn app.main:app --reload

# In another terminal
cd ../frontend && npm start
```

## 📋 Key Files You'll Use

```
backend/
├── config/
│   ├── template.json          ← Copy this for new domains
│   ├── config.manufacturing.json
│   ├── config.retail.json
│   └── config.healthcare.json
├── data/
│   └── [Put your CSV files here]
├── .chroma/                    ← Auto-created (persistence)
├── .env                        ← Your settings
└── scripts/
    ├── quickstart.py           ← USE THIS to switch domains
    ├── health_check.py         ← Verify system
    ├── generate_synthetic_data.py
    └── evaluate_rag.py
```

## ⚡ Super Quick Reference

```bash
# Check system is ready
python scripts/health_check.py

# List available domains
python scripts/quickstart.py --list

# Switch domains instantly
python scripts/quickstart.py --switch your_domain

# Generate test data
python scripts/generate_synthetic_data.py --domain your_domain --rows 1000

# Start backend
python -m uvicorn app.main:app --reload

# Start frontend (new terminal)
cd ../frontend && npm start

# Evaluate your solution
python scripts/evaluate_rag.py --domain your_domain --quick
```

## 🎬 For Your 3.5 Hour Sprint

| Time | Task | Command |
|------|------|---------|
| 0:00 | Understand problem | Read problem statement |
| 0:05 | Create domain config | `quickstart.py --create` |
| 0:15 | Add/generate data | Place CSV or `--generate` |
| 0:30 | Start development | Run backend + frontend |
| 2:30 | Finalize code | Test with `evaluate_rag.py` |
| 3:30 | Demo ready | Show your solution |

## 🔧 Configuration Example

**`config/config.your_domain.json`:**
```json
{
  "domain": "your_domain",
  "title": "🎯 Your Problem Title",
  "description": "What your solution does",
  "system_prompt": "You are an expert in your_domain...",
  "query_enhancement_prompt": "Focus on specific aspects...",
  "data_paths": ["data/*.csv"],
  "demo_responses": {
    "keyword": "Quick response for testing"
  }
}
```

## ✨ Key Improvements Made

1. **Persistent Storage**: No re-indexing data every restart
2. **Any Domain**: Not limited to 4 domains - works with any problem
3. **Config-Driven**: Change behavior without code changes
4. **Better Encoding**: Handles various CSV encodings
5. **Faster Switching**: Domain switching is now <5 seconds
6. **Health Check**: Verify everything before starting
7. **Quick Templates**: Generic domain template for fast setup

## 📊 System Status

Run this to see if everything is ready:
```bash
python scripts/health_check.py
```

Should show all ✅ checks passing.

## 🆘 Common Issues During Hackathon

### "No data files found"
```bash
# Make sure data is in data/ folder
ls data/
# or generate it
python scripts/generate_synthetic_data.py --domain your_domain --rows 1000
```

### "API quota exceeded"
```bash
# Use demo mode instead
export DEMO_MODE=True
# Responses come instantly!
```

### "Want to keep embeddings when switching domains"
```bash
# Use --keep-data flag (much faster!)
python scripts/quickstart.py --switch new_domain --keep-data
```

### "Need to add new custom fields to config"
```bash
# Edit config/config.your_domain.json
# The system will pick them up based on system_prompt/query_enhancement_prompt
```

## 🏆 You're Ready!

Your hackathon setup is complete. The system is:
- ✅ Fast (persistent DB)
- ✅ Flexible (any domain)
- ✅ Simple (config-driven)
- ✅ Ready (all tools included)

**Now go build something amazing!** 🚀

---

For more details see:
- `HACKATHON_SPEEDRUN.md` - Detailed guide
- `QUICK_REFERENCE.md` - Quick lookup
- `docs/README.md` - Full documentation