#!/usr/bin/env python3
"""
Synthetic Data Generator for Hackathon Problems
Generates realistic datasets for Manufacturing, Retail, and Healthcare domains.
"""

import pandas as pd
import numpy as np
import random
import argparse
import os
from datetime import datetime, timedelta

def generate_manufacturing_data(num_rows=1000):
    """Generate synthetic manufacturing quality incident data."""
    data = []
    defect_types = ['Crack', 'Dent', 'Misalignment', 'Color Variation', 'Size Deviation', 'Surface Scratch']
    lines = ['Line A', 'Line B', 'Line C', 'Line D']
    products = ['Widget X', 'Gadget Y', 'Tool Z', 'Part W']
    severities = ['Low', 'Medium', 'High', 'Critical']

    base_date = datetime.now() - timedelta(days=365)

    for i in range(num_rows):
        timestamp = base_date + timedelta(hours=random.randint(0, 8760))  # Random hour in year
        defect_type = random.choice(defect_types)
        line = random.choice(lines)
        product = random.choice(products)
        severity = random.choice(severities)

        # Simulate defect spikes
        if random.random() < 0.1:  # 10% chance of spike
            quantity = random.randint(50, 200)
        else:
            quantity = random.randint(1, 20)

        # Process parameters
        temperature = round(np.random.normal(150, 10), 1)
        pressure = round(np.random.normal(100, 5), 1)
        speed = round(np.random.normal(50, 5), 1)

        data.append({
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'defect_type': defect_type,
            'line': line,
            'product': product,
            'severity': severity,
            'quantity': quantity,
            'temperature': temperature,
            'pressure': pressure,
            'speed': speed,
            'operator': f'Operator_{random.randint(1, 20)}',
            'batch_id': f'BATCH_{random.randint(1000, 9999)}'
        })

    return pd.DataFrame(data)

def generate_retail_data(num_rows=1000):
    """Generate synthetic retail demand forecast data."""
    data = []
    products = ['Laptop', 'Smartphone', 'Tablet', 'Headphones', 'Monitor', 'Keyboard']
    categories = ['Electronics', 'Accessories', 'Computers', 'Audio']
    regions = ['North', 'South', 'East', 'West']
    channels = ['Online', 'Store', 'Wholesale']

    base_date = datetime.now() - timedelta(days=180)

    for i in range(num_rows):
        date = base_date + timedelta(days=i % 180)  # 6 months of data
        product = random.choice(products)
        category = random.choice(categories)
        region = random.choice(regions)
        channel = random.choice(channels)

        # Base demand
        base_forecast = random.randint(50, 500)

        # Add seasonality (higher in Q4)
        month = date.month
        seasonal_multiplier = 1.0
        if month in [11, 12]:
            seasonal_multiplier = 1.5
        elif month in [6, 7, 8]:
            seasonal_multiplier = 0.8

        # Add promotion effect
        is_promo = random.random() < 0.2  # 20% promotional periods
        promo_multiplier = 1.3 if is_promo else 1.0

        # Add supply constraints (occasional shortages)
        supply_issue = random.random() < 0.05  # 5% supply issues
        supply_multiplier = 0.7 if supply_issue else 1.0

        forecast = int(base_forecast * seasonal_multiplier * promo_multiplier)
        actual = int(forecast * supply_multiplier * np.random.normal(1.0, 0.2))  # Add noise

        deviation = ((actual - forecast) / forecast) * 100 if forecast > 0 else 0

        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'product': product,
            'category': category,
            'region': region,
            'channel': channel,
            'forecast': forecast,
            'actual': actual,
            'deviation_percent': round(deviation, 2),
            'is_promotion': is_promo,
            'supply_constraint': supply_issue,
            'season': 'Holiday' if month in [11, 12] else 'Normal'
        })

    return pd.DataFrame(data)

def generate_healthcare_data(num_rows=500):
    """Generate synthetic healthcare policies and procedures data."""
    # This will be text data, so we'll create a list of documents
    documents = []

    policies = [
        {
            'title': 'Patient Admission Procedure',
            'content': 'All patients must present valid ID and insurance information upon admission. Staff should verify patient information against the hospital database. Emergency admissions bypass standard verification but require immediate documentation.'
        },
        {
            'title': 'Medication Administration Protocol',
            'content': 'Nurses must follow the 5 Rights: Right patient, Right drug, Right dose, Right route, Right time. All medications require double-check by another qualified staff member for high-risk drugs.'
        },
        {
            'title': 'Infection Control Policy',
            'content': 'Hand hygiene is mandatory before and after patient contact. PPE must be worn in isolation rooms. Regular environmental cleaning schedules must be maintained.'
        },
        {
            'title': 'Discharge Planning Guidelines',
            'content': 'Discharge planning begins at admission. Patients must receive written discharge instructions including medication lists, follow-up appointments, and warning signs requiring immediate medical attention.'
        },
        {
            'title': 'Emergency Response Protocol',
            'content': 'Code Blue teams must respond within 2 minutes. All staff should be familiar with their roles in emergency situations. Regular drills are conducted monthly.'
        }
    ]

    # Generate variations and additional content
    for i in range(num_rows):
        base_policy = random.choice(policies)
        variation = f"""
{base_policy['title']} - Version {random.randint(1, 5)}

{base_policy['content']}

Additional Guidelines:
- Last updated: {(datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d')}
- Approved by: Dr. Smith_{random.randint(1, 10)}
- Reference: HOSP-POL-{random.randint(100, 999)}
- Related procedures: {', '.join([f'PROC-{random.randint(1000, 9999)}' for _ in range(2)])}

Sample paragraph with additional context about healthcare procedures and compliance requirements.
        """.strip()

        documents.append({
            'id': f'POL_{i+1}',
            'title': base_policy['title'],
            'content': variation,
            'category': 'Policy' if 'Policy' in base_policy['title'] else 'Procedure',
            'department': random.choice(['Nursing', 'Administration', 'Medical', 'Emergency', 'Surgery']),
            'last_updated': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d')
        })

    return pd.DataFrame(documents)

def main():
    parser = argparse.ArgumentParser(description='Generate synthetic data for hackathon problems')
    parser.add_argument('--domain', choices=['manufacturing', 'retail', 'healthcare'],
                       required=True, help='Domain to generate data for')
    parser.add_argument('--rows', type=int, default=1000,
                       help='Number of rows/documents to generate')
    parser.add_argument('--output', type=str, default=None,
                       help='Output file path (default: data/{domain}_synthetic.csv)')

    args = parser.parse_args()

    print(f"Generating {args.rows} synthetic {args.domain} records...")

    if args.domain == 'manufacturing':
        df = generate_manufacturing_data(args.rows)
    elif args.domain == 'retail':
        df = generate_retail_data(args.rows)
    elif args.domain == 'healthcare':
        df = generate_healthcare_data(args.rows)

    # Set default output path
    if args.output is None:
        os.makedirs('data', exist_ok=True)
        args.output = f'data/{args.domain}_synthetic.csv'

    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    # Save to CSV
    df.to_csv(args.output, index=False)
    print(f"✅ Saved {len(df)} records to {args.output}")

    # Print sample
    print("\nSample data:")
    print(df.head())

if __name__ == '__main__':
    main()