CLASSIFICATION_PROMPT = """
You are an expert HR analyst. Classify this employee feedback into exactly ONE of these categories:

Categories:
- Process Issues: Complicated procedures, reimbursement delays, difficult processes
- Coverage Issues: Inadequate benefits, poor service quality, coverage gaps
- Benefit Value: Cost concerns, location limitations, membership issues

Employee Feedback: {comment}
Benefit Type: {benefit_type}
Satisfaction Score: {score}/5

Respond with only the category name:
"""

SENTIMENT_PROMPT = """
Analyze the sentiment and severity of this employee feedback.

Sentiment: positive, negative, or neutral
Severity: 1-5 scale (1=minor, 5=critical issue requiring immediate attention)

Feedback: {comment}
Satisfaction Score: {score}/5

Respond in format: {{"sentiment": "neutral", "severity": 4}}
"""

ACTION_PROMPT = """
Based on the feedback analysis, identify a specific actionable task.

Category: {category}
Benefit: {benefit_type}
Sentiment: {sentiment}
Severity: {severity}
Employee Comment: {comment}

Provide a specific, actionable task (not generic advice):
"""

ROUTING_PROMPT = """
Route this task to the appropriate department and assign priority level.

Available Departments:
- Benefits Administration: Process improvements, reimbursements
- HR Benefits Team: Health insurance, life insurance, policy changes
- Vendor Management: Third-party services, gym memberships, external providers

Priority Levels: high (severity= 4-5), medium (severity= 3), low (severity= 1-2)

Task: {action}
Issue Category: {category}
Benefit Type: {benefit_type}
Severity Level: {severity}

Respond in format: {{"department": "Benefits Administration", "priority": "low"}}
"""

SYNTHESIS_PROMPT = """
Analyze the overall feedback patterns and provide strategic recommendations.

Data Summary:
- Category Distribution: {categories}
- High Priority Issues: {high_priority_count} items
- Top Problem Areas: {problematic_areas}

Provide exactly 3 strategic recommendations prioritized by impact and feasibility.
Include specific benefit cuts if data shows consistent negative feedback.
Focus on actionable changes that will improve employee satisfaction.

Format each recommendation as a bullet point.
"""