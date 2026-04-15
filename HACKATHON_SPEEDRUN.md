# ⏱️ Hackathon Mode - 3.5 Hour Sprint Guide

## 🎯 Quick Start (5 minutes)

### 1. **Setup Environment**
```bash
# Backend setup
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env: Add your OPENAI_API_KEY or set DEMO_MODE=True
```

### 2. **Check Your Domain** (30 seconds)
```bash
# List all available domains
python scripts/quickstart.py --list

# Or create a new domain config
python scripts/quickstart.py --create "your_domain" --desc "Your domain description"
```

### 3. **Switch to Your Domain** (30 seconds)
```bash
# Switch and auto-clear cache
python scripts/quickstart.py --switch "your_domain"

# Option: Keep cache for faster switching
python scripts/quickstart.py --switch "your_domain" --keep-data
```

### 4. **Add Your Data** (1-2 minutes)
- Place CSV files in `data/` folder
- Or generate sample data:
```bash
python scripts/quickstart.py --switch "your_domain" --generate 1000
```

### 5. **Start Coding** (2-3 hours)
```bash
# Terminal 1: Backend
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend  
cd ../frontend
npm install
npm start
```

Visit: http://localhost:3000

---

## 📊 System Architecture

```
.chroma/                 ← Persistent ChromaDB (disk-based)
config/                  ← All domain configs here
  ├── config.json        ← Current config
  ├── template.json      ← Use as template for new domains
  ├── config.manufacturing.json
  ├── config.retail.json
  └── config.healthcare.json
data/                    ← CSV files here (auto-loaded)
app/
  ├── main.py           ← FastAPI server
  ├── rag.py            ← Core RAG engine (flexible for any domain)
  ├── auth.py
  └── db.py
scripts/
  ├── quickstart.py     ← Domain switching tool (USE THIS!)
  ├── generate_synthetic_data.py
  └── evaluate_rag.py
```

---

## ⚡ Key Changes for Your Workflow

### ✅ Persistent Database
- ChromaDB now saves to disk (`.chroma/` folder)
- **No data re-indexing on restart** - instant startup!

### ✅ Config Folder System
- All configs in `config/` folder
- Switch via: `python scripts/quickstart.py --switch DOMAIN`
- Or manually: `export CONFIG_FILE=config.your_domain.json`

### ✅ Generic Domain Support
- **Works with ANY domain, not just 4 predefined ones**
- System auto-detects CSV structure
- Flexible system prompt based on config

### ✅ No More Path Issues
- All paths resolved relative to project root
- Works from any terminal location

---

## 🚀 Typical Hackathon Workflow

### Hour 0-0.5: Problem Analysis
```bash
# Create config for the problem given at hackathon
python scripts/quickstart.py --create "hackathon_problem" \
  --desc "Problem statement from organizers"
```

### Hour 0.5-1: Data Preparation
```bash
# Add your data files to data/ folder
# Or generate samples if data isn't available
python scripts/quickstart.py --switch hackathon_problem --generate 500
```

### Hour 1-3: Development
- Edit `config/config.hackathon_problem.json` to refine system behavior
- Add business logic in `app/rag.py` or `app/main.py`
- Build UI in `frontend/src/`

### Hour 3-3.5: Polish & Demo
- Test with `scripts/evaluate_rag.py`
- Ensure .env is configured properly
- Demo ready!

---

## 🎯 Critical Tips for Speed

### 1. **Don't Restart Chrome DB Unless Needed**
```bash
# Fast switching (keeps cache)
python scripts/quickstart.py --switch new_domain --keep-data

# Use this if you MUST clear
python scripts/quickstart.py --switch new_domain
```

### 2. **Use Demo Mode for Testing UI**
```bash
# .env
DEMO_MODE=True
OPENAI_API_KEY=sk-xxx  # Still need key even in demo mode for errors

# Responses come instantly - test UI/UX fast!
```

### 3. **Batch Process Large Datasets**
- Generator handles batching automatically
- No API overload

### 4. **Use Generic Templates**
```bash
# Instead of starting from scratch, template has:
# - Smart system prompts
# - Demo responses
# - Good defaults for any domain

cp config/template.json config/my_domain.json
# Then edit slightly
```

### 5. **Skip Unnecessary Steps**
- Don't regenerate data if provided
- Don't re-index if using --keep-data
- Skip evaluation if time is tight

---

## 🔧 Customize for Your Domain

### Edit `config/config.your_domain.json`:

```json
{
  "domain": "your_domain",
  "title": "🎯 Your Title",
  "description": "What this solves",
  "system_prompt": "You are an expert in your_domain...",
  "query_enhancement_prompt": "Focus on specific aspects...",
  "data_paths": ["data/*.csv"],  # Where to find data
  "demo_responses": {
    "keyword": "Response when user says keyword"
  }
}
```

### That's it! The system handles the rest.

---

## 📈 Performance Expectations

| Operation | Time |
|-----------|------|
| Domain switch | <5 sec |
| Data indexing (1000 rows) | 10-30 sec |
| Query response | 2-5 sec |
| Full restart | 15-30 sec |

---

## 🆘 Troubleshooting

### "No data files found"
```bash
# Make sure files are in data/
ls data/

# Check config data_paths
cat config/config.your_domain.json | grep data_paths
```

### "API Quota Exceeded"
```bash
# Use demo mode
export DEMO_MODE=True

# Test with smaller dataset
python scripts/generate_synthetic_data.py --domain your_domain --rows 10
```

### "Module not found"
```bash
# Reinstall requirements
cd backend
pip install -r requirements.txt
```

### ChromaDB Issues
```bash
# Clear cache and restart
rm -rf .chroma
python -m uvicorn app.main:app --reload
```

---

## 🎬 Show Your Work!

Judge criteria usually include:
1. **Problem Understanding** - Config/system prompt shows you get it
2. **Speed** - How fast you set up (quickstart tool is key!)
3. **Code Quality** - Use modular approaches
4. **Results** - Run evaluation script to show metrics

---

## 💡 Pro Tips

- **Save time on docs**: Use config descriptions (shown to users)
- **Test incrementally**: Import 10 rows first, then 1000
- **Version control**: Commit working config before trying changes
- **Parallel work**: One person on data, one on UI
- **Demo mode beats API**: Use while developing UI/UX

---

Good luck! 🏆