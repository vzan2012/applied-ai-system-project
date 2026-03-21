"""
PawPal+ System - Pet Care Management and Scheduling
Core classes for managing owners, pets, tasks, and daily schedules.
"""

from dataclasses import dataclass, field
from typing import List
from enum import Enum


class Priority(Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Species(Enum):
    """Supported pet species"""
    DOG = "dog"
    CAT = "cat"
    OTHER = "other"


@dataclass
class Task:
    """Represents a pet care task"""
    task_name: str
    duration_minutes: int
    priority: Priority

    def get_priority(self) -> Priority:
        """Get the priority level of this task"""
        pass

    def get_duration(self) -> int:
        """Get the duration in minutes"""
        pass


@dataclass
class Pet:
    """Represents a pet owned by an owner"""
    pet_name: str
    species: Species
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet"""
        pass

    def remove_task(self, task_name: str) -> None:
        """Remove a task by name"""
        pass

    def get_tasks_by_priority(self, priority: Priority) -> List[Task]:
        """Get all tasks with a specific priority level"""
        pass

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks for this pet"""
        pass


@dataclass
class Owner:
    """Represents a pet owner"""
    owner_name: str
    available_hours_per_day: float
    preferences: str = ""
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's collection"""
        pass

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name"""
        pass

    def get_pets(self) -> List[Pet]:
        """Get all pets owned by this owner"""
        pass


@dataclass
class ScheduledTask:
    """Represents a task scheduled at a specific time"""
    task: Task
    time_slot: str
    reasoning: str

    def get_task(self) -> Task:
        """Get the task object"""
        pass

    def get_time_slot(self) -> str:
        """Get the scheduled time slot"""
        pass

    def get_reasoning(self) -> str:
        """Get the reasoning for this scheduling decision"""
        pass


@dataclass
class DailyPlan:
    """Represents a daily schedule plan"""
    scheduled_tasks: List[ScheduledTask] = field(default_factory=list)
    total_time_used: float = 0.0
    description: str = ""

    def get_schedule(self) -> List[ScheduledTask]:
        """Get the list of scheduled tasks"""
        pass


class Scheduler:
    """Orchestrates the scheduling logic to generate daily plans"""

    def generate_daily_plan(
        self, owner: Owner, pet: Pet, available_time: float
    ) -> DailyPlan:
        """Generate an optimized daily plan based on constraints"""
        pass

    def _sort_tasks_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority (internal helper method)"""
        pass

    def _check_time_constraints(
        self, tasks: List[Task], available_time: float
    ) -> bool:
        """Verify that tasks fit within available time (internal helper method)"""
        pass
