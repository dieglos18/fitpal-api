import json
from langchain.prompts import PromptTemplate
from config.llm_setup import get_llm

prompt_template = PromptTemplate(
    input_variables=["plan_data"],
    template="""
You are an expert in nutrition and training.  
Based on the following calculated data:

{plan_data}

Return a **valid** JSON (with no extra text) with the following structure:
{{
    "diet_plan": {{
        "breakfast": "...",
        "lunch": "...",
        "dinner": "...",
        "snacks": ["...", "..."],
        "notes": "..."
    }},
    "training_plan": {{
        "weekly_schedule": {{
            "monday": "...",
            "tuesday": "...",
            "wednesday": "...",
            "thursday": "...",
            "friday": "...",
            "saturday": "...",
            "sunday": "rest"
        }},
        "notes": "..."
    }},
    "explanation": "Brief explanation of why this plan was created"
}}

⚠️ IMPORTANT: Only respond with valid JSON, no extra text before or after.
""",
)


def generate_ai_training_diet_plan(plan_data: dict) -> dict:
    """Generates a diet and training plan using LangChain + OpenAI."""
    plan_str = json.dumps(plan_data, indent=2)

    llm = get_llm()

    chain = prompt_template | llm
    response = chain.invoke({"plan_data": plan_str})  # sin await

    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        raise ValueError("The model did not return valid JSON.")

