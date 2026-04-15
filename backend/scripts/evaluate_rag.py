#!/usr/bin/env python3
"""
Evaluation Tools for RAG Assistant
Measures relevance, accuracy, and performance of responses.
"""

import time
import json
import argparse
from typing import List, Dict
import re
from collections import Counter
import os
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag import ask_rag, CONFIG

def evaluate_relevance(response: str, query: str, context_docs: List[str]) -> Dict:
    """Evaluate response relevance to query and context."""
    scores = {}

    # Check if response mentions key terms from query
    query_words = set(re.findall(r'\b\w+\b', query.lower()))
    response_words = set(re.findall(r'\b\w+\b', response.lower()))
    scores['query_overlap'] = len(query_words.intersection(response_words)) / len(query_words) if query_words else 0

    # Check if response references context
    context_text = ' '.join(context_docs).lower()
    response_lower = response.lower()

    # Simple keyword matching (could be improved with embeddings)
    context_keywords = set(re.findall(r'\b\w+\b', context_text))
    response_keywords = set(re.findall(r'\b\w+\b', response_lower))
    scores['context_coverage'] = len(context_keywords.intersection(response_keywords)) / len(context_keywords) if context_keywords else 0

    # Length appropriateness
    word_count = len(response.split())
    scores['response_length'] = 1.0 if 10 <= word_count <= 200 else 0.5

    # Actionability score (presence of specific recommendations)
    action_words = ['recommend', 'suggest', 'should', 'consider', 'investigate', 'check', 'verify']
    scores['actionability'] = 1.0 if any(word in response_lower for word in action_words) else 0.0

    return scores

def evaluate_accuracy(response: str, ground_truth: str = None) -> Dict:
    """Evaluate factual accuracy (requires ground truth)."""
    if not ground_truth:
        return {'accuracy': None, 'note': 'No ground truth provided'}

    # Simple text similarity (BLEU-like)
    gt_words = ground_truth.lower().split()
    resp_words = response.lower().split()

    # Calculate precision, recall, F1
    gt_counter = Counter(gt_words)
    resp_counter = Counter(resp_words)

    common = sum((gt_counter & resp_counter).values())
    precision = common / len(resp_words) if resp_words else 0
    recall = common / len(gt_words) if gt_words else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'accuracy': f1  # Simplified
    }

def evaluate_performance(func, *args, **kwargs) -> Dict:
    """Measure response time and throughput."""
    start_time = time.time()
    try:
        result = func(*args, **kwargs)
        end_time = time.time()
        return {
            'response_time': end_time - start_time,
            'success': True,
            'result_length': len(str(result)) if result else 0
        }
    except Exception as e:
        end_time = time.time()
        return {
            'response_time': end_time - start_time,
            'success': False,
            'error': str(e)
        }

def run_test_suite(test_cases: List[Dict], output_file: str = None) -> Dict:
    """Run a suite of test cases and aggregate results."""
    results = []

    for i, test_case in enumerate(test_cases):
        query = test_case['query']
        ground_truth = test_case.get('expected_answer')
        category = test_case.get('category', 'general')

        print(f"Testing case {i+1}/{len(test_cases)}: {query[:50]}...")

        # Measure performance
        perf_result = evaluate_performance(ask_rag, query)

        if perf_result['success']:
            response = perf_result.get('result', '')
            # Evaluate relevance (we'd need context docs for full eval)
            relevance_scores = evaluate_relevance(response, query, [])
            accuracy_scores = evaluate_accuracy(response, ground_truth)

            result = {
                'test_case': i+1,
                'query': query,
                'response': response,
                'category': category,
                'performance': perf_result,
                'relevance': relevance_scores,
                'accuracy': accuracy_scores
            }
        else:
            result = {
                'test_case': i+1,
                'query': query,
                'error': perf_result.get('error'),
                'performance': perf_result
            }

        results.append(result)

    # Aggregate results
    summary = {
        'total_tests': len(results),
        'successful_tests': len([r for r in results if r.get('performance', {}).get('success')]),
        'avg_response_time': sum(r.get('performance', {}).get('response_time', 0) for r in results) / len(results),
        'avg_relevance': sum(r.get('relevance', {}).get('query_overlap', 0) for r in results if 'relevance' in r) / len([r for r in results if 'relevance' in r]) if results else 0,
        'avg_accuracy': sum(r.get('accuracy', {}).get('f1_score', 0) for r in results if 'accuracy' in r) / len([r for r in results if 'accuracy' in r]) if results else 0
    }

    if output_file:
        with open(output_file, 'w') as f:
            json.dump({'summary': summary, 'results': results}, f, indent=2)
        print(f"Results saved to {output_file}")

    return {'summary': summary, 'results': results}

def load_test_cases(domain: str) -> List[Dict]:
    """Load domain-specific test cases."""
    test_cases = {
        'manufacturing': [
            {
                'query': 'Why are there more defects on Line A?',
                'expected_answer': 'Line A shows higher defect rates possibly due to temperature variations or operator issues.',
                'category': 'root_cause'
            },
            {
                'query': 'What factors contribute to critical severity defects?',
                'expected_answer': 'Critical defects are often linked to process parameter deviations like high temperature or low pressure.',
                'category': 'analysis'
            },
            {
                'query': 'How can we reduce surface scratches?',
                'expected_answer': 'Surface scratches may be reduced by adjusting speed settings or improving material handling.',
                'category': 'recommendation'
            }
        ],
        'retail': [
            {
                'query': 'Why did sales deviate from forecast in December?',
                'expected_answer': 'December deviations are likely due to holiday seasonality and promotional activities.',
                'category': 'seasonal_analysis'
            },
            {
                'query': 'What caused the negative deviation in the North region?',
                'expected_answer': 'North region deviations may be due to supply constraints or regional demand patterns.',
                'category': 'regional_analysis'
            },
            {
                'query': 'How do promotions affect forecast accuracy?',
                'expected_answer': 'Promotions typically increase actual sales beyond forecasts, leading to positive deviations.',
                'category': 'impact_analysis'
            }
        ],
        'healthcare': [
            {
                'query': 'What are the steps for patient admission?',
                'expected_answer': 'Patient admission requires ID verification, insurance check, and database confirmation.',
                'category': 'procedure'
            },
            {
                'query': 'How should medications be administered?',
                'expected_answer': 'Follow the 5 Rights: right patient, drug, dose, route, and time, with double-check for high-risk drugs.',
                'category': 'protocol'
            },
            {
                'query': 'What are the infection control requirements?',
                'expected_answer': 'Mandatory hand hygiene, PPE usage in isolation areas, and regular environmental cleaning.',
                'category': 'policy'
            }
        ]
    }

    return test_cases.get(domain, [])

def main():
    parser = argparse.ArgumentParser(description='Evaluate RAG assistant performance')
    parser.add_argument('--domain', choices=['manufacturing', 'retail', 'healthcare'],
                       default=CONFIG.get('domain', 'finance'), help='Domain to evaluate')
    parser.add_argument('--test-file', type=str, help='JSON file with custom test cases')
    parser.add_argument('--output', type=str, default='evaluation_results.json',
                       help='Output file for results')
    parser.add_argument('--quick', action='store_true', help='Run quick evaluation with 3 test cases')

    args = parser.parse_args()

    if args.test_file:
        with open(args.test_file, 'r') as f:
            test_cases = json.load(f)
    else:
        test_cases = load_test_cases(args.domain)
        if args.quick:
            test_cases = test_cases[:3]

    print(f"Running evaluation for {args.domain} domain with {len(test_cases)} test cases...")

    results = run_test_suite(test_cases, args.output)

    # Print summary
    summary = results['summary']
    print("\n📊 Evaluation Summary:")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Successful: {summary['successful_tests']}")
    print(f"Avg Response Time: {summary['avg_response_time']:.2f}s")
    print(f"Avg Relevance: {summary['avg_relevance']:.2f}")
    print(f"Avg Accuracy: {summary['avg_accuracy']:.2f}")
    print(".2f")

if __name__ == '__main__':
    main()