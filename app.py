from fastapi import FastAPI
from math import floor
from datetime import date
from utils.calculate_bmr import calculate_bmr
from models.plan_responses import PlanResponse, PlanResponseFeasible, PlanResponseNotFeasible
from models.plan_request import PlanRequest
from docs.plan_request_docs import plan_description
from constants.nutrition_constants import (
    KCAL_PER_KG,
    MAX_SAFE_DAILY_DEFICIT,
    MAX_SAFE_DAILY_SURPLUS,
    MIN_CALORIES_FEMALE,
    MIN_CALORIES_MALE,
)

app = FastAPI(
    title="FitPal API",
    description="API for calculating a healthy plan for weight loss or gain",
    version="1.0.0",
)

@app.post(
    "/plan",
    response_model=PlanResponse,
    summary="Generates a healthy calorie plan for weight loss or gain",
    description=plan_description,
    response_model_exclude_none=True,
)

def generate_plan(req: PlanRequest):
    days = (req.target_date - date.today()).days
    if days <= 0:
        return PlanResponseNotFeasible(
            feasible=False,
            reason="The date must be in the future",
            values={},
            user_message="Hello! Unfortunately, the date you selected is not valid because it must be a future date. Please try another date."
        )

    bmr = calculate_bmr(req.current_weight, req.height, req.age, req.sex)
    tdee = bmr * 1.2  # light activity by default

    weight_change = req.target_weight - req.current_weight
    total_kcal = abs(weight_change) * KCAL_PER_KG
    daily_change = total_kcal / days  # positive = gain, negative = loss

    if weight_change < 0:
        daily_deficit = abs(daily_change)
        if daily_deficit > MAX_SAFE_DAILY_DEFICIT:
            return PlanResponseNotFeasible(
                feasible=False,
                reason=f"Required daily deficit ({floor(daily_deficit)} kcal) is greater than the safe limit of {MAX_SAFE_DAILY_DEFICIT} kcal.",
                values={
                    "tdee": floor(tdee),
                    "daily_deficit": floor(daily_deficit),
                    "type": "loss",
                },
                user_message=(
                    "Hello! The plan you propose is not healthy because "
                    f"it requires a daily calorie deficit of {floor(daily_deficit)} kcal, "
                    f"which exceeds the recommended limit of {MAX_SAFE_DAILY_DEFICIT} kcal. "
                    "I suggest extending the timeframe or adjusting your goal."
                )
            )
        target_calories = tdee - daily_deficit
        min_allowed = MIN_CALORIES_MALE if req.sex == "M" else MIN_CALORIES_FEMALE
        if target_calories < min_allowed:
            return PlanResponseNotFeasible(
                feasible=False,
                reason=f"Target calories ({floor(target_calories)}) are below the healthy minimum ({min_allowed}).",
                values={
                    "tdee": floor(tdee),
                    "daily_deficit": floor(daily_deficit),
                    "type": "loss",
                },
                user_message=(
                    "Hello! The amount of calories you would need to consume to reach your goal "
                    "is too low and could be harmful to your health. "
                    "Please consider a more realistic goal or consult a professional."
                )
            )
        return PlanResponseFeasible(
            feasible=True,
            target_calories=floor(target_calories),
            type="loss",
            tdee=floor(tdee),
            daily_deficit=floor(daily_deficit),
            daily_surplus=None,
            days=days,
        )
    else:
        daily_surplus = daily_change
        if daily_surplus > MAX_SAFE_DAILY_SURPLUS:
            return PlanResponseNotFeasible(
                feasible=False,
                reason=f"Required daily surplus ({floor(daily_surplus)} kcal) is greater than the safe limit of {MAX_SAFE_DAILY_SURPLUS} kcal (not recommended).",
                values={
                    "tdee": floor(tdee),
                    "daily_surplus": floor(daily_surplus),
                    "type": "gain",
                },
                user_message=(
                    "Hello! The plan you propose implies a very rapid weight gain "
                    f"with a daily calorie surplus of {floor(daily_surplus)} kcal, "
                    f"which exceeds the recommended limit of {MAX_SAFE_DAILY_SURPLUS} kcal. "
                    "Consider a longer timeframe or a more moderate goal for your health."
                )
            )
        target_calories = tdee + daily_surplus
        return PlanResponseFeasible(
            feasible=True,
            target_calories=floor(target_calories),
            type="gain",
            tdee=floor(tdee),
            daily_deficit=None,
            daily_surplus=floor(daily_surplus),
            days=days,
        )
