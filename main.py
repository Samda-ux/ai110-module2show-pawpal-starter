"""Temporary testing ground: build an owner with pets and print today's schedule."""

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    owner = Owner("Jordan", available_minutes=90, preferences={"day_start": "07:00"})

    mochi = Pet("Mochi", "dog", age=3)
    luna = Pet("Luna", "cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("Morning walk", 30, "high", time="07:00"))
    mochi.add_task(Task("Brush coat", 20, "low"))
    luna.add_task(Task("Breakfast", 10, "high", time="07:45"))
    luna.add_task(Task("Give medication", 5, "high", time="08:00"))
    luna.add_task(Task("Play session", 15, "medium", time="09:00"))
    mochi.add_task(Task("Bath", 45, "low", frequency="weekly"))

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    print("=" * 50)
    print("Today's Schedule".center(50))
    print("=" * 50)
    print(scheduler.explain_plan())
    print("=" * 50)


if __name__ == "__main__":
    main()
