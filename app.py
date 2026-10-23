import re

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task, _to_hhmm, _to_minutes

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs")

# Keep the Owner in session_state so pets and tasks survive Streamlit's reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner = st.session_state.owner

owner.name = st.text_input("Owner name", value=owner.name)
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    if owner.get_pet(pet_name):
        st.warning(f"{pet_name} is already added.")
    else:
        owner.add_pet(Pet(pet_name, species))

if owner.pets:
    st.write("Pets: " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Give a task a preferred time to have it sorted and checked for conflicts.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
    task_pet = st.selectbox("For pet", [p.name for p in owner.pets])
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    task_time = st.text_input("Preferred time (HH:MM, optional)")
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])

if st.button("Add task"):
    task_time = task_time.strip() or None
    if task_pet is None:
        st.warning("Add a pet first.")
    elif task_time and not re.fullmatch(r"([01]?\d|2[0-3]):[0-5]\d", task_time):
        st.error("Preferred time must look like 07:30.")
    else:
        owner.get_pet(task_pet).add_task(
            Task(task_title, int(duration), priority, time=task_time, frequency=frequency)
        )
        st.success(f"Added '{task_title}' for {task_pet}.")

scheduler = Scheduler(owner)

if owner.get_all_tasks():
    # Conflict warnings come straight from the Scheduler.
    for warning in scheduler.detect_conflicts():
        st.warning(f"⚠️ {warning}")

    col1, col2 = st.columns(2)
    with col1:
        pet_filter = st.selectbox("Show pet", ["All pets"] + [p.name for p in owner.pets])
    with col2:
        status_filter = st.selectbox("Show status", ["All", "To do", "Done"])

    filtered = scheduler.filter_tasks(
        pet_name=None if pet_filter == "All pets" else pet_filter,
        completed={"All": None, "To do": False, "Done": True}[status_filter],
    )
    if filtered:
        st.table(
            [
                {
                    "Time": t.time or "flexible",
                    "Task": t.description,
                    "Pet": pet.name,
                    "Minutes": t.duration_minutes,
                    "Priority": t.priority,
                    "Repeats": t.frequency,
                    "Due": t.due_date.isoformat(),
                    "Status": "✅ done" if t.completed else "to do",
                }
                for pet, t in scheduler.sort_by_time(filtered)
            ]
        )
    else:
        st.info("No tasks match these filters.")

    open_tasks = scheduler.filter_tasks(completed=False)
    if open_tasks:
        col1, col2 = st.columns([3, 1])
        with col1:
            choice = st.selectbox(
                "Mark a task done",
                range(len(open_tasks)),
                format_func=lambda i: f"{open_tasks[i][1].description} ({open_tasks[i][0].name})",
            )
        with col2:
            st.write("")
            if st.button("Complete"):
                pet, task = open_tasks[choice]
                scheduler.complete_task(pet.name, task.description)
                st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
owner.available_minutes = int(
    st.number_input("Minutes available today", min_value=0, max_value=1440, value=owner.available_minutes)
)

if st.button("Generate schedule"):
    plan = scheduler.generate_plan()
    if plan:
        used = sum(item.task.duration_minutes for item in plan)
        st.success(f"Scheduled {len(plan)} task(s), {used} of {owner.available_minutes} minutes.")
        day_start = _to_minutes(owner.preferences.get("day_start", "08:00"))
        st.table(
            [
                {
                    "Start": _to_hhmm(day_start + item.start_minute),
                    "Task": item.task.description,
                    "Pet": item.pet.name,
                    "Minutes": item.task.duration_minutes,
                    "Why": item.reason,
                }
                for item in plan
            ]
        )
    else:
        st.info("Nothing to schedule today.")
    for pet, task in scheduler.skipped:
        st.warning(f"Skipped {task.description} for {pet.name}: not enough time left.")
