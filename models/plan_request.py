from pydantic import BaseModel, field_validator, ValidationInfo
from datetime import date

class PlanRequest(BaseModel):
    current_weight: float  # kg
    height: float          # cm
    target_weight: float   # kg
    target_date: date
    age: int
    sex: str  # "M" or "F"

    @field_validator("sex")
    def valid_sex(cls, v):
        if v.upper() not in ("M", "F"):
            raise ValueError("sex must be 'M' or 'F'")
        return v.upper()

    @field_validator("target_date")
    def future_date(cls, v):
        if v <= date.today():
            raise ValueError("target_date must be in the future")
        return v

    @field_validator("target_weight")
    def valid_target_weight(cls, v, info: ValidationInfo):
        current_weight = info.data.get("current_weight")  # access other fields
        if current_weight is not None:
            if v == current_weight:
                raise ValueError("target_weight cannot be equal to current_weight")
        return v
