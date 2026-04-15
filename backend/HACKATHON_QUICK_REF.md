# 🏆 Hackathon Quick Reference - Domain Switching

## To Switch Domains Instantly

### Option 1: Change Config File (Easiest)
```bash
# Edit .env file:
CONFIG_FILE=config.healthcare.json
# OR
CONFIG_FILE=config.ecommerce.json
# OR
CONFIG_FILE=config.agriculture.json

# Then restart backend:
python -m uvicorn app.main:app --reload
```

### Option 2: Create New Config From Template
```json
{
  "domain": "supply_chain",
  "title": "📦 AI Logistics",
  "description": "Analyze supply chain and logistics data",
  "system_prompt": "You are a supply chain analyst...",
  "query_enhancement_prompt": "Warehouse, inventory, shipment, logistics",
  "data_paths": ["backend/data/supply_chain/*.csv"],
  "demo_responses": {
    "warehouse": "Warehouse utilization at 85%",
    "inventory": "Current stock levels optimal"
  }
}
```

## Minimal Changes Needed

| Problem Statement | Change Required | Effort |
|------------------|-----------------|--------|
| Finance ➜ Healthcare | Change `config.json` | 30 seconds |
| Finance ➜ E-Commerce | Change `config.json` | 30 seconds |
| Finance ➜ Custom Domain | Create `config.custom.json` + add data | 5 minutes |

## Pre-Demo Setup

1. **Prepare 3-4 configs** for judges to try:
   - Finance (default)
   - Healthcare 
   - E-Commerce
   - Your custom domain

2. **Place sample data** in each folder:
   ```
   backend/data/healthcare/*.csv
   backend/data/ecommerce/*.csv
   backend/data/your_domain/*.csv
   ```

3. **Update demo responses** in each config with real examples

4. **Keep DEMO_MODE=true** to avoid API delays

## During Hackathon

### Judge asks about Healthcare?
```bash
# In terminal:
# Change CONFIG_FILE=config.healthcare.json
# Restart backend
# Refresh browser
```

### Judge brings new CSV data?
```bash
# 1. Add CSV to backend/data/new_domain/
# 2. Create new config.json (copy existing one)
# 3. Update:
#    - domain name
#    - title & description
#    - system_prompt
#    - demo_responses
#    - data_paths (point to new CSV location)
# 4. Restart backend
# 5. Done! App automagically works
```

## Live Demo Script

```
1. Show Finance domain (default)
   - Ask: "What was the total expenditure?"
   - Get demo response instantly

2. Switch to Healthcare
   - Edit .env → CONFIG_FILE=config.healthcare.json
   - Restart backend (2 sec)
   - Ask: "What's the patient recovery time?"
   - Get healthcare demo response

3. Show E-Commerce
   - Change CONFIG_FILE=config.ecommerce.json
   - Restart backend (2 sec)
   - Ask: "What were total sales?"
   - Get e-commerce demo response

4. Show Custom Domain
   - If time permits, show new config creation
   - Highlight how 5 lines of JSON config = entire new domain
```

## Key Files to Know

```
backend/
├── config.json                    # Default (Finance)
├── config.healthcare.json         # Healthcare domain
├── config.ecommerce.json          # E-Commerce domain
├── config.agriculture.json        # Agriculture domain
├── .env                          # CONFIG_FILE setting
├── HACKATHON_GUIDE.md            # Full documentation
└── data/
    ├── finance/*.csv             # Finance data
    ├── healthcare/*.csv          # Healthcare data
    ├── ecommerce/*.csv           # E-Commerce data
    └── agriculture/*.csv         # Agriculture data
```

## What Happens Behind Scenes

1. Frontend fetches `/config` endpoint
2. Backend reads CONFIG_FILE from .env
3. Frontend shows domain-specific title
4. Backend loads domain-specific CSV data
5. ChromaDB stores in separate collection per domain
6. Demo responses match domain keywords
7. All prompts are domain-aware

## Pro Tips 🎯

1. **Test all configs before demo** - Ensure they work
2. **Have data ready** - Don't create CSV during demo
3. **Use demo mode** - No API calls = instant responses
4. **Prepare talking points** - Explain how config makes it flexible
5. **Show this to judges** - They love clean architecture!

Good luck! 🚀
