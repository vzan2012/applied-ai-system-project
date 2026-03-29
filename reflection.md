# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
  My initial design was to create five classes **Owner, Pet, Task, Scheduler and DailyPlan**. _Owner_ can have multiple pets. _Pet_ will have list of tasks, and _Scheduler_ organizes these components to generate daily schedule.
- What classes did you include, and what responsibilities did you assign to each?
  **Owner**: This class is the pet owner. Contains the owner name, pet collection, defining constraints like hours availability and preferences.
  **Pet**: This class will have attributes of pet name, species, list of tasks assigned to the pet and methods like getTasksByPriority().
  **Task**: This class with have the attributes of task name, task duration and task priority - _LOW, MEDIUM and High_.
  **Scheduler**: This will be responsible for organizing the schedule based on the constraints - _Owner, Pet, and Task_.  
  **DailyPlan**: This will have list of tasks - with assigned time slot and task description.

  **UML Diagram:**

  ```mermaid
  classDiagram
    class Owner {
      - ownerName: str
      - availableHoursPerDay: float
      - preferences: str
      - pets: List~Pet~
      + addPet(pet: Pet) void
      + removePet(petName: str) void
      + getPets() List~Pet~
    }

    class Pet {
      - petName: str
      - species: str
      - tasks: List~Task~
      + addTask(task: Task) void
      + removeTask(taskName: str) void
      + getTasksByPriority(priority: str) List~Task~
      + getAllTasks() List~Task~
    }

    class Task {
      - taskName: str
      - durationMinutes: int
      - priority: str
      + getPriority() str
      + getDuration() int
    }

    class Scheduler {
      + generateDailyPlan(owner: Owner, pet: Pet, availableTime: float) DailyPlan
      - sortTasksByPriority(tasks: List~Task~) List~Task~
      - checkTimeConstraints(tasks: List~Task~, availableTime: float) bool
    }

    class DailyPlan {
      - scheduledTasks: List~ScheduledTask~
      - totalTimeUsed: float
      - description: str
      + getSchedule() List~ScheduledTask~
    }

    class ScheduledTask {
        - task: Task
        - timeSlot: str
        - reasoning: str
        + getTask() Task
        + getTimeSlot() str
        + getReasoning() str
    }

    Owner "1" --> "*" Pet : owns
    Pet "1" --> "*" Task : has
    Scheduler --> DailyPlan : creates
    DailyPlan "*" --> "1..*" ScheduledTask : contains
    ScheduledTask --> Task : references
  ```

**Updated UML Diagram (Final Implementation):**

  ```mermaid
  classDiagram
    class Priority {
      <<enumeration>>
      LOW
      MEDIUM
      HIGH
    }

    class Species {
      <<enumeration>>
      DOG
      CAT
      OTHER
    }

    class TaskStatus {
      <<enumeration>>
      PENDING
      COMPLETED
      SKIPPED
    }

    class Frequency {
      <<enumeration>>
      ONCE
      DAILY
      WEEKLY
    }

    class Task {
      + task_name: str
      + duration_minutes: int
      + priority: Priority
      + status: TaskStatus
      + frequency: Frequency
      + due_date: date
      + get_priority() Priority
      + get_duration() int
      + mark_completed() Task
      + mark_skipped() void
      + reset() void
    }

    class Pet {
      + pet_name: str
      + species: Species
      + tasks: List~Task~
      + add_task(task: Task) void
      + remove_task(task_name: str) void
      + get_tasks_by_priority(priority: Priority) List~Task~
      + get_all_tasks() List~Task~
      + get_pending_tasks() List~Task~
    }

    class Owner {
      + owner_name: str
      + available_hours_per_day: float
      + preferences: str
      + pets: List~Pet~
      + add_pet(pet: Pet) void
      + remove_pet(pet_name: str) void
      + get_pets() List~Pet~
      + get_all_tasks_from_all_pets() List~Task~
      + get_pending_tasks_from_all_pets() List~Task~
      + get_tasks_by_status(status: TaskStatus) List~Task~
      + get_tasks_by_pet(pet_name: str) List~Task~
    }

    class ScheduledTask {
      + task: Task
      + time_slot: str
      + reasoning: str
      + get_task() Task
      + get_time_slot() str
      + get_reasoning() str
    }

    class DailyPlan {
      + scheduled_tasks: List~ScheduledTask~
      + total_time_used: float
      + description: str
      + get_schedule() List~ScheduledTask~
      + add_scheduled_task(st: ScheduledTask) void
      + calculate_total_time() float
    }

    class Scheduler {
      + PRIORITY_WEIGHTS: dict
      + generate_daily_plan(owner: Owner, pet: Pet, available_time: float) DailyPlan
      + sort_by_time(scheduled_tasks: List~ScheduledTask~) List~ScheduledTask~
      + detect_conflicts(scheduled_tasks: List~ScheduledTask~) List~str~
    }

    Owner "1" --> "*" Pet : owns
    Pet "1" --> "*" Task : has
    ScheduledTask --> Task : wraps
    DailyPlan "1" --> "*" ScheduledTask : contains
    Scheduler --> DailyPlan : creates
    Scheduler --> Owner : reads
    Scheduler --> Pet : reads
    Task --> Priority : uses
    Task --> TaskStatus : uses
    Task --> Frequency : uses
    Pet --> Species : uses
  ```

**b. Design changes**

- Did your design change during implementation?
  Yes, several refinements were identified during code skeleton review and implementation planning.
- If yes, describe at least one change and why you made it.
  **Change 1**: Removed the `getExplanation()` method and replaced it with a `description` attribute.
  **Why**: The description is generated once by the Scheduler and remains static. Storing it as an attribute is simpler and more efficient than using a method.

  **Change 2 (Identified for future implementation)**: Code review revealed several features needed for production:
  - **Task Status**: Tasks need states (PENDING, COMPLETED, SKIPPED) to track progress through the day.
  - **Recurring Tasks**: "Morning walk" happens daily, but current model treats tasks as one-time only. Need `is_recurring` and `recurrence_pattern` fields.
  - **Date Tracking**: DailyPlan should store what date the schedule is for to support multi-day planning.
  - **Scheduler Scope**: Currently generates plan for one pet, but Owner has many. Should consider handling all pets simultaneously.

  **Decision**: These enhancements are identified but will be prioritized and added during implementation based on testing requirements.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
  I have created the Scheduler that considers these constraints - **time**, **priority levels** and **task status**.
  -
  - **priority levels** with _HIGH_, _MEDIUM_ and _LOW_ levels determine the order of tasks to be scheduled.
  - **task status** - scheduling only Pending tasks.

- How did you decide which constraints mattered most?
  Time and priority are the most important ones and focused on it.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
  I have used the `detect_conflicts()` method to check the task pair for overlaps but gets slower as the task increases.
- Why is that tradeoff reasonable for this scenario?
  It can able to handle few tasks per pet.

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
