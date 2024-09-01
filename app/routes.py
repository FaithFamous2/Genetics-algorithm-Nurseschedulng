from flask import Blueprint, render_template, request, jsonify
from datetime import datetime, timedelta
from .genetic_algorithm import GeneticAlgorithm  # Assuming this is your GA module
from .models import save_schedule_to_db

main = Blueprint('main', __name__)

# Define the mapping from day names to weekday numbers
day_to_weekday = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6
}

# Function to normalize day names


def normalize_day_name(day):
    """Normalize day name to match the full form (e.g., 'Mon' -> 'Monday')."""
    day = day.strip().capitalize(
    )  # Remove leading/trailing spaces and capitalize the first letter
    abbreviations = {
        "Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday",
        "Thu": "Thursday", "Fri": "Friday", "Sat": "Saturday", "Sun": "Sunday"
    }
    if day in day_to_weekday:
        return day  # Already a full day name
    elif day in abbreviations:
        return abbreviations[day]  # Convert abbreviation to full day name
    else:
        raise ValueError(f"Invalid day name: {day}")


def get_dates_for_days(start_date, days):
    """Returns a dictionary mapping days to their respective dates."""
    day_map = {}

    # Normalize day names and create a map from each day to the next occurrence of that day
    for day in days:
        try:
            normalized_day = normalize_day_name(day)
            days_ahead = (
                7 + (day_to_weekday[normalized_day] - start_date.weekday())) % 7
            target_date = start_date + timedelta(days=days_ahead)
            day_map[normalized_day] = target_date.strftime(
                "%Y-%m-%d")  # Date formatting as needed
        except ValueError as e:
            # Return error if day name is invalid
            return jsonify({"error": str(e)}), 400

    return day_map

# Your route definitions


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/generate_schedule', methods=['POST'])
def generate_schedule():
    data = request.get_json()

    # Parse form data
    days = data.get('days')
    shifts = data.get('shifts')
    nurses = {
        "Head Nurse": data.get('head_nurses', '').split(','),
        "Junior Nurse": data.get('junior_nurses', '').split(',')
    }
    min_head_nurses_per_shift = int(data.get('min_head_nurses', 1))
    population_size = int(data.get('population_size', 50))
    max_generations = int(data.get('max_generations', 100))
    crossover_rate = float(data.get('crossover_rate', 0.8))
    mutation_rate = float(data.get('mutation_rate', 0.1))

    # Initialize Genetic Algorithm
    ga = GeneticAlgorithm(
        nurses, days, shifts, min_head_nurses_per_shift,
        population_size, max_generations,
        crossover_rate, mutation_rate
    )

    # Run GA to generate the schedule
    best_schedule = ga.run()

    # Save the schedule to the database
    save_schedule_to_db(best_schedule)

    # Calculate the start date for the schedule
    today = datetime.now()
    start_date = today + \
        timedelta(days=(7 - today.weekday() if today.weekday() > 0 else 0))
    dates_map = get_dates_for_days(start_date, days)

    # Formatting the schedule for the frontend
    formatted_schedule = {}
    for day in days:
        formatted_schedule[day] = {}
        for shift in shifts:
            formatted_schedule[day][shift] = {
                "Head Nurse": best_schedule.get(day, {}).get(shift, {}).get('Head Nurse', []),
                "Junior Nurse": best_schedule.get(day, {}).get(shift, {}).get('Junior Nurse', [])
            }

    # Return the formatted schedule as a JSON response
    print(formatted_schedule)
    return jsonify({'schedule': formatted_schedule})
