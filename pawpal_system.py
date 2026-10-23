"""PawPal+ logic layer: owner, pets, tasks, and the scheduler."""

from dataclasses import dataclass, field, replace
from datetime import date, timedelta

# Lower rank = scheduled first. Sorting on the raw strings would be alphabetical.
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}

# How far ahead the next copy of a recurring task is due. "once" tasks don't recur.
RECURRENCE = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


@dataclass
class Task:
    description: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    time: str | None = None  # preferred start "HH:MM", or None if flexible
    frequency: str = "daily"  # "once" | "daily" | "weekly"
    completed: bool = False
    due_date: date = field(default_factory=date.today)

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self) -> "Task | None":
        """Return a fresh copy due one interval later, or None for one-off tasks."""
        interval = RECURRENCE.get(self.frequency)
        if interval is None:
            return None
        return replace(self, completed=False, due_date=self.due_date + interval)

    def mark_incomplete(self) -> None:
        """Reset this task, e.g. for the next day of a recurring task."""
        self.completed = False


@dataclass
class Pet:
    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, description: str) -> None:
        """Remove the first task with the given description."""
        for i, task in enumerate(self.tasks):
            if task.description == description:
                del self.tasks[i]
                return


@dataclass
class Owner:
    name: str
    available_minutes: int = 120
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove the pet with the given name."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def get_pet(self, pet_name: str) -> Pet | None:
        """Look up a pet by name."""
        return next((p for p in self.pets if p.name == pet_name), None)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair so callers know which pet each task is for."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


@dataclass
class ScheduledTask:
    """One entry in a daily plan: a task placed at a time, with the reason it was chosen."""

    pet: Pet
    task: Task
    start_minute: int  # minutes from the start of the owner's day
    reason: str


def _to_minutes(hhmm: str) -> int:
    """Convert an "HH:MM" string to minutes since midnight."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def _to_hhmm(minutes: int) -> str:
    """Convert minutes since midnight to an "HH:MM" string."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


class Scheduler:
    def __init__(self, owner: Owner):
        """Create a scheduler that plans the day for the given owner."""
        self.owner = owner
        self.plan: list[ScheduledTask] = []  # last generated plan, read by explain_plan()
        self.skipped: list[tuple[Pet, Task]] = []  # tasks that didn't fit the time budget

    def get_pending_tasks(self, day: date | None = None) -> list[tuple[Pet, Task]]:
        """Incomplete tasks due on or before `day` (default today), across every pet."""
        day = day or date.today()
        return [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if not task.completed and task.due_date <= day
        ]

    def sort_by_time(self, tasks: list[tuple[Pet, Task]] | None = None) -> list[tuple[Pet, Task]]:
        """Order tasks by their "HH:MM" time, earliest first; flexible tasks go last."""
        tasks = self.owner.get_all_tasks() if tasks is None else tasks
        # Converting to minutes keeps "7:30" before "10:00", which plain string sorting would not.
        return sorted(tasks, key=lambda pt: _to_minutes(pt[1].time) if pt[1].time else float("inf"))

    def filter_tasks(
        self, pet_name: str | None = None, completed: bool | None = None
    ) -> list[tuple[Pet, Task]]:
        """Return tasks matching a pet name and/or completion status; None means "any"."""
        return [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if (pet_name is None or pet.name == pet_name)
            and (completed is None or task.completed == completed)
        ]

    def sort_tasks(self, tasks: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        """Order by priority, then preferred time (timed tasks first), then shortest first."""
        return sorted(
            tasks,
            key=lambda pt: (
                PRIORITY_RANK.get(pt[1].priority, len(PRIORITY_RANK)),
                pt[1].time is None,
                pt[1].time or "",
                pt[1].duration_minutes,
            ),
        )

    def detect_conflicts(self) -> list[str]:
        """Return a warning for each time slot that has more than one pending task.

        Lightweight check: only exact "HH:MM" matches count, not overlapping durations.
        Returns an empty list when there are no conflicts; never raises.
        """
        by_time: dict[str, list[tuple[Pet, Task]]] = {}
        for pet, task in self.get_pending_tasks():
            if task.time:
                by_time.setdefault(task.time, []).append((pet, task))

        warnings = []
        for time, tasks in sorted(by_time.items()):
            if len(tasks) > 1:
                names = ", ".join(f"{task.description} ({pet.name})" for pet, task in tasks)
                warnings.append(f"Conflict at {time}: {names}")
        return warnings

    def generate_plan(self) -> list[ScheduledTask]:
        """Pick and order tasks for the day within the owner's available time."""
        day_start = _to_minutes(self.owner.preferences.get("day_start", "08:00"))
        budget = self.owner.available_minutes
        used = 0
        chosen: list[tuple[Pet, Task]] = []
        self.skipped = []

        # Greedy: take the most important tasks first until the time budget runs out.
        for pet, task in self.sort_tasks(self.get_pending_tasks()):
            if used + task.duration_minutes <= budget:
                chosen.append((pet, task))
                used += task.duration_minutes
            else:
                self.skipped.append((pet, task))

        # Lay chosen tasks out in time order: preferred times first, flexible ones after.
        chosen = self.sort_by_time(chosen)
        self.plan = []
        clock = day_start
        for pet, task in chosen:
            if task.time:
                clock = max(clock, _to_minutes(task.time))
            reason = f"{task.priority} priority"
            if task.time:
                reason += f", preferred time {task.time}"
            self.plan.append(ScheduledTask(pet, task, clock - day_start, reason))
            clock += task.duration_minutes
        return self.plan

    def complete_task(self, pet_name: str, description: str) -> bool:
        """Mark a pet's open task done and queue its next occurrence if it recurs.

        Returns False if the pet has no open task with that description.
        """
        for pet, task in self.owner.get_all_tasks():
            if pet.name == pet_name and task.description == description and not task.completed:
                task.mark_complete()
                next_task = task.next_occurrence()
                if next_task:
                    pet.add_task(next_task)
                return True
        return False

    def explain_plan(self) -> str:
        """Describe why each task was chosen and where it landed in the plan."""
        if not self.plan:
            return "No tasks scheduled."
        day_start = _to_minutes(self.owner.preferences.get("day_start", "08:00"))
        lines = [f"Daily plan for {self.owner.name} ({self.owner.available_minutes} min available):"]
        for item in self.plan:
            start = _to_hhmm(day_start + item.start_minute)
            lines.append(
                f"  {start} - {item.task.description} for {item.pet.name} "
                f"({item.task.duration_minutes} min) [{item.reason}]"
            )
        for pet, task in self.skipped:
            lines.append(f"  Skipped: {task.description} for {pet.name} (not enough time left)")
        return "\n".join(lines)
