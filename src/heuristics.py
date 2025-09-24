from .models import ProblemInstance, Robot, Task
from typing import Dict, Any, List, Optional

def find_minimal_coalition(task: Task, robots: List[Robot]) -> Optional[List[Robot]]:
    """
    Finds a coalition of robots to perform a task.

    This function uses a greedy set-cover algorithm to find a sufficient
    coalition. It does not guarantee the smallest possible coalition (which is an
    NP-hard problem), but it finds a valid one if it exists.

    The logic is as follows:
    1. If a single robot has all required skills, return it.
    2. Otherwise, iteratively add the robot that covers the most remaining skills
       until all task requirements are met.

    Args:
        task: The task that needs a coalition.
        robots: A list of all robots in the problem.

    Returns:
        A list of `Robot` objects forming the coalition, or `None` if no valid
        coalition can be found from the given robots.
    """
    required_skills = task.requirements
    if not any(req == 1 for req in required_skills):
        return []  # No skills required, no coalition needed.

    # First, check if any single robot can perform the task.
    for robot in robots:
        if robot.has_skills(required_skills):
            return [robot]

    # If not, find a coalition using a greedy approach (set cover).
    uncovered_skills = set(i for i, req in enumerate(required_skills) if req == 1)
    coalition = []
    available_robots = list(robots)

    while uncovered_skills:
        best_robot = None
        skills_covered_by_best = set()

        # Find the robot that covers the most new skills.
        for robot in available_robots:
            covered_by_this_robot = uncovered_skills.intersection(
                i for i, skill in enumerate(robot.skills) if skill == 1
            )
            if len(covered_by_this_robot) > len(skills_covered_by_best):
                skills_covered_by_best = covered_by_this_robot
                best_robot = robot

        if best_robot:
            coalition.append(best_robot)
            uncovered_skills -= skills_covered_by_best
            available_robots.remove(best_robot)
        else:
            # If no robot can cover any of the remaining needed skills, a full coalition is not possible.
            return None

    return coalition


def greedy_heuristic(problem: ProblemInstance) -> Dict[str, Any]:
    """
    A coalition-aware greedy heuristic for the task allocation problem.

    This heuristic implements a list-scheduling algorithm. At each step, it
    evaluates all possible assignments of "ready" tasks to capable coalitions
    and greedily selects the assignment that results in the earliest finish time.

    The main loop continues until all tasks are scheduled. In each iteration:
    1. It identifies all tasks whose precedence constraints have been met.
    2. For each ready task, it finds a viable coalition of robots.
    3. It calculates the earliest possible finish time for this task-coalition pair.
    4. It selects the single best assignment (across all tasks and coalitions)
       and commits it to the schedule.
    """
    # --- State Tracking ---
    # robot_available_time: Tracks the time when each robot becomes free.
    # robot_current_location: Tracks the last completed task's ID for each robot.
    robot_available_time = [0.0] * problem.num_robots
    robot_current_location = [0] * problem.num_robots  # All start at the depot (task 0)

    # task_finish_times: A map of task ID to its completion time.
    tasks_to_schedule = problem.get_real_tasks()
    scheduled_task_ids = {0}
    task_finish_times = {0: 0.0}

    robot_schedules = {str(i): [] for i in range(problem.num_robots)}

    while len(tasks_to_schedule) > 0:
        best_assignment = None
        earliest_finish_time = float('inf')

        for task in tasks_to_schedule:
            predecessors = problem.precedence_constraints.get(task.id, [])
            if not all(p in scheduled_task_ids for p in predecessors):
                continue

            max_pred_finish_time = max((task_finish_times.get(p, 0) for p in predecessors), default=0.0)

            coalition = find_minimal_coalition(task, problem.robots)

            if coalition:
                # All robots in the coalition must be free and have traveled to the task location.
                # The time the coalition is ready is when the last robot arrives.
                coalition_arrival_times = [
                    robot_available_time[r.id] + problem.travel_times[robot_current_location[r.id]][task.id]
                    for r in coalition
                ]
                coalition_ready_time = max(coalition_arrival_times)

                start_time = max(coalition_ready_time, max_pred_finish_time)
                finish_time = start_time + task.execution_time

                if finish_time < earliest_finish_time:
                    earliest_finish_time = finish_time
                    best_assignment = {
                        "task": task,
                        "coalition": coalition,
                        "start_time": start_time,
                        "finish_time": finish_time,
                    }

        if best_assignment:
            task = best_assignment["task"]
            coalition = best_assignment["coalition"]
            start_time = best_assignment["start_time"]
            finish_time = best_assignment["finish_time"]

            # Update state for all robots in the coalition
            for robot in coalition:
                robot_available_time[robot.id] = finish_time
                robot_current_location[robot.id] = task.id
                robot_schedules[str(robot.id)].append({
                    "task": task.id,
                    "start_time": start_time,
                    "end_time": finish_time
                })

            scheduled_task_ids.add(task.id)
            task_finish_times[task.id] = finish_time
            tasks_to_schedule.remove(task)
        else:
            if tasks_to_schedule:
                print("Warning: Heuristic failed. Could not find a valid assignment for remaining tasks.")
            break

    makespan = max(robot_available_time) if robot_available_time else 0.0

    return {
        "makespan": makespan,
        "n_tasks": len(problem.get_real_tasks()),
        "n_robots": problem.num_robots,
        "robot_schedules": robot_schedules,
    }
