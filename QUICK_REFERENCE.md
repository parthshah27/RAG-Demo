# ⚡ HACKATHON QUICK REFERENCE CARD

## 30-Second Setup
```bash
cd backend
pip install -r requirements.txt
python scripts/quickstart.py --status
```

## Switch Domain (DONE IN 10 SECONDS)
```bash
# See available
python scripts/quickstart.py --list

# Switch instantly
python scripts/quickstart.py --switch "your_domain"

# With auto-generated sample data
python scripts/quickstart.py --switch "your_domain" --generate 1000
```

## Create New Domain (OPTIONAL)
```bash
python scripts/quickstart.py --create "new_problem" --desc "Description"
# Edit: config/config.new_problem.json
```

## Start Development
```bash
# Terminal 1: Backend (auto-reload)
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend
cd ../frontend && npm start
```

## Configuration File
**Location:** `config/config.your_domain.json`
```json
{
  "domain": "your_domain",
  "title": "🎯 Title shown to users",
  "system_prompt": "You are an expert in...",
  "query_enhancement_prompt": "Focus on...",
  "data_paths": ["data/*.csv"],
  "demo_responses": { }
}
```

## Add Data
**Location:** `data/` folder
```bash
# 1. Place CSV files in data/ folder
# 2. Or generate:
python scripts/generate_synthetic_data.py --domain your_domain --rows 1000
```

## .env Configuration
```env
# Production (needs API key)
OPENAI_API_KEY=sk-xxx
CONFIG_FILE=config.your_domain.json
DEMO_MODE=False

# Testing (instant responses)
OPENAI_API_KEY=sk-xxx
CONFIG_FILE=config.your_domain.json
DEMO_MODE=True
```

## Test Your Solution
```bash
python scripts/evaluate_rag.py --domain your_domain --quick
```

## Key Files to Edit

| File | Purpose |
|------|---------|
| `config/config.your_domain.json` | Customize AI behavior |
| `app/main.py` | Add API endpoints |
| `app/rag.py` | Customize RAG logic |
| `frontend/src/pages/Chat.js` | Customize UI |

## Database (Automatic)
- **Location:** `.chroma/` folder
- **Type:** Persistent ChromaDB (disk-based)
- **Auto-indexes** on first startup
- **Survives** restarts (no re-indexing needed!)

## Common Mistakes to Avoid
❌ Don't manually restart ChromaDB unless needed (`--keep-data` is faster)
❌ Don't forget OPENAI_API_KEY in .env (use DEMO_MODE=True if missing)
❌ Don't put data outside `data/` folder
❌ Don't forget to `pip install -r requirements.txt`

## Performance Targets
- Domain switch: <5 sec ✓
- Data intake (1000 CSV rows): 15 sec ✓
- Query response: 2-5 sec ✓
- Full app restart: 15-30 sec ✓

## 3-Hour Timeline
| Time | Task |
|------|------|
| 0:00-0:15 | Problem analysis, create domain config |
| 0:15-0:45 | Data preparation (CSV or generate) |
| 0:45-2:45 | Development (2 hours) |
| 2:45-3:15 | Testing & refinement |
| 3:15-3:30 | Demo prep |

## Emergency Fixes
```bash
# Reinstall everything
pip install -r requirements.txt --force-reinstall

# Clear all caches and start fresh
rm -rf .chroma
rm -rf frontend/node_modules
python -m uvicorn app.main:app --reload

# Check system status
python scripts/quickstart.py --status
```

---

**💡 Pro Tip:** Keep this card open during hackathon! Refer to `HACKATHON_SPEEDRUN.md` for detailed info.