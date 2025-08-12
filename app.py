from fastapi import FastAPI
from services.plan_service import generate_plan
from services.ai_plan_service import generate_ai_training_diet_plan
from models.plan_responses import PlanResponse
from models.plan_request import PlanRequest
from docs.plan_request_docs import plan_description
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()

app = FastAPI(
    title="FitPal API",
    description="API for calculating a healthy plan for weight loss or gain",
    version="1.0.0",
)

async def run_generate_ai_plan(plan_data: dict) -> dict:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, generate_ai_training_diet_plan, plan_data)


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

    # Run the AI plan generation in a separate thread to avoid blocking the event loop
    ai_plan = await run_generate_ai_plan(plan_result.model_dump())

    # Convert the plan_result model to a dictionary and add the AI plan at the same level
    result_dict = plan_result.model_dump()
    result_dict["ai_plan"] = ai_plan

    # Return the combined result matching the PlanResponse model structure
    return result_dict
