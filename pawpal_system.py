"""PawPal+ logic layer: owner, pets, tasks, and the scheduler."""

from dataclasses import dataclass, field

# Lower rank = scheduled first. Sorting on the raw strings would be alphabetical.
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    category: str = "general"  # e.g. walk, feeding, meds, grooming
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        pass

    def remove_task(self, title: str) -> None:
        """Remove the task with the given title."""
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int = 120
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        pass

    def remove_pet(self, pet_name: str) -> None:
        """Remove the pet with the given name."""
        pass

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair so callers know which pet each task is for."""
        pass


@dataclass
class ScheduledTask:
    """One entry in a daily plan: a task placed at a time, with the reason it was chosen."""

    pet: Pet
    task: Task
    start_minute: int  # minutes from the start of the owner's day
    reason: str


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.plan: list[ScheduledTask] = []  # last generated plan, read by explain_plan()

    def generate_plan(self) -> list[ScheduledTask]:
        """Pick and order tasks for the day within the owner's available time."""
        pass

    def explain_plan(self) -> str:
        """Describe why each task was chosen and where it landed in the plan."""
        pass
