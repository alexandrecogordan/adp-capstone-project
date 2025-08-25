import pandas as pd
import openai
import json
from typing import Dict, List
import os
from prompt_templates import CLASSIFICATION_PROMPT, SENTIMENT_PROMPT, ACTION_PROMPT, ROUTING_PROMPT

def parse_json(response: str):
    try:
        return json.loads(response)
    except:
        return None

class GPTFeedbackPipeline:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)

        # Load benefit mappings
        benefits_df = pd.read_csv('benefits_data.csv')
        self.benefit_map = dict(zip(benefits_df['BenefitID'],
                                    benefits_df['BenefitType'] + ': ' + benefits_df['BenefitSubType']))

    def call_gpt(self, prompt: str, max_retries: int = 3) -> str | None:
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=1000
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"API call failed after {max_retries} attempts: {e}")
        return None

    def classify_feedback(self, comment: str, benefit_type: str, score: int) -> str:
        valid_categories = ["Process Issues", "Coverage Issues", "Benefit Value"]
        prompt = CLASSIFICATION_PROMPT.format(
            comment=comment,
            benefit_type=benefit_type,
            score=score
        )
        result = self.call_gpt(prompt)
        return "Unknown" if result not in valid_categories else result

    def analyze_sentiment(self, comment: str, score: int) -> tuple:
        prompt = SENTIMENT_PROMPT.format(
            comment=comment,
            score=score
        )
        result = parse_json(self.call_gpt(prompt))
        if result is None:
            return "unknown", -1
        sentiment = "unknown" if result["sentiment"] not in ["positive", "negative", "neutral"] else result["sentiment"]
        severity = -1 if not isinstance(result["severity"], int) or result["severity"] < 1 or result["severity"] > 5 else result["severity"]
        return sentiment, severity

    def identify_action(self, category: str, benefit_type: str, sentiment: str, severity: int,  comment: str) -> str:
        prompt = ACTION_PROMPT.format(
            category=category,
            benefit_type=benefit_type,
            sentiment=sentiment,
            severity=severity,
            comment=comment
        )
        result = self.call_gpt(prompt)
        return result if result else "unknown"

    def route_task(self, action: str, category: str, benefit_type: str, severity: int) -> tuple:
        prompt = ROUTING_PROMPT.format(
            action=action,
            category=category,
            benefit_type=benefit_type,
            severity=severity
        )
        result = parse_json(self.call_gpt(prompt))
        if result is None:
            return "unknown", "unknown"
        department = "unknown" if result["department"].lower() not in ["benefits administration", "hr benefits team", "vendor management"] else result["department"]
        priority = "unknown" if result["priority"].lower() not in ["high", "medium", "low"] else result["priority"]
        return department, priority

    def process_feedback(self, feedback_df: pd.DataFrame, limit: int = 50) -> List[Dict]:
        results = []

        for i, row in feedback_df.head(limit).iterrows():
            benefit_type = self.benefit_map.get(row['BenefitID'], f"Benefit {row['BenefitID']}")

            # Phase 1: Classification
            category = self.classify_feedback(row['Comments'], benefit_type, row['SatisfactionScore'])

            # Phase 2: Sentiment Analysis
            sentiment, severity = self.analyze_sentiment(row['Comments'], row['SatisfactionScore'])

            # Phase 3: Action Identification
            action = self.identify_action(category, benefit_type, sentiment, severity, row['Comments'])

            # Phase 4: Task Routing
            department, priority = self.route_task(action, category, benefit_type, severity)

            result = {
                'employee_id': row['EmployeeID'],
                'benefit_type': benefit_type,
                'category': category,
                'sentiment': sentiment,
                'severity': severity,
                'action': action,
                'department': department,
                'priority': priority
            }

            results.append(result)

            with open('feedback_analysis_results.json', 'w') as f:
                json.dump(results, f, indent=2)

            print(f"Processed {i+1}/{min(limit, len(feedback_df))}")

        return results


def run_pipeline():
    # Set your OpenAI API key
    API_KEY = os.getenv('OPENAI_API_KEY') or input("Enter OpenAI API Key: ")

    # Load data
    feedback_df = pd.read_csv('feedback_data.csv')

    # Initialize pipeline
    pipeline = GPTFeedbackPipeline(API_KEY)

    # Process feedback (limit to 50 for demo)
    print("Processing feedback with GPT-4o...")
    results = pipeline.process_feedback(feedback_df, 6000)

    print("Analysis complete! Files saved:")
    print("- feedback_analysis_results.json")

    return results


if __name__ == "__main__":
    results = run_pipeline()
