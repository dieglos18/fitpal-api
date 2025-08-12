from math import floor
from datetime import date
from utils.calculate_bmr import calculate_bmr
from models.plan_responses import PlanResponseFeasible, PlanResponseNotFeasible
from constants.nutrition_constants import (
    KCAL_PER_KG,
    MAX_SAFE_DAILY_DEFICIT,
    MAX_SAFE_DAILY_SURPLUS,
    MIN_CALORIES_FEMALE,
    MIN_CALORIES_MALE,
)

def generate_plan(req):
    days = (req.target_date - date.today()).days
    if days <= 0:
        return PlanResponseNotFeasible(
            feasible=False,
            reason="The date must be in the future",
            values={},
            user_message="Hello! Unfortunately, the date you selected is not valid because it must be a future date. Please try another date."
        )

    bmr = calculate_bmr(req.current_weight, req.height, req.age, req.sex)
    tdee = bmr * 1.2

    weight_change = req.target_weight - req.current_weight
    total_kcal = abs(weight_change) * KCAL_PER_KG
    daily_change = total_kcal / days

    if weight_change < 0:
        return _handle_loss(daily_change, tdee, days, req.sex)
    else:
        return _handle_gain(daily_change, tdee, days)

def _handle_loss(daily_change, tdee, days, sex):
    daily_deficit = abs(daily_change)
    if daily_deficit > MAX_SAFE_DAILY_DEFICIT:
        return PlanResponseNotFeasible(
            feasible=False,
            reason=f"Required daily deficit ({floor(daily_deficit)} kcal) is greater than the safe limit of {MAX_SAFE_DAILY_DEFICIT} kcal.",
            values={"tdee": floor(tdee), "daily_deficit": floor(daily_deficit), "type": "loss"},
            user_message=(
                "Hello! The plan you propose is not healthy because "
                f"it requires a daily calorie deficit of {floor(daily_deficit)} kcal, "
                f"which exceeds the recommended limit of {MAX_SAFE_DAILY_DEFICIT} kcal."
            )
        )
    target_calories = tdee - daily_deficit
    min_allowed = MIN_CALORIES_MALE if sex == "M" else MIN_CALORIES_FEMALE
    if target_calories < min_allowed:
        return PlanResponseNotFeasible(
            feasible=False,
            reason=f"Target calories ({floor(target_calories)}) are below the healthy minimum ({min_allowed}).",
            values={"tdee": floor(tdee), "daily_deficit": floor(daily_deficit), "type": "loss"},
            user_message="The amount of calories is too low and could harm your health."
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

def _handle_gain(daily_change, tdee, days):
    daily_surplus = daily_change
    if daily_surplus > MAX_SAFE_DAILY_SURPLUS:
        return PlanResponseNotFeasible(
            feasible=False,
            reason=f"Required daily surplus ({floor(daily_surplus)} kcal) is greater than the safe limit of {MAX_SAFE_DAILY_SURPLUS} kcal.",
            values={"tdee": floor(tdee), "daily_surplus": floor(daily_surplus), "type": "gain"},
            user_message="The plan you propose implies a very rapid weight gain."
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
