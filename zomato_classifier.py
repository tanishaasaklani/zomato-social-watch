import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

MODEL_NAME = "deepseek/deepseek-chat"


SYSTEM_PROMPT = """
You are a real-time social media analyst for Zomato.

Classify the post into exactly one category:

- urgent_safety_trust
- delivery_operations
- app_product_issues
- viral_positive_mentions
- competitor_intelligence
- irrelevant

Return ONLY valid JSON:

{
  "category": "...",
  "confidence": 0.95,
  "summary": "One sentence explanation."
}
"""


CATEGORY_RULES = {
    "urgent_safety_trust": {
        "priority": "HIGH",
        "score": 90,
        "action": "send_email_immediately",
        "escalate": True,
    },
    "delivery_operations": {
        "priority": "HIGH",
        "score": 80,
        "action": "email_and_dashboard_highlight",
        "escalate": True,
    },
    "app_product_issues": {
        "priority": "MEDIUM",
        "score": 60,
        "action": "log_for_product_team",
        "escalate": False,
    },
    "viral_positive_mentions": {
        "priority": "LOW",
        "score": 20,
        "action": "show_on_dashboard",
        "escalate": False,
    },
    "competitor_intelligence": {
        "priority": "MEDIUM",
        "score": 55,
        "action": "store_for_strategy_team",
        "escalate": False,
    },
    "irrelevant": {
        "priority": "LOW",
        "score": 10,
        "action": "no_action",
        "escalate": False,
    },
}


def classify_social_post(post_text: str):

    response = client.chat.completions.create(
    model=MODEL_NAME,
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": post_text}
    ],
    temperature=0,
    response_format={"type": "json_object"}
)

    raw = response.choices[0].message.content

    # print("\nRAW OPENROUTER RESPONSE:")
    # print(raw)



    result = json.loads(raw)

    category = result["category"]

    rules = CATEGORY_RULES.get(
        category,
        {
            "priority": "MEDIUM",
            "score": 50,
            "action": "manual_review",
            "escalate": False,
        }
    )

    return {
        "category": result["category"],
        "confidence": result["confidence"],
        "summary": result["summary"],
        "priority": rules["priority"],
        "score": rules["score"],
        "action": rules["action"],
        "escalate": rules["escalate"]
    }