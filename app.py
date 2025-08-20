from fastapi import FastAPI
from services.plan_service import generate_plan
from services.ai_plan_service import generate_ai_training_diet_plan
from models.plan_responses import PlanResponse
from models.plan_request import PlanRequest
from docs.plan_request_docs import plan_description

app = FastAPI(
    title="FitPal API",
    description="API for calculating a healthy plan for weight loss or gain",
    version="1.0.0",
)

@app.post(
    "/plan_ai",
    response_model=PlanResponse,
    summary="Generates a healthy calorie plan for weight loss or gain",
    description=plan_description,
    response_model_exclude_none=True,
)
async def generate_plan_with_ai(req: PlanRequest):
    # Generate the basic plan synchronously
    plan_result = generate_plan(req)

    # If the plan is not feasible, return the Pydantic model directly
    if not plan_result.feasible:
        return plan_result

    # Call the async AI plan function directly with await
    ai_plan = await generate_ai_training_diet_plan(plan_result.model_dump())

    # Convert the plan_result model to a dictionary and add the AI plan
    result_dict = plan_result.model_dump()
    result_dict["ai_plan"] = ai_plan

    return result_dict
