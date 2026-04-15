# Manufacturing Quality Incident Insight Assistant

## Problem Statement
Manufacturing teams encounter quality incidents such as defect spikes or process deviations that require rapid root cause analysis. Engineers often sift through logs, inspection reports, and metrics to identify probable causes, delaying resolution. An AI assistant that translates quality incident data into clear explanations would improve responsiveness and decision making on the shop floor.

## Solution Overview
A RAG-powered assistant that ingests quality inspection data, defect logs, and process parameters to provide concise explanations of incidents and suggest potential root causes.

## Data Schema
```csv
timestamp,defect_type,line,product,severity,quantity,temperature,pressure,speed,operator,batch_id
```

## Sample Queries
- "Why are there more defects on Line A this week?"
- "What factors contribute to critical severity defects?"
- "How can we reduce surface scratches on Widget X?"

## Configuration
Use `config.manufacturing.json`:
```json
{
  "domain": "manufacturing",
  "title": "Manufacturing Quality Assistant",
  "system_prompt": "You are an expert manufacturing quality engineer...",
  "data_paths": ["data/manufacturing_synthetic.csv"],
  "query_enhancement_prompt": "Focus on process parameters, defect patterns, and operational factors."
}
```

## Expected Outcomes
- Relevant, actionable explanations reducing analysis time by 70%
- Clear root cause suggestions based on data patterns
- Integration with existing quality management systems