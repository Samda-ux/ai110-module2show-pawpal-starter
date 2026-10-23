# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Output of `python main.py`:

```
==================================================
                 Today's Schedule
==================================================
Daily plan for Jordan (90 min available):
  07:00 - Morning walk for Mochi (30 min) [high priority, preferred time 07:00]
  07:45 - Breakfast for Luna (10 min) [high priority, preferred time 07:45]
  08:00 - Give medication for Luna (5 min) [high priority, preferred time 08:00]
  09:00 - Play session for Luna (15 min) [medium priority, preferred time 09:00]
  09:15 - Brush coat for Mochi (20 min) [low priority]
  Skipped: Bath for Mochi (not enough time left)
==================================================
```

## 🧪 Testing PawPal+

```bash
# Activate the virtual environment first (Windows: .venv\Scripts\activate)
python -m pytest
```

I tested basic functions like checking task count and marking tasks complete. I tested sort functions that sort tasks in chronological order, tasks with no set time going to the end and making that the tasks are sorted correctly. Made sure repeating tasks are all done like tomorrow not in today, one time tasks, adding weekly and daily copies. I also detected coflicts of two pets at the same time and made sure finished tasks and tasks at different time do not give conflicts.
\*\*\*\* 4 stars

# Test output:

collected 13 items

tests\test_pawpal.py ............. [100%]

========== 13 passed in 0.05s ===========

## 📐 Smarter Scheduling

| Feature           | Method(s)                           | Notes                                              |
| ----------------- | ----------------------------------- | -------------------------------------------------- |
| Task sorting      | sort_tasks(), sort_by_time()        | By priority, or by "HH:MM" time                    |
| Filtering         | filter_tasks(), get_pending_tasks() | By pet or status; skips tasks over the time budget |
| Conflict handling | detect_conflicts()                  | Warns on same-time tasks (exact match only)        |
| Recurring tasks   | complete_task(), next_occurrence()  | Daily = +1 day, weekly = +7 days                   |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. Run streamlit run app.py and open the link it prints
2. Enter an owner name, pet name and species. Than click add pet.
3. Add in taks by filling in a title, duration, priority, the pet name, and preffered time and frequency. Click add task
4. Adjust show pet to see what pet needs to be used and show status to see whether you wanna see all, done or to do tasks.
5. Click generate schedule to schedule all the tasks and see what times are alloted.

**Screenshot or video** _(optional)_: <!-- Insert a screenshot or link to a demo video here -->

```

```
