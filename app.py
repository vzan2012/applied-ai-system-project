import streamlit as st
from pawpal_system import (
    Owner, Pet, Task, Scheduler,
    Priority, Species, Frequency,
)
from ai_advisor import analyze_schedule

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")


def initialize_session_state():
    """Initialize session state variables"""
    if "owner" not in st.session_state:
        st.session_state.owner = None
    if "pet" not in st.session_state:
        st.session_state.pet = None
    if "tasks" not in st.session_state:
        st.session_state.tasks = []
    if "scheduler" not in st.session_state:
        st.session_state.scheduler = Scheduler()
    if "daily_plan" not in st.session_state:
        st.session_state.daily_plan = None
    if "available_hours" not in st.session_state:
        st.session_state.available_hours = 8.0
    if "form_counter" not in st.session_state:
        st.session_state.form_counter = 0
    if "ai_advice" not in st.session_state:
        st.session_state.ai_advice = None
    if "ai_ready" not in st.session_state:
        st.session_state.ai_ready = False
    if "schedule_history" not in st.session_state:
        st.session_state.schedule_history = []


def create_or_update_owner(name: str, available_hours: float):
    """Create or update Owner in session state"""
    if st.session_state.owner is None or st.session_state.owner.owner_name != name:
        st.session_state.owner = Owner(name, available_hours)
    else:
        st.session_state.owner.available_hours_per_day = available_hours


def create_or_update_pet(name: str, species_str: str):
    """Create or update Pet in session state"""
    species_map = {"dog": Species.DOG,
                   "cat": Species.CAT, "other": Species.OTHER}
    species = species_map.get(species_str.lower(), Species.OTHER)

    if st.session_state.pet is None or st.session_state.pet.pet_name != name:
        st.session_state.pet = Pet(name, species)
        st.session_state.tasks = []
    else:
        st.session_state.pet.species = species


initialize_session_state()

# ── Header ────────────────────────────────────────────────────────────────────

st.title("🐾 PawPal+")
st.caption("Smart daily care scheduling for your pet.")

st.divider()

# ── Owner & Pet Info ───────────────────────────────────────────────────────────

st.subheader("👤 Owner & Pet Info")
col1, col2 = st.columns(2)

with col1:
    owner_name = st.text_input(
        "Owner name", value="Jordan", key="owner_name_input")
    available_hours = st.slider(
        "Available hours per day", 1.0, 12.0, 8.0, 0.5, key="hours_slider"
    )

with col2:
    pet_name = st.text_input("Pet name", value="Mochi", key="pet_name_input")
    species = st.selectbox(
        "Species", ["dog", "cat", "other"], key="species_select")

create_or_update_owner(owner_name, available_hours)
create_or_update_pet(pet_name, species)

st.info(
    f"Owner: **{st.session_state.owner.owner_name}** | "
    f"Pet: **{st.session_state.pet.pet_name}** ({st.session_state.pet.species.value}) | "
    f"Available: **{available_hours}h/day**"
)

st.divider()

# ── Add Tasks ─────────────────────────────────────────────────────────────────

st.subheader("📋 Tasks")
st.caption("Add tasks for your pet. High-priority tasks are scheduled first.")

fc = st.session_state.form_counter
col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
with col1:
    task_title = st.text_input(
        "Task title", value="Morning walk", key=f"task_title_input_{fc}")
with col2:
    duration = st.number_input(
        "Duration (min)", min_value=1, max_value=240, value=20, key=f"duration_input_{fc}"
    )
with col3:
    priority = st.selectbox(
        "Priority", ["low", "medium", "high"], index=2, key=f"priority_select_{fc}")
with col4:
    frequency = st.selectbox(
        "Repeat", ["once", "daily", "weekly"], key=f"frequency_select_{fc}")

if st.button("➕ Add Task"):
    priority_map = {"low": Priority.LOW,
                    "medium": Priority.MEDIUM, "high": Priority.HIGH}
    frequency_map = {"once": Frequency.ONCE,
                     "daily": Frequency.DAILY, "weekly": Frequency.WEEKLY}
    new_task = Task(
        task_title[:1].upper() + task_title[1:], duration,
        priority_map[priority],
        frequency=frequency_map[frequency]
    )
    st.session_state.tasks.append(new_task)
    st.session_state.pet.add_task(new_task)
    st.session_state.daily_plan = None
    st.session_state.ai_advice = None
    st.session_state.ai_ready = False
    st.session_state.form_counter += 1
    st.success(f"Added **{task_title}** ({frequency}, {priority} priority)")
    st.rerun()

if st.session_state.tasks:
    PRIORITY_ICON = {Priority.HIGH: "🔴",
                     Priority.MEDIUM: "🟡", Priority.LOW: "🟢"}
    FREQ_ICON = {Frequency.ONCE: "1×",
                 Frequency.DAILY: "Daily", Frequency.WEEKLY: "Weekly"}

    # Header row
    h1, h2, h3, h4, h5, h6 = st.columns([3, 2, 2, 2, 2, 1])
    h1.markdown("**Task**")
    h2.markdown("**Duration**")
    h3.markdown("**Priority**")
    h4.markdown("**Repeat**")
    h5.markdown("**Status**")
    h6.markdown("")
    st.divider()

    for i, task in enumerate(st.session_state.tasks):
        c1, c2, c3, c4, c5, c6 = st.columns([3, 2, 2, 2, 2, 1])
        c1.write(task.task_name)
        c2.write(f"{task.duration_minutes} min")
        c3.write(
            f"{PRIORITY_ICON[task.priority]} {task.priority.value.upper()}")
        c4.write(FREQ_ICON[task.frequency])
        c5.write(task.status.value.capitalize())
        if c6.button("🗑️", key=f"del_{i}"):
            st.session_state.pet.remove_task(task.task_name)
            st.session_state.tasks.pop(i)
            st.session_state.daily_plan = None
            st.session_state.ai_advice = None
            st.session_state.ai_ready = False
            st.rerun()

    st.divider()
    if st.button("🗑️ Clear All Tasks"):
        st.session_state.tasks = []
        st.session_state.pet.tasks = []
        st.session_state.daily_plan = None
        st.session_state.ai_advice = None
        st.session_state.ai_ready = False
        st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ── Generate Schedule ──────────────────────────────────────────────────────────

st.subheader("🎯 Generate Daily Schedule")
st.caption(
    "Generates an optimized plan — highest priority tasks first, within your time budget.")

if st.button("✨ Generate Schedule", type="primary"):
    if not st.session_state.tasks:
        st.error("Please add at least one task before generating a schedule.")
    else:
        st.session_state.daily_plan = st.session_state.scheduler.generate_daily_plan(
            st.session_state.owner,
            st.session_state.pet,
            available_hours,
        )
        with st.spinner("Analyzing schedule with AI..."):
            st.session_state.ai_advice = analyze_schedule(
                st.session_state.owner,
                st.session_state.pet,
                st.session_state.daily_plan,
                st.session_state.scheduler,
            )
        st.session_state.ai_ready = True

        # Save to history — replace existing entry for this pet, otherwise append
        _sorted = st.session_state.scheduler.sort_by_time(
            st.session_state.daily_plan.get_schedule()
        )
        _entry = {
            "pet_name": st.session_state.pet.pet_name,
            "species": st.session_state.pet.species.value,
            "owner_name": st.session_state.owner.owner_name,
            "available_hours": available_hours,
            "total_tasks": len(_sorted),
            "hours_used": st.session_state.daily_plan.total_time_used / 60,
            "skipped": len(st.session_state.tasks) - len(_sorted),
            "sorted_schedule": _sorted,
            "ai_advice": st.session_state.ai_advice,
            "description": st.session_state.daily_plan.description,
        }
        _idx = next(
            (i for i, h in enumerate(st.session_state.schedule_history)
             if h["pet_name"] == _entry["pet_name"]),
            None,
        )
        if _idx is not None:
            st.session_state.schedule_history[_idx] = _entry
        else:
            st.session_state.schedule_history.append(_entry)

# ── Display Plan ───────────────────────────────────────────────────────────────

if st.session_state.daily_plan is not None:
    plan = st.session_state.daily_plan
    scheduler = st.session_state.scheduler

    st.markdown("---")
    st.subheader("📅 Today's Schedule")

    if not plan.get_schedule():
        st.warning(
            "No tasks could be scheduled. All tasks may already be completed or skipped.")
    else:
        # Sort the schedule chronologically before display
        sorted_schedule = scheduler.sort_by_time(plan.get_schedule())

        # ── Conflict Detection Banner ──────────────────────────────────────────
        conflicts = scheduler.detect_conflicts(sorted_schedule)
        if conflicts:
            st.error(
                f"**⚠️ Schedule Conflict Detected** — {len(conflicts)} overlapping time slot(s) found.\n\n"
                "Review the tasks below and adjust durations or remove a conflicting task."
            )
            with st.expander("See conflict details"):
                for warning in conflicts:
                    # Strip the raw "WARNING:" prefix for a friendlier display
                    friendly = warning.replace("WARNING: ", "")
                    st.markdown(f"- {friendly}")
        else:
            st.success("No scheduling conflicts - your plan looks great!")

        # ── Plan Summary ───────────────────────────────────────────────────────
        st.info(plan.description)

        # ── Task Cards (chronological order) ──────────────────────────────────
        st.markdown("#### Scheduled Tasks")
        PRIORITY_ICON = {Priority.HIGH: "🔴",
                         Priority.MEDIUM: "🟡", Priority.LOW: "🟢"}

        for i, scheduled_task in enumerate(sorted_schedule, 1):
            task = scheduled_task.get_task()
            freq_badge = (
                " _(repeats daily)_" if task.frequency == Frequency.DAILY
                else " _(repeats weekly)_" if task.frequency == Frequency.WEEKLY
                else ""
            )
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.markdown(
                        f"**{i}. {task.task_name}**{freq_badge}"
                    )
                    st.caption(scheduled_task.get_reasoning())
                with col2:
                    st.markdown(f"🕐 `{scheduled_task.get_time_slot()}`")
                    st.caption(f"{task.duration_minutes} min")
                with col3:
                    st.markdown(
                        f"{PRIORITY_ICON[task.priority]} **{task.priority.value.upper()}**"
                    )

        # ── Summary Metrics ────────────────────────────────────────────────────
        st.markdown("---")
        total_tasks = len(sorted_schedule)
        hours_used = plan.total_time_used / 60
        remaining = available_hours - hours_used
        skipped = len(st.session_state.tasks) - total_tasks

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Tasks Scheduled", total_tasks)
        col2.metric("Time Used", f"{hours_used:.1f}h")
        col3.metric("Time Remaining", f"{remaining:.1f}h")
        col4.metric("Tasks Skipped", skipped, delta=f"-{skipped}" if skipped else None,
                    delta_color="inverse")

        # ── AI Care Insights ───────────────────────────────────────────────────
        if st.session_state.ai_ready:
            st.markdown("---")
            st.subheader("🤖 AI Care Insights")
            st.caption(
                "Powered by Gemini 2.0 Flash · Groq (Llama 3.3) fallback · Analysis based on your schedule")
            if st.session_state.ai_advice:
                st.info(st.session_state.ai_advice)
            else:
                st.warning(
                    "AI insights unavailable. "
                    "Check that `API_KEY` is set correctly in your `.env` file."
                )

# ── Schedule History ───────────────────────────────────────────────────────────

if len(st.session_state.schedule_history) >= 2:
    st.divider()
    st.subheader("📊 Schedule History")
    st.caption("Compare schedules across pets — expand any card to see full details.")

    if st.button("🗑️ Clear History"):
        st.session_state.schedule_history = []
        st.rerun()

    _PICON = {Priority.HIGH: "🔴", Priority.MEDIUM: "🟡", Priority.LOW: "🟢"}

    for entry in st.session_state.schedule_history:
        label = (
            f"🐾 {entry['pet_name']} ({entry['species']})  ·  "
            f"{entry['total_tasks']} tasks  ·  {entry['hours_used']:.1f}h used  ·  "
            f"{entry['skipped']} skipped"
        )
        with st.expander(label):
            st.caption(entry["description"])

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Tasks Scheduled", entry["total_tasks"])
            m2.metric("Time Used", f"{entry['hours_used']:.1f}h")
            m3.metric("Time Remaining",
                      f"{entry['available_hours'] - entry['hours_used']:.1f}h")
            m4.metric("Tasks Skipped", entry["skipped"])

            st.markdown("**Scheduled Tasks**")
            for i, st_task in enumerate(entry["sorted_schedule"], 1):
                task = st_task.get_task()
                c1, c2, c3 = st.columns([3, 2, 1])
                c1.write(f"**{i}. {task.task_name}**")
                c2.write(f"🕐 `{st_task.get_time_slot()}`")
                c3.write(f"{_PICON[task.priority]} {task.priority.value.upper()}")

            if entry["ai_advice"]:
                st.markdown("**🤖 AI Care Insights**")
                st.info(entry["ai_advice"])
