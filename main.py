"""Temporary testing ground: build an owner with pets and print today's schedule."""

from pawpal_system import Owner, Pet, Scheduler, Task


def print_tasks(title: str, tasks: list) -> None:
    """Print (pet, task) pairs as aligned rows under a heading."""
    print(f"\n{title}")
    print("-" * 50)
    if not tasks:
        print("  (none)")
    for pet, task in tasks:
        status = "done" if task.completed else "todo"
        print(
            f"  {task.time or 'any':>5}  {task.description:<16} {pet.name:<6} "
            f"{task.frequency:<7} due {task.due_date}  [{status}]"
        )


def main() -> None:
    owner = Owner("Jordan", available_minutes=90, preferences={"day_start": "07:00"})

    mochi = Pet("Mochi", "dog", age=3)
    luna = Pet("Luna", "cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Added deliberately out of time order to exercise sort_by_time().
    luna.add_task(Task("Play session", 15, "medium", time="09:00"))
    mochi.add_task(Task("Brush coat", 20, "low"))
    luna.add_task(Task("Give medication", 5, "high", time="08:00"))
    mochi.add_task(Task("Morning walk", 30, "high", time="07:00"))
    mochi.add_task(Task("Bath", 45, "low", frequency="weekly"))
    luna.add_task(Task("Breakfast", 10, "high", time="07:45"))
    # Two deliberate clashes: same pet at 08:00, and different pets at 07:45.
    luna.add_task(Task("Brush teeth", 5, "medium", time="08:00"))
    mochi.add_task(Task("Breakfast", 10, "high", time="07:45"))

    scheduler = Scheduler(owner)

    print_tasks("All tasks, in the order they were added", owner.get_all_tasks())
    print_tasks("Sorted by time", scheduler.sort_by_time())
    print_tasks("Only Luna's tasks", scheduler.filter_tasks(pet_name="Luna"))

    # Completing recurring tasks queues their next occurrence automatically.
    scheduler.complete_task("Mochi", "Morning walk")  # daily  -> due tomorrow
    scheduler.complete_task("Mochi", "Bath")  # weekly -> due in 7 days
    print_tasks("Completed tasks", scheduler.filter_tasks(completed=True))
    print_tasks("Mochi's tasks after completing two recurring ones", scheduler.filter_tasks(pet_name="Mochi"))

    print("\nConflict check")
    print("-" * 50)
    conflicts = scheduler.detect_conflicts()
    for warning in conflicts:
        print(f"  WARNING: {warning}")
    if not conflicts:
        print("  No conflicts found.")

    scheduler.generate_plan()
    print("\n" + "=" * 50)
    print("Today's Schedule".center(50))
    print("=" * 50)
    print(scheduler.explain_plan())
    print("=" * 50)


if __name__ == "__main__":
    main()
