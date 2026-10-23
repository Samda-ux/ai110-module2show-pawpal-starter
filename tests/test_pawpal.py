from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    task = Task("Morning walk", 30)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Breakfast", 10))
    assert len(pet.tasks) == 1


# --- Shared setup ---------------------------------------------------------


def make_scheduler(*pets):
    """Build a Scheduler for an owner who has the given pets."""
    owner = Owner("Jordan")
    for pet in pets:
        owner.add_pet(pet)
    return Scheduler(owner)


# --- Sorting: tasks come back in chronological order ----------------------


def test_sort_by_time_returns_chronological_order():
    pet = Pet("Mochi", "dog")
    for t in ["09:00", "07:00", "12:30", "07:45"]:
        pet.add_task(Task(f"Task at {t}", 10, time=t))
    scheduler = make_scheduler(pet)

    times = [task.time for _, task in scheduler.sort_by_time()]

    assert times == ["07:00", "07:45", "09:00", "12:30"]


def test_sort_by_time_compares_as_clock_time_not_text():
    # As plain strings "10:00" < "7:30", which would be wrong.
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Late", 10, time="10:00"))
    pet.add_task(Task("Early", 10, time="7:30"))
    scheduler = make_scheduler(pet)

    assert [task.description for _, task in scheduler.sort_by_time()] == ["Early", "Late"]


def test_sort_by_time_puts_flexible_tasks_last():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Anytime", 10))
    pet.add_task(Task("Morning", 10, time="08:00"))
    scheduler = make_scheduler(pet)

    assert [task.description for _, task in scheduler.sort_by_time()] == ["Morning", "Anytime"]


# --- Recurrence: completing a repeating task queues the next one ----------


def test_completing_daily_task_creates_one_due_next_day():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", 30, frequency="daily"))
    scheduler = make_scheduler(pet)

    assert scheduler.complete_task("Mochi", "Walk") is True

    assert len(pet.tasks) == 2
    original, follow_up = pet.tasks
    assert original.completed is True
    assert follow_up.completed is False
    assert follow_up.due_date == date.today() + timedelta(days=1)


def test_completing_weekly_task_creates_one_due_in_seven_days():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Bath", 45, frequency="weekly"))
    scheduler = make_scheduler(pet)

    scheduler.complete_task("Mochi", "Bath")

    assert pet.tasks[-1].due_date == date.today() + timedelta(weeks=1)


def test_completing_once_task_does_not_recur():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Vet visit", 60, frequency="once"))
    scheduler = make_scheduler(pet)

    scheduler.complete_task("Mochi", "Vet visit")

    assert len(pet.tasks) == 1


def test_next_days_task_is_not_in_todays_plan():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", 30, frequency="daily"))
    scheduler = make_scheduler(pet)

    scheduler.complete_task("Mochi", "Walk")

    assert scheduler.generate_plan() == []


# --- Conflict detection: duplicate times are flagged ----------------------


def test_detect_conflicts_flags_same_time_for_same_pet():
    pet = Pet("Luna", "cat")
    pet.add_task(Task("Medication", 5, time="08:00"))
    pet.add_task(Task("Brush teeth", 5, time="08:00"))
    scheduler = make_scheduler(pet)

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "08:00" in warnings[0]
    assert "Medication" in warnings[0] and "Brush teeth" in warnings[0]


def test_detect_conflicts_flags_same_time_across_pets():
    mochi, luna = Pet("Mochi", "dog"), Pet("Luna", "cat")
    mochi.add_task(Task("Breakfast", 10, time="07:45"))
    luna.add_task(Task("Breakfast", 10, time="07:45"))
    scheduler = make_scheduler(mochi, luna)

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "Mochi" in warnings[0] and "Luna" in warnings[0]


def test_detect_conflicts_returns_empty_when_times_differ():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", 30, time="07:00"))
    pet.add_task(Task("Breakfast", 10, time="07:45"))
    pet.add_task(Task("Anytime", 10))  # no time set, can't conflict
    scheduler = make_scheduler(pet)

    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_ignores_completed_tasks():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", 30, time="07:00", frequency="once"))
    pet.add_task(Task("Feed", 10, time="07:00"))
    scheduler = make_scheduler(pet)

    scheduler.complete_task("Mochi", "Walk")

    assert scheduler.detect_conflicts() == []
