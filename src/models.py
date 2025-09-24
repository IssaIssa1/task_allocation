from typing import List, Dict, Tuple

class Task:
    """
    Represents a single task, storing all its properties.

    Attributes:
        id (int): The unique identifier for the task.
        execution_time (float): The time required to complete the task once started.
        location (Tuple[int, int]): The (x, y) coordinates of the task.
        requirements (List[int]): A binary vector of skill requirements.
        is_dummy (bool): True if the task is a dummy start/end node.
    """
    def __init__(self, task_id: int, execution_time: float, location: Tuple[int, int], requirements: List[int], is_dummy: bool = False):
        self.id = task_id
        self.execution_time = execution_time
        self.location = location
        self.requirements = requirements
        self.is_dummy = is_dummy

class Robot:
    """
    Represents a single robot and its capabilities.

    Attributes:
        id (int): The unique identifier for the robot.
        skills (List[int]): A binary vector representing the skills possessed by the robot.
    """
    def __init__(self, robot_id: int, skills: List[int]):
        self.id = robot_id
        self.skills = skills

    def has_skills(self, required_skills: List[int]) -> bool:
        """
        Checks if the robot's skills are sufficient for a given requirement vector.
        """
        for i in range(len(required_skills)):
            if required_skills[i] == 1 and self.skills[i] == 0:
                return False
        return True

class ProblemInstance:
    """
    A container for a complete problem instance.

    This class parses the raw dictionary from the JSON file into a structured,
    object-oriented representation, making the data easier to work with.

    Attributes:
        tasks (List[Task]): A list of all tasks, including dummy nodes.
        robots (List[Robot]): A list of all robots.
        travel_times (List[List[float]]): A matrix of travel times between all tasks.
        precedence_constraints (Dict[int, List[int]]): A mapping of a task to its predecessors.
    """
    def __init__(self, data: Dict):
        self.tasks: List[Task] = []
        self.robots: List[Robot] = []
        self.travel_times: List[List[float]] = data.get("T_t", [])
        self.precedence_constraints: Dict[int, List[int]] = {}  # task -> list of predecessors

        # Process precedence constraints
        for pre, suc in data.get("precedence_constraints", []):
            if suc not in self.precedence_constraints:
                self.precedence_constraints[suc] = []
            self.precedence_constraints[suc].append(pre)

        task_data = data.get("T_e", [])
        task_locations = data.get("task_locations", [])
        task_requirements = data.get("R", [])

        # The first task (id 0) is a dummy start task.
        # The README mentions M+2 tasks, implying the last is also a dummy.
        num_tasks_total = len(task_data)
        for i in range(num_tasks_total):
            # Mark first and last tasks as dummies
            is_dummy = (i == 0 or (i == num_tasks_total - 1 and num_tasks_total > 1))
            task = Task(
                task_id=i,
                execution_time=task_data[i],
                location=tuple(task_locations[i]),
                requirements=task_requirements[i],
                is_dummy=is_dummy
            )
            self.tasks.append(task)

        robot_data = data.get("Q", [])
        for i in range(len(robot_data)):
            robot = Robot(
                robot_id=i,
                skills=robot_data[i]
            )
            self.robots.append(robot)

    @property
    def num_robots(self) -> int:
        return len(self.robots)

    def get_real_tasks(self) -> List[Task]:
        """Returns a list of all non-dummy tasks."""
        return [t for t in self.tasks if not t.is_dummy]
