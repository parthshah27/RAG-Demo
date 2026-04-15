# Retail Demand Forecast Deviation Explanation Assistant

## Problem Statement
Retail organizations frequently observe deviations between forecasted and actual demand due to promotions, seasonality, or supply constraints. Analysts must investigate multiple reports and datasets to understand why forecasts missed expectations. An AI assistant capable of explaining demand deviations in simple language would accelerate analysis and support faster corrective decisions.

## Solution Overview
An AI explanation agent that analyzes retail demand data, forecasts, and contextual factors to generate clear, human-readable explanations of deviations and contributing factors.

## Data Schema
```csv
date,product,category,region,channel,forecast,actual,deviation_percent,is_promotion,supply_constraint,season
```

## Sample Queries
- "Why did sales deviate from forecast in December?"
- "What caused the negative deviation in the North region?"
- "How do promotions affect forecast accuracy?"

## Configuration
Use `config.retail.json`:
```json
{
  "domain": "retail",
  "title": "Retail Demand Assistant",
  "system_prompt": "You are an expert retail analyst...",
  "data_paths": ["data/retail_synthetic.csv"],
  "query_enhancement_prompt": "Consider seasonality, promotions, supply constraints, and regional factors."
}
```

## Expected Outcomes
- Actionable insights reducing analyst investigation effort by 60%
- Clear explanations of deviation drivers
- Improved forecast accuracy through pattern recognition