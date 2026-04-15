# 🚀 HOW TO RUN THIS PROJECT - COMPLETE GUIDE

**Everything you need to get this RAG system up and running in 10 minutes.**

---

## 📋 PREREQUISITES

Before you start, make sure you have:

- **Python 3.12+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **OpenAI API Key** - [Get one](https://platform.openai.com/api-keys)
- **Git** (optional) - [Download](https://git-scm.com/)

**Verify you have everything:**
```bash
python --version  # Should be 3.12+
node --version    # Should be 18+
npm --version     # Should be 8+
```

---

## ⚡ QUICK START (5 MINUTES)

### **Step 1: Set Up Environment**

```bash
# Navigate to backend
cd backend

# Create .env file with your OpenAI API key
# Windows PowerShell:
'OPENAI_API_KEY=sk-your-key-here' | Out-File -Encoding UTF8 .env

# or just create it manually - open .env and add:
# OPENAI_API_KEY=sk-your-key-here
```

**Don't have an API key?** No problem - use demo mode:
```bash
'DEMO_MODE=true' | Out-File -Encoding UTF8 .env -Append
```

### **Step 2: Install Dependencies**

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### **Step 3: Verify System is Ready**

```bash
cd backend
python scripts/health_check.py
```

Expected output: ✅ All 8 checks should pass
```
✅ Python 3.12.x
✅ Directories
✅ Critical Files
✅ Python Packages
✅ Configuration
✅ ChromaDB
✅ Environment Setup
✅ RAG Module
```

---

## 🎯 RUNNING THE FULL STACK

### **Terminal 1: Start Backend**

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### **Terminal 2: Start Frontend**

```bash
cd frontend
npm start
```

Expected output:
```
Compiled successfully!
Local: http://localhost:3000
```

### **Terminal 3: Test Backend (Optional)**

```bash
cd backend

# Test if RAG is working
python -c "from app.rag import ask_rag; print(ask_rag('test query'))"
```

### **Access the App**

Done! Open your browser to: **http://localhost:3000**

You should see:
- Landing page with "Get Started" button OR
- Login page if auth is enabled

---

## 🎯 SETTING UP FOR YOUR HACKATHON PROBLEM

When you receive a problem, follow these steps to get your RAG system ready:

### **Step 1: Create a Domain Config**

```bash
cd backend

# Create config for your problem
python scripts/quickstart.py --create "my_problem" --desc "My problem description"

# This creates: config/config.my_problem.json
```

### **Step 2: Add Your Data**

**Option A: Add your own CSV files**
```bash
# Copy your CSV files to the data folder
cp /path/to/your/data.csv data/

# Switch to your domain
python scripts/quickstart.py --switch "my_problem"
```

**Option B: Auto-generate test data**
```bash
# Generate 1000 synthetic rows
python scripts/quickstart.py --switch "my_problem" --generate 1000

# Or generate specific amount
python scripts/generate_synthetic_data.py --domain my_problem --rows 500
```

### **Step 3: Customize Config (IMPORTANT)**

Edit `config/config.my_problem.json`:

```json
{
  "domain": "my_problem",
  "title": "🎯 Your Problem Title",
  "description": "Brief description of your domain",
  "system_prompt": "You are an expert in [YOUR FIELD]. You help users by [YOUR VALUE-ADD].",
  "query_enhancement_prompt": "When answering, focus on [KEY ASPECTS]. Consider [CONSTRAINTS].",
  "data_paths": ["data/*.csv"],
  "demo_responses": {}
}
```

**Key customizations:**
- `title` - What users see in the UI
- `system_prompt` - Defines RAG behavior (MOST IMPORTANT)
- `query_enhancement_prompt` - Improves retrieval quality
- `data_paths` - Where to find your CSVs

### **Step 4: Restart Backend (to apply new config)**

```bash
# Stop backend with Ctrl+C, then restart:
python -m uvicorn app.main:app --reload
```

---

## 📊 USING THE SYSTEM

### **In the Web UI**

1. Select domain from dropdown (if multiple available)
2. Ask your question
3. See AI answer backed by your data
4. Optional: Upload files for context

### **From Command Line (Testing)**

```bash
# Test RAG with your domain
$env:CONFIG_FILE="config.my_problem.json"
python -c "from app.rag import ask_rag; print(ask_rag('your question here'))"
```

### **Programmatic Use**

```python
from app.rag import ask_rag, CONFIG

# Your domain config auto-loads from config/ folder
result = ask_rag("What is the..."?)
print(result)
```

---

## 🔧 SWITCHING BETWEEN DOMAINS

Once you have multiple domains configured:

```bash
# List all available domains
python scripts/quickstart.py --list

# Switch instantly
python scripts/quickstart.py --switch "other_domain"

# Check current status
python scripts/quickstart.py --status
```

Switching takes **less than 10 seconds** - no restart needed!

---

## 🐛 TROUBLESHOOTING

### **Issue: "ModuleNotFoundError: No module named 'openai'"**
```bash
pip install -r requirements.txt
```

### **Issue: "OPENAI_API_KEY not set"**
Create a `.env` file in `backend/` folder:
```
OPENAI_API_KEY=sk-your-key-here
```

Or use demo mode (no key needed):
```
DEMO_MODE=true
```

### **Issue: "Port 8000/3000 already in use"**
```bash
# Use different ports:
python -m uvicorn app.main:app --reload --port 8080
npm start --port 3001
```

### **Issue: "Cannot find data files"**
Make sure CSV files are in `backend/data/` folder:
```bash
ls backend/data/  # Check what's there
```

### **Issue: "ChromaDB not working"**
```bash
cd backend
rm -r .chroma  # Delete cache
python scripts/health_check.py  # Rebuild
```

### **Issue: Health check fails**
```bash
# Run detailed check
python scripts/health_check.py

# Check specific Python package
python -c "import chromadb; print('OK')"
```

---

## 📁 PROJECT STRUCTURE

```
RAG/
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI server
│   │   ├── rag.py          # RAG logic (CORE FILE)
│   │   ├── db.py           # Database
│   │   └── auth.py         # Authentication
│   ├── config/             # Domain configs (PUT YOUR CONFIG HERE)
│   │   ├── config.json     # Default
│   │   ├── config.manufacturing.json
│   │   ├── config.retail.json
│   │   └── template.json   # Copy this to create new domain
│   ├── data/               # CSV data files (PUT YOUR DATA HERE)
│   │   ├── *.csv           # Any CSV files go here
│   │   └── ...
│   ├── scripts/            # Quick-start tools
│   │   ├── quickstart.py   # Domain management
│   │   ├── health_check.py # System verification
│   │   └── generate_synthetic_data.py
│   ├── .chroma/            # Vector database (auto-created)
│   ├── .env.example        # Environment template
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # For Docker deployment
│
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main React app
│   │   ├── components/     # React components
│   │   ├── pages/          # Pages (Chat, Landing, Login)
│   │   └── api.js          # API client
│   ├── package.json        # Node dependencies
│   └── public/
│
├── HOW_TO_RUN.md          # This file
├── QUICK_REFERENCE.md     # Command cheat sheet
├── README_FIRST.md        # Entry point
└── ... (other docs)
```

---

## ✅ COMMON TASKS

### **Task: Test if everything works**
```bash
cd backend && python scripts/health_check.py
```

### **Task: See current setup status**
```bash
cd backend && python scripts/quickstart.py --status
```

### **Task: Create test data without OpenAI API**
```bash
cd backend
python scripts/quickstart.py --create "test" --generate 500
```

### **Task: Reset everything**
```bash
cd backend
rm -r .chroma         # Delete vector cache
rm config/config.*.json  # Delete custom configs (keep template)
# Then restart: python -m uvicorn app.main:app --reload
```

### **Task: Run with demo mode (no API key needed)**
```bash
# Create .env file with:
DEMO_MODE=true

# Then run:
python -m uvicorn app.main:app --reload
```

### **Task: Deploy with Docker**
```bash
docker build -t rag-system .
docker run -p 8000:8000 -p 3000:3000 rag-system
```

---

## 📚 MORE DOCUMENTATION

- **`QUICK_REFERENCE.md`** - Command cheatsheet (bookmark this!)
- **`HACKATHON_SPEEDRUN.md`** - 3.5-hour timeline
- **`SYSTEM_OVERVIEW.md`** - Deep architecture guide
- **`DOCUMENTATION_INDEX.md`** - All guides explained
- **`TOOLKIT_INVENTORY.md`** - Complete file reference

---

## 🎯 NEXT STEPS

1. ✅ Run health check: `python scripts/health_check.py`
2. ✅ Start backend: `python -m uvicorn app.main:app --reload`
3. ✅ Start frontend: `cd frontend && npm start`
4. ✅ Open browser: `http://localhost:3000`
5. ✅ Create domain: `python scripts/quickstart.py --create "my_problem"`
6. ✅ Add data: Copy CSVs to `data/` folder
7. ✅ Customize config: Edit `config/config.my_problem.json`
8. ✅ Test RAG: Ask a question in the UI

**You're ready! Time to build! ⚡**

---

## 💡 PRO TIPS

- **Save time:** Keep `npm start` and `uvicorn` running in separate terminals while developing
- **Debug faster:** Use `--reload` on uvicorn to auto-restart on code changes
- **Switch domains in seconds:** Use `quickstart.py --switch` instead of restarting
- **Test without API:** Use `DEMO_MODE=true` to test without OpenAI API costs
- **Persistent data:** Vector database auto-saves to `.chroma/` folder, survives restarts
- **Config-driven:** Change behavior by editing JSON, not code - changes apply on next request

---

**Questions?** Check the documentation files or look at `app/rag.py` for implementation details.

**Ready to hack?** Go build something awesome! 🚀
