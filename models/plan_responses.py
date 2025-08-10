from pydantic import BaseModel
from typing import Union

class PlanResponseFeasible(BaseModel):
    feasible: bool = True
    target_calories: int
    type: str  # "loss" or "gain"
    tdee: int
    days: int
    daily_deficit: int | None = None
    daily_surplus: int | None = None

class PlanResponseNotFeasible(BaseModel):
    feasible: bool = False
    reason: str
    values: dict
    user_message: str  # <- friendly message for the user

PlanResponse = Union[PlanResponseFeasible, PlanResponseNotFeasible]
