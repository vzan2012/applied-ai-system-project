"""
PawPal+ System Tests
Unit tests for core scheduling functionality using pytest.
Run with: python -m pytest tests/test_pawpal.py -v
"""

import pytest
from datetime import date, timedelta
from pawpal_system import (
    Owner, Pet, Task, Scheduler, Priority, Species,
    TaskStatus, Frequency, DailyPlan, ScheduledTask
)


class TestTask:
    """Test Task class functionality"""

    def test_task_creation(self):
        """Verify task can be created with correct attributes"""
        task = Task("Morning walk", 20, Priority.HIGH)
        assert task.task_name == "Morning walk"
        assert task.duration_minutes == 20
        assert task.priority == Priority.HIGH
        assert task.status == TaskStatus.PENDING

    def test_task_completion(self):
        """Verify that calling mark_completed() changes task status to COMPLETED"""
        task = Task("Breakfast", 10, Priority.MEDIUM)

        # Initially should be PENDING
        assert task.status == TaskStatus.PENDING

        # After marking complete
        task.mark_completed()
        assert task.status == TaskStatus.COMPLETED

    def test_task_skip(self):
        """Verify that calling mark_skipped() changes task status to SKIPPED"""
        task = Task("Playtime", 30, Priority.HIGH)

        task.mark_skipped()
        assert task.status == TaskStatus.SKIPPED

    def test_task_reset(self):
        """Verify that calling reset() returns task to PENDING status"""
        task = Task("Walk", 20, Priority.MEDIUM)
        task.mark_completed()

        task.reset()
        assert task.status == TaskStatus.PENDING

    def test_get_priority(self):
        """Verify get_priority() returns correct priority"""
        task = Task("Task", 15, Priority.HIGH)
        assert task.get_priority() == Priority.HIGH

    def test_get_duration(self):
        """Verify get_duration() returns correct duration"""
        task = Task("Task", 25, Priority.LOW)
        assert task.get_duration() == 25


class TestPet:
    """Test Pet class functionality"""

    def test_pet_creation(self):
        """Verify pet can be created with correct attributes"""
        pet = Pet("Mochi", Species.DOG)
        assert pet.pet_name == "Mochi"
        assert pet.species == Species.DOG
        assert len(pet.get_all_tasks()) == 0

    def test_task_addition(self):
        """Verify that adding a task to a Pet increases that pet's task count"""
        pet = Pet("Whiskers", Species.CAT)
        initial_count = len(pet.get_all_tasks())

        task = Task("Nap", 20, Priority.LOW)
        pet.add_task(task)

        # Task count should increase by 1
        assert len(pet.get_all_tasks()) == initial_count + 1
        assert task in pet.get_all_tasks()

    def test_add_multiple_tasks(self):
        """Verify adding multiple tasks"""
        pet = Pet("Buddy", Species.DOG)

        task1 = Task("Walk", 20, Priority.HIGH)
        task2 = Task("Eat", 10, Priority.MEDIUM)
        task3 = Task("Play", 30, Priority.HIGH)

        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)

        assert len(pet.get_all_tasks()) == 3

    def test_remove_task(self):
        """Verify removing a task decreases task count"""
        pet = Pet("Max", Species.DOG)
        task = Task("Fetch", 15, Priority.MEDIUM)
        pet.add_task(task)

        assert len(pet.get_all_tasks()) == 1

        pet.remove_task("Fetch")
        assert len(pet.get_all_tasks()) == 0

    def test_get_tasks_by_priority(self):
        """Verify filtering tasks by priority"""
        pet = Pet("Luna", Species.CAT)

        high_task = Task("Important", 20, Priority.HIGH)
        medium_task = Task("Normal", 15, Priority.MEDIUM)
        low_task = Task("Optional", 10, Priority.LOW)

        pet.add_task(high_task)
        pet.add_task(medium_task)
        pet.add_task(low_task)

        high_priority_tasks = pet.get_tasks_by_priority(Priority.HIGH)
        assert len(high_priority_tasks) == 1
        assert high_priority_tasks[0].task_name == "Important"

    def test_get_pending_tasks(self):
        """Verify getting only pending tasks"""
        pet = Pet("Charlie", Species.DOG)

        task1 = Task("Task 1", 10, Priority.HIGH)
        task2 = Task("Task 2", 15, Priority.MEDIUM)
        task3 = Task("Task 3", 20, Priority.LOW)

        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)

        # All should be pending initially
        assert len(pet.get_pending_tasks()) == 3

        # Mark one as completed
        task1.mark_completed()
        assert len(pet.get_pending_tasks()) == 2


class TestOwner:
    """Test Owner class functionality"""

    def test_owner_creation(self):
        """Verify owner can be created"""
        owner = Owner("Jordan", 8.5)
        assert owner.owner_name == "Jordan"
        assert owner.available_hours_per_day == 8.5
        assert len(owner.get_pets()) == 0

    def test_add_pet(self):
        """Verify adding a pet to owner"""
        owner = Owner("Sarah", 8.0)
        pet = Pet("Mochi", Species.DOG)

        owner.add_pet(pet)
        assert len(owner.get_pets()) == 1
        assert pet in owner.get_pets()

    def test_remove_pet(self):
        """Verify removing a pet from owner"""
        owner = Owner("Alex", 7.0)
        pet = Pet("Whiskers", Species.CAT)

        owner.add_pet(pet)
        assert len(owner.get_pets()) == 1

        owner.remove_pet("Whiskers")
        assert len(owner.get_pets()) == 0

    def test_get_all_tasks_from_all_pets(self):
        """Verify retrieving all tasks from all pets"""
        owner = Owner("Jordan", 8.0)

        # Create two pets with tasks
        dog = Pet("Mochi", Species.DOG)
        dog.add_task(Task("Walk", 20, Priority.HIGH))
        dog.add_task(Task("Eat", 10, Priority.MEDIUM))

        cat = Pet("Whiskers", Species.CAT)
        cat.add_task(Task("Play", 15, Priority.HIGH))

        owner.add_pet(dog)
        owner.add_pet(cat)

        all_tasks = owner.get_all_tasks_from_all_pets()
        assert len(all_tasks) == 3


class TestScheduler:
    """Test Scheduler class functionality"""

    def test_scheduler_creation(self):
        """Verify scheduler can be created"""
        scheduler = Scheduler()
        assert scheduler is not None
        assert hasattr(scheduler, 'PRIORITY_WEIGHTS')

    def test_generate_daily_plan_basic(self):
        """Verify scheduler generates a daily plan"""
        owner = Owner("Jordan", 8.0)
        pet = Pet("Mochi", Species.DOG)

        pet.add_task(Task("Walk", 20, Priority.HIGH))
        pet.add_task(Task("Eat", 10, Priority.MEDIUM))

        scheduler = Scheduler()
        plan = scheduler.generate_daily_plan(owner, pet, 8.0)

        assert isinstance(plan, DailyPlan)
        assert len(plan.get_schedule()) > 0

    def test_equal_priority_preserves_insertion_order(self):
        """Tasks with equal priority should be scheduled in insertion order."""
        owner = Owner("Jordan", 8.0)
        pet = Pet("Mochi", Species.DOG)
        pet.add_task(Task("Morning walk", 20, Priority.HIGH))
        pet.add_task(Task("Breakfast", 30, Priority.HIGH))
        pet.add_task(Task("Evening walk", 30, Priority.HIGH))

        plan = Scheduler().generate_daily_plan(owner, pet, 8.0)
        names = [st.get_task().task_name for st in plan.get_schedule()]
        assert names == ["Morning walk", "Breakfast", "Evening walk"]

    def test_scheduler_priority_sorting(self):
        """Verify scheduler sorts tasks by priority (HIGH first)"""
        owner = Owner("Sarah", 5.0)
        pet = Pet("Whiskers", Species.CAT)

        # Add tasks in wrong priority order
        pet.add_task(Task("Low priority task", 10, Priority.LOW))
        pet.add_task(Task("High priority task", 15, Priority.HIGH))
        pet.add_task(Task("Medium priority task", 10, Priority.MEDIUM))

        scheduler = Scheduler()
        plan = scheduler.generate_daily_plan(owner, pet, 5.0)

        # First scheduled task should be HIGH priority
        first_task = plan.get_schedule()[0].get_task()
        assert first_task.priority == Priority.HIGH

    def test_scheduler_respects_time_constraints(self):
        """Verify scheduler respects available time constraint"""
        owner = Owner("Alex", 1.0)  # Only 1 hour available
        pet = Pet("Buddy", Species.DOG)

        # Add tasks totaling more than 1 hour
        pet.add_task(Task("Task 1", 30, Priority.LOW))
        pet.add_task(Task("Task 2", 30, Priority.LOW))
        pet.add_task(Task("Task 3", 30, Priority.HIGH))

        scheduler = Scheduler()
        plan = scheduler.generate_daily_plan(owner, pet, 1.0)

        # Should fit within 60 minutes
        assert plan.total_time_used <= 60

    def test_plan_no_tasks(self):
        """Verify scheduler handles pet with no tasks"""
        owner = Owner("Jordan", 8.0)
        pet = Pet("Empty", Species.DOG)

        scheduler = Scheduler()
        plan = scheduler.generate_daily_plan(owner, pet, 8.0)

        assert len(plan.get_schedule()) == 0
        assert "No pending tasks" in plan.description


class TestIntegration:
    """Integration tests for full workflow"""

    def test_full_workflow(self):
        """Test complete workflow: create owner, pets, tasks, and generate schedule"""
        # Create owner
        owner = Owner("Jordan", 8.0, "Prefers mornings")

        # Create pets
        dog = Pet("Mochi", Species.DOG)
        cat = Pet("Whiskers", Species.CAT)
        owner.add_pet(dog)
        owner.add_pet(cat)

        # Add tasks
        dog.add_task(Task("Morning walk", 20, Priority.HIGH))
        dog.add_task(Task("Breakfast", 10, Priority.MEDIUM))
        dog.add_task(Task("Play", 30, Priority.HIGH))

        cat.add_task(Task("Breakfast", 5, Priority.MEDIUM))
        cat.add_task(Task("Play", 20, Priority.HIGH))

        # Generate schedules
        scheduler = Scheduler()
        dog_plan = scheduler.generate_daily_plan(owner, dog, 8.0)
        cat_plan = scheduler.generate_daily_plan(owner, cat, 8.0)

        # Verify
        assert len(owner.get_pets()) == 2
        assert len(owner.get_all_tasks_from_all_pets()) == 5
        assert dog_plan.total_time_used > 0
        assert cat_plan.total_time_used > 0

    def test_task_lifecycle(self):
        """Test complete task lifecycle: create, schedule, complete"""
        pet = Pet("Mochi", Species.DOG)
        task = Task("Walk", 20, Priority.HIGH)

        # Add task
        pet.add_task(task)
        assert task in pet.get_pending_tasks()

        # Mark complete
        task.mark_completed()
        assert task not in pet.get_pending_tasks()
        assert task.status == TaskStatus.COMPLETED


class TestSortByTime:
    """Verify sort_by_time() returns ScheduledTasks in chronological order."""

    def _make_scheduled_task(self, name: str, time_slot: str) -> ScheduledTask:
        task = Task(name, 30, Priority.MEDIUM)
        return ScheduledTask(task, time_slot, "test")

    # --- Happy paths ---

    def test_sort_out_of_order_tasks(self):
        """Tasks given in random order should come back sorted earliest-first."""
        scheduler = Scheduler()
        tasks = [
            self._make_scheduled_task("Lunch",     "12:00 - 12:30"),
            self._make_scheduled_task("Walk",      "08:00 - 08:30"),
            self._make_scheduled_task("Medication","10:00 - 10:15"),
        ]
        sorted_tasks = scheduler.sort_by_time(tasks)
        time_slots = [st.get_time_slot() for st in sorted_tasks]
        assert time_slots == ["08:00 - 08:30", "10:00 - 10:15", "12:00 - 12:30"]

    def test_sort_already_ordered_tasks(self):
        """Tasks already in order should remain unchanged."""
        scheduler = Scheduler()
        tasks = [
            self._make_scheduled_task("Walk",  "08:00 - 08:30"),
            self._make_scheduled_task("Lunch", "12:00 - 12:30"),
        ]
        sorted_tasks = scheduler.sort_by_time(tasks)
        assert sorted_tasks[0].get_time_slot() == "08:00 - 08:30"
        assert sorted_tasks[1].get_time_slot() == "12:00 - 12:30"

    # --- Edge cases ---

    def test_sort_single_task_unchanged(self):
        """A list with one task should be returned as-is."""
        scheduler = Scheduler()
        tasks = [self._make_scheduled_task("Walk", "09:00 - 09:30")]
        sorted_tasks = scheduler.sort_by_time(tasks)
        assert len(sorted_tasks) == 1
        assert sorted_tasks[0].get_time_slot() == "09:00 - 09:30"

    def test_sort_empty_list(self):
        """Empty input should return an empty list without errors."""
        scheduler = Scheduler()
        assert scheduler.sort_by_time([]) == []

    def test_sort_does_not_mutate_original(self):
        """sort_by_time() should return a new list, not modify the original."""
        scheduler = Scheduler()
        tasks = [
            self._make_scheduled_task("Lunch", "12:00 - 12:30"),
            self._make_scheduled_task("Walk",  "08:00 - 08:30"),
        ]
        original_order = [st.get_time_slot() for st in tasks]
        scheduler.sort_by_time(tasks)
        assert [st.get_time_slot() for st in tasks] == original_order


class TestRecurrenceLogic:
    """Verify mark_completed() produces the correct next-occurrence Task."""

    # --- Happy paths ---

    def test_daily_task_returns_next_day(self):
        """Completing a DAILY task should return a new task due tomorrow."""
        today = date.today()
        task = Task("Medication", 10, Priority.HIGH,
                    frequency=Frequency.DAILY, due_date=today)
        next_task = task.mark_completed()

        assert next_task is not None
        assert next_task.due_date == today + timedelta(days=1)

    def test_weekly_task_returns_next_week(self):
        """Completing a WEEKLY task should return a new task due in 7 days."""
        today = date.today()
        task = Task("Vet visit", 60, Priority.HIGH,
                    frequency=Frequency.WEEKLY, due_date=today)
        next_task = task.mark_completed()

        assert next_task is not None
        assert next_task.due_date == today + timedelta(weeks=1)

    def test_once_task_returns_none(self):
        """Completing a ONCE task should return None — no recurrence."""
        task = Task("Adoption paperwork", 30, Priority.MEDIUM,
                    frequency=Frequency.ONCE)
        next_task = task.mark_completed()

        assert next_task is None

    # --- Edge cases ---

    def test_original_task_is_completed_after_mark(self):
        """The original task must be COMPLETED, not the generated next task."""
        today = date.today()
        task = Task("Medication", 10, Priority.HIGH,
                    frequency=Frequency.DAILY, due_date=today)
        next_task = task.mark_completed()

        assert task.status == TaskStatus.COMPLETED
        assert next_task.status == TaskStatus.PENDING  # next task starts fresh

    def test_next_task_inherits_name_and_priority(self):
        """The generated next task should keep the same name, duration, and priority."""
        today = date.today()
        task = Task("Medication", 15, Priority.HIGH,
                    frequency=Frequency.DAILY, due_date=today)
        next_task = task.mark_completed()

        assert next_task.task_name == "Medication"
        assert next_task.duration_minutes == 15
        assert next_task.priority == Priority.HIGH
        assert next_task.frequency == Frequency.DAILY

    def test_daily_task_with_no_due_date_falls_back_to_today(self):
        """If due_date is None, the next occurrence should be based on today."""
        task = Task("Walk", 20, Priority.MEDIUM, frequency=Frequency.DAILY)
        next_task = task.mark_completed()

        assert next_task is not None
        assert next_task.due_date == date.today() + timedelta(days=1)


class TestConflictDetection:
    """Verify detect_conflicts() correctly identifies overlapping time slots."""

    def _make_scheduled_task(self, name: str, time_slot: str) -> ScheduledTask:
        task = Task(name, 30, Priority.MEDIUM)
        return ScheduledTask(task, time_slot, "test")

    # --- Happy paths ---

    def test_no_conflict_sequential_tasks(self):
        """Non-overlapping sequential tasks should produce no warnings."""
        scheduler = Scheduler()
        tasks = [
            self._make_scheduled_task("Walk",  "08:00 - 08:30"),
            self._make_scheduled_task("Eat",   "08:30 - 08:45"),
            self._make_scheduled_task("Play",  "09:00 - 09:30"),
        ]
        warnings = scheduler.detect_conflicts(tasks)
        assert warnings == []

    # --- Edge cases ---

    def test_identical_time_slots_flagged(self):
        """Two tasks with the exact same time slot must be flagged as a conflict."""
        scheduler = Scheduler()
        tasks = [
            self._make_scheduled_task("Walk", "08:00 - 08:30"),
            self._make_scheduled_task("Eat",  "08:00 - 08:30"),
        ]
        warnings = scheduler.detect_conflicts(tasks)
        assert len(warnings) == 1
        assert "Walk" in warnings[0]
        assert "Eat" in warnings[0]

    def test_partial_overlap_flagged(self):
        """Tasks that partially overlap should produce a conflict warning."""
        scheduler = Scheduler()
        tasks = [
            self._make_scheduled_task("Walk", "08:00 - 08:45"),
            self._make_scheduled_task("Eat",  "08:30 - 09:00"),
        ]
        warnings = scheduler.detect_conflicts(tasks)
        assert len(warnings) == 1

    def test_adjacent_tasks_not_flagged(self):
        """A task ending exactly when the next begins is adjacent, not overlapping."""
        scheduler = Scheduler()
        tasks = [
            self._make_scheduled_task("Walk", "08:00 - 08:30"),
            self._make_scheduled_task("Eat",  "08:30 - 09:00"),
        ]
        # 08:30 == 08:30 → start_a < end_b (480 < 540) AND start_b < end_a (510 < 510) is FALSE
        warnings = scheduler.detect_conflicts(tasks)
        assert warnings == []

    def test_empty_list_returns_no_warnings(self):
        """An empty task list should return an empty warnings list."""
        scheduler = Scheduler()
        assert scheduler.detect_conflicts([]) == []

    def test_single_task_returns_no_warnings(self):
        """A single task cannot conflict with anything."""
        scheduler = Scheduler()
        tasks = [self._make_scheduled_task("Walk", "08:00 - 08:30")]
        assert scheduler.detect_conflicts(tasks) == []

    def test_multiple_conflicts_all_reported(self):
        """If three tasks all overlap, all conflict pairs should be reported."""
        scheduler = Scheduler()
        tasks = [
            self._make_scheduled_task("A", "08:00 - 09:00"),
            self._make_scheduled_task("B", "08:15 - 08:45"),
            self._make_scheduled_task("C", "08:30 - 09:30"),
        ]
        warnings = scheduler.detect_conflicts(tasks)
        # A-B, A-C, and B-C all overlap → 3 warnings
        assert len(warnings) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
