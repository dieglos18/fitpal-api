def calculate_bmr(weight_kg, height_cm, age_years, sex):
    if sex == "M":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age_years + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age_years - 161
