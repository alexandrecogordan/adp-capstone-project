import json
import openai
import os
from typing import Dict, List
from prompt_templates import SYNTHESIS_PROMPT

class ResultsSynthesizer:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)

    def call_gpt(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()

    def synthesize_from_json(self, json_filepath: str = 'feedback_analysis_results.json') -> str:
        with open(json_filepath, 'r') as f:
            results = json.load(f)
        
        categories = {}
        high_priority = []
        benefit_issues = {}

        for r in results:
            categories[r['category']] = categories.get(r['category'], 0) + 1
            if r['priority'] == 'High':
                high_priority.append(r['action'])
            if r['severity'] >= 4:
                benefit_issues[r['benefit_type']] = benefit_issues.get(r['benefit_type'], 0) + 1

        prompt = SYNTHESIS_PROMPT.format(
            categories=categories,
            high_priority_count=len(high_priority),
            problematic_areas=benefit_issues
        )

        recommendations = self.call_gpt(prompt)
        
        # Generate summary
        priorities = {}
        for r in results:
            priorities[r['priority']] = priorities.get(r['priority'], 0) + 1

        md_content = f"""# GPT-4o Feedback Analysis Summary

## Overview
- **Total Processed**: {len(results)} feedback items

## Category Breakdown
{chr(10).join([f'- **{cat}**: {count}' for cat, count in categories.items()])}

## Priority Distribution
{chr(10).join([f'- **{pri}**: {count}' for pri, count in priorities.items()])}

## Recommendations
{recommendations}
"""

        with open('feedback_analysis_summary.md', 'w') as f:
            f.write(md_content)

        return recommendations

if __name__ == "__main__":
    import sys
    
    API_KEY = os.getenv('OPENAI_API_KEY') or input("Enter OpenAI API Key: ")
    synthesizer = ResultsSynthesizer(API_KEY)
    
    json_file = sys.argv[1] if len(sys.argv) > 1 else 'feedback_analysis_results.json'
    
    print(f"Synthesizing results from {json_file}...")
    recommendations = synthesizer.synthesize_from_json(json_file)
    
    print("Synthesis complete! File saved:")
    print("- feedback_analysis_summary.md")