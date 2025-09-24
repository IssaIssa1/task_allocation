import json
import os
from .models import ProblemInstance

def load_problem_instance(instance_id, base_path="."):
    """
    Loads a problem instance and its corresponding optimal solution from JSON files.

    This function expects the following directory structure:
    - {base_path}/problem_instances/problem_instance_1p_{id}.json
    - {base_path}/solutions/optimal_schedule_1p_{id}.json

    Args:
        instance_id (int): The six-digit ID of the problem instance.
        base_path (str): The root directory containing the dataset folders.

    Returns:
        A tuple (problem_data, solution_data).
        - problem_data (dict): The raw data from the problem instance JSON file.
        - solution_data (dict): The raw data from the solution JSON file.
        Returns (None, None) or (dict, None) if files are not found.
    """
    problem_filename = f"problem_instance_1p_{instance_id:06d}.json"
    solution_filename = f"optimal_schedule_1p_{instance_id:06d}.json"

    problem_filepath = os.path.join(base_path, "problem_instances", problem_filename)
    solution_filepath = os.path.join(base_path, "solutions", solution_filename)

    problem_data = None
    solution_data = None

    try:
        with open(problem_filepath, 'r') as f:
            problem_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Problem file not found at {problem_filepath}")
        return None, None

    try:
        with open(solution_filepath, 'r') as f:
            solution_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Solution file not found at {solution_filepath}")
        return problem_data, None

    return problem_data, solution_data

if __name__ == '__main__':
    # This block is for testing purposes.
    # The main benchmarking script is now in `main.py`.
    print("This script is intended to be used as a module.")
    print("Run `python3 main.py` to start the benchmark.")
