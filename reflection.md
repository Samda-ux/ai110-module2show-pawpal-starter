# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I started with four classes, each with one job (UML in [diagrams/uml.mmd](diagrams/uml.mmd), code in [pawpal_system.py](pawpal_system.py)):

- **Task** (dataclass): one care activity. It holds `title`, `duration_minutes`, `priority`, `category`, and `completed`. Its only behavior is `mark_complete()`.
- **Pet** (dataclass): holds `name`, `species`, `age`, and its own list of `Task`s. It is responsible for adding and removing its tasks.
- **Owner** (dataclass): holds `name`, `available_minutes` (the daily time budget), `preferences`, and the list of `Pet`s. It manages its pets and can collect tasks across all of them.
- **Scheduler**: the only class with planning logic. It takes an `Owner`, picks and orders tasks to fit the time budget (`generate_plan()`), and describes the result (`explain_plan()`).

Relationships: an Owner has many Pets and a Pet has many Tasks (composition), and the Scheduler works on one Owner. I used dataclasses for the data-holding classes and kept the Scheduler as a plain class because it is behavior rather than data.

**b. Design changes**

After the first skeleton, I reviewed it for missing relationships and bottlenecks and made three changes:

1. **Added a `ScheduledTask` dataclass.** `generate_plan()` originally returned `list[Task]`, which has nowhere to store a start time or the reason a task was picked, so `explain_plan()` would have had nothing to read. `ScheduledTask` holds the pet, the task, `start_minute`, and `reason`, and the Scheduler keeps its latest `plan`.
2. **`Owner.get_all_tasks()` now returns `(Pet, Task)` pairs.** A flat list of tasks loses which pet each task belongs to, and the plan needs to show that.
3. **Added `PRIORITY_RANK`.** Priority is a string, and sorting `"high"/"medium"/"low"` directly would be alphabetical (high, low, medium). An explicit rank makes ordering correct.

Known limitation I left for later: `remove_task` and `remove_pet` match by name or title, so duplicates would be ambiguous. I'll revisit that when I implement the logic.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
