# Hackathon RAG Assistant

A modular, domain-adaptable Retrieval-Augmented Generation (RAG) system designed for hackathon challenges. Quickly switch between domains like Manufacturing Quality Analysis, Retail Demand Forecasting, and Healthcare Policy Q&A.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key

### Installation

1. **Backend Setup:**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env  # Add your OpenAI API key
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Generate Sample Data:**
   ```bash
   cd backend
   python scripts/generate_synthetic_data.py --domain manufacturing --rows 1000
   ```

4. **Run Backend:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

## 🏗️ Architecture

```
├── backend/
│   ├── app/              # FastAPI application
│   │   ├── main.py       # API endpoints
│   │   ├── rag.py        # RAG logic
│   │   ├── auth.py       # Authentication
│   │   └── db.py         # Database utilities
│   ├── scripts/          # Utility scripts
│   │   ├── generate_synthetic_data.py
│   │   └── evaluate_rag.py
│   ├── data/             # Domain data files
│   └── config.*.json     # Domain configurations
├── frontend/
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Page components
│   │   └── styles/       # CSS styles
│   └── public/
└── docs/                 # Documentation
```

## 🎯 Domain Configuration

Switch domains by setting the `CONFIG_FILE` environment variable:

```bash
export CONFIG_FILE=config.manufacturing.json
# or
export CONFIG_FILE=config.retail.json
# or
export CONFIG_FILE=config.healthcare.json
```

### Available Domains

#### Manufacturing Quality Incident Assistant
- **Problem:** Analyze quality incidents and suggest root causes
- **Data:** Defect logs, process parameters, timestamps
- **Config:** `config.manufacturing.json`

#### Retail Demand Forecast Deviation Assistant
- **Problem:** Explain forecast vs actual demand deviations
- **Data:** Sales data, forecasts, promotional flags
- **Config:** `config.retail.json`

#### Healthcare Operations Policy Q&A Assistant
- **Problem:** Answer questions about policies and procedures
- **Data:** SOPs, guidelines, FAQs
- **Config:** `config.healthcare.json`

## 🛠️ Development Tools

### Generate Synthetic Data
```bash
# Manufacturing data
python scripts/generate_synthetic_data.py --domain manufacturing --rows 1000

# Retail data
python scripts/generate_synthetic_data.py --domain retail --rows 1000

# Healthcare documents
python scripts/generate_synthetic_data.py --domain healthcare --rows 500
```

### Evaluate Performance
```bash
# Quick evaluation
python scripts/evaluate_rag.py --domain manufacturing --quick

# Full evaluation
python scripts/evaluate_rag.py --domain manufacturing --output results.json
```

### Demo Mode
Set `DEMO_MODE=True` in `.env` to use mock responses without OpenAI API calls.

## 📊 Data Schema

### Manufacturing
```csv
timestamp,defect_type,line,product,severity,quantity,temperature,pressure,speed,operator,batch_id
```

### Retail
```csv
date,product,category,region,channel,forecast,actual,deviation_percent,is_promotion,supply_constraint,season
```

### Healthcare
```csv
id,title,content,category,department,last_updated
```

## 🔧 API Endpoints

- `GET /config` - Get current domain configuration
- `POST /login` - User authentication
- `POST /ask` - Query the RAG assistant

## 🚀 Deployment

### Docker
```bash
docker build -t rag-assistant .
docker run -p 8000:8000 rag-assistant
```

### Environment Variables
```env
OPENAI_API_KEY=your_key_here
CONFIG_FILE=config.manufacturing.json
DEMO_MODE=False
```

## 📈 Evaluation Metrics

- **Relevance:** Query-response overlap, context coverage
- **Accuracy:** F1 score against ground truth
- **Performance:** Response time, success rate
- **Actionability:** Presence of actionable recommendations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests and documentation
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.