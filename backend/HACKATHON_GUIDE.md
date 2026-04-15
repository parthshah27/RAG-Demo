# 🚀 RAG AI Assistant - Hackathon Customization Guide

## Quick Start for New Problem Statement

### Step 1: Create Your Domain Config

1. Copy `config.json` to `config.[domain].json`
   ```bash
   cp backend/config.json backend/config.healthcare.json
   ```

2. Edit the config file with your domain details:
   ```json
   {
     "domain": "your_domain_name",
     "title": "🎯 Your Domain Title",
     "description": "Your domain description",
     "system_prompt": "Custom instructions for your AI assistant",
     "query_enhancement_prompt": "Keywords and context hints for better understanding",
     "data_paths": ["backend/data/your_domain/*.csv"],
     "demo_responses": {
       "keyword1": "Sample response 1",
       "keyword2": "Sample response 2"
     }
   }
   ```

### Step 2: Switch Between Configs

Edit `.env` file to point to your config:
```bash
# Keep DEMO_MODE=true for testing without OpenAI API
DEMO_MODE=true

# Configuration file to use (default: config.json)
CONFIG_FILE=config.healthcare.json
```

### Step 3: Add Your Data

Place your CSV files in the corresponding data directory:
```
backend/data/
  ├── healthcare/
  │   ├── patients.csv
  │   ├── treatments.csv
  │   └── facilities.csv
  ├── ecommerce/
  │   ├── sales.csv
  │   ├── inventory.csv
  │   └── customers.csv
  └── your_domain/
      ├── data1.csv
      ├── data2.csv
      └── ...
```

### Step 4: Restart Backend

```bash
cd backend
python -m uvicorn app.main:app --reload
```

## Configuration Reference

### Required Fields

| Field | Purpose | Example |
|-------|---------|---------|
| `domain` | Domain name (lowercase, no spaces) | "finance", "healthcare" |
| `title` | UI title with emoji | "💰 AI Financial Analyst" |
| `description` | Landing page description | "Analyze financial data..." |
| `system_prompt` | Instructions for AI | "You are a financial analyst..." |
| `query_enhancement_prompt` | Keywords for better search | "Possible meanings: revenue..." |
| `data_paths` | Glob patterns for CSV files | ["backend/data/finance/*.csv"] |
| `demo_responses` | Demo mode fallback responses | {"keyword": "response"} |

### Example Configs Provided

- **Finance** (default): `config.json`
- **Healthcare**: `config.healthcare.json`
- **E-Commerce**: `config.ecommerce.json`
- **Agriculture**: `config.agriculture.json`

## How Customization Works

### 1. Frontend Automatically Updates

- Landing page shows custom title + description from config
- Chat page shows domain-specific placeholder text
- No code changes needed!

### 2. Backend Adapts

- Loads CSV files from domain-specific paths
- Uses domain-specific prompts
- Returns domain-specific demo responses
- Re-indexes data in separate ChromaDB collection per domain

### 3. Authentication Remains Same

- Login with `admin` / `admin` for all domains
- No authentication config needed

## Quick Config Templates

### Finance Domain
```json
{
  "domain": "finance",
  "title": "💰 AI Finance Analyst",
  "system_prompt": "Analyze financial metrics, budgets, and fiscal data..."
}
```

### Healthcare Domain
```json
{
  "domain": "healthcare",
  "title": "🏥 AI Healthcare Assistant",
  "system_prompt": "Analyze medical records, patient data, and health statistics..."
}
```

### Education Domain
```json
{
  "domain": "education",
  "title": "🎓 AI Education Assistant",
  "system_prompt": "Analyze student performance, curriculum, and educational data..."
}
```

### Supply Chain Domain
```json
{
  "domain": "supply_chain",
  "title": "📦 AI Logistics Assistant",
  "system_prompt": "Analyze warehouse, inventory, and supply chain data..."
}
```

## Demo Mode for Quick Testing

When `DEMO_MODE=true` in `.env`:
- No OpenAI API needed
- Uses `demo_responses` from config
- Perfect for testing UI and flow
- Keywords trigger demo responses

Example: If config has:
```json
"demo_responses": {
  "revenue": "Total revenue for Q1: $5.2M"
}
```

Then asking "What's the revenue?" will return that response.

## Production Ready

When you have OpenAI API credits:
1. Set `DEMO_MODE=false`
2. Backend will use real ChromaDB + embeddings
3. Queries will use your CSV data via RAG
4. LLM will generate intelligent responses

## Troubleshooting

### Config not loading?
```bash
# Check config file exists
ls backend/config*.json

# Check .env has correct CONFIG_FILE
cat backend/.env
```

### Data not found?
```bash
# Verify CSV files in correct path
ls backend/data/your_domain/

# Check data_paths in config matches actual paths
```

### Demo responses not showing?
```bash
# Ensure DEMO_MODE=true
grep DEMO_MODE backend/.env

# Check demo_responses has keywords matching your queries
```

## For Hackathon Success

1. **Pre-load multiple configs** for quick demo switching
2. **Use demo mode** for rapid prototyping
3. **Test with real images** in your problem statement
4. **Prepare 2-3 example queries** to showcase functionality
5. **Document your domain** in config for judges
6. **Keep data files organized** by domain

Good luck with your hackathon! 🚀
