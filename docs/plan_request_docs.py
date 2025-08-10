plan_description = """
Receives the user's current weight, height, age, sex, and target date for achieving a desired weight. 
Calculates a safe daily calorie intake plan to help reach the goal in a healthy timeframe.

**Parameters:**
- `current_weight` (float, kg): Your current body weight in kilograms.
- `height` (float, cm): Your height in centimeters.
- `age` (int): Your age in years.
- `sex` (string): Your biological sex, use 'M' for male or 'F' for female.
- `target_weight` (float, kg): The weight you want to achieve in kilograms.
- `target_date` (date, YYYY-MM-DD): The future date by which you want to reach your target weight.

Make sure the `target_date` is a future date, and that the target weight is different from your current weight. 
The API will validate these inputs and return a calorie plan if the goal is achievable and safe.
"""

plan_example_body = {
    "current_weight": 80.0,
    "height": 180.0,
    "age": 30,
    "sex": "M",
    "target_weight": 75.0,
    "target_date": "2025-12-31"
}
