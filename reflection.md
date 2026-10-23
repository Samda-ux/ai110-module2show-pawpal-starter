# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I started with four classes, each with one job

- Task: one care activity. It has attributes title, duration_minutes, priority, category, and completed. It has method mark_complete().
- Pet: has attributes name, species, age, and its own list of Tasks. It is responsible for adding and removing its tasks.
- Owner has attributes name, available_minutes (the daily time budget), preferences, and the list of Pets. It manages its pets and can collect tasks across all of them.
- Scheduler : scheduling logic. It takes an Owner, picks and orders tasks to fit the time budget generate_plan(), and describes the result (explain_plan()).

Relationships: an Owner has many Pets and a Pet has many Tasks (composition), and the Scheduler works on one Owner. I used dataclasses for the data-holding classes and kept the Scheduler as a plain class because it is behavior rather than data.

**b. Design changes**

After the first skeleton, I reviewed it for missing relationships and bottlenecks and made three changes:

1.Added a ScheduledTask dataclass. generate_plan() originally returned list[Task], which has nowhere to store a start time or the reason a task was picked, so explain_plan() would have had nothing to read. ScheduledTask holds the pet, the task, start_minute, and reason, and the Scheduler keeps its latest plan.
2.Owner.get_all_tasks() now returns (Pet, Task) pairs. A flat list of tasks loses which pet each task belongs to, and the plan needs to show that.
3.PRIORITY_RANK Priority is a string, and sorting "high"/"medium"/"low" directly would be alphabetical (high, low, medium). An explicit rank makes ordering correct.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
  My scheduler considered time and priority.
- How did you decide which constraints mattered most?
  Priority mattered the most because higher priority tasks like medication and eating are much more important than brushing and we could miss out on medication and eating in favor of brushing which is why priority mattered the most.
  **b. Tradeoffs**
- The time budget counts minutes of care, not hours on the clock. It does not check when the last task actually ends. The scheduler also uses a greedy pass instead of searching every combination.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
  I used it for design brainstorming, debugging, refactoring, helping my understanding, etc.
- What kinds of prompts or questions were most helpful?
  For specific tasks one shot prompts worked well.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
  Let the AI run on the code and it mistakenly changed a lot in README and reflection.
- How did you evaluate or verify what the AI suggested?
  Had to look through the code and ask the AI its thought process to evaluate and verify.

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
