"""
PawPal+ AI Advisor
Agentic workflow that analyzes a generated daily schedule and returns
specific, data-driven pet care recommendations.

Agentic steps:
  1. Extract scheduled tasks, skipped tasks, and conflicts from the plan.
  2. Build a structured prompt that contains the full schedule context.
  3. Try Gemini first; fall back to Groq (Llama 3.3) if Gemini fails.
  4. Log every request and response; return None gracefully on any failure.
"""

import os
import logging
from typing import Optional

import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

from pawpal_system import Owner, Pet, DailyPlan, Scheduler

# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    filename="pawpal_ai.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Client setup ───────────────────────────────────────────────────────────────
load_dotenv()

_SYSTEM_PROMPT = (
    "You are PawPal+, a knowledgeable and caring pet care advisor. "
    "Your job is to analyze daily pet care schedules and provide specific, "
    "actionable recommendations. You understand animal behavior, health needs, "
    "and the importance of consistent routines. Always tie your advice directly "
    "to the tasks and schedule you are given — never give generic responses."
)

_gemini_model: Optional[genai.GenerativeModel] = None
_groq_client: Optional[Groq] = None

_gemini_key = os.getenv("API_KEY")
if _gemini_key:
    try:
        genai.configure(api_key=_gemini_key)
        _gemini_model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=_SYSTEM_PROMPT,
        )
        logger.info("Gemini model initialized successfully (gemini-2.0-flash).")
    except Exception as exc:  # noqa: BLE001 — any init failure must not crash the app
        logger.error("Gemini initialization failed: %s", exc)
else:
    logger.warning("API_KEY not found in environment - Gemini disabled.")

_groq_key = os.getenv("GROQ_API_KEY")
if _groq_key:
    try:
        _groq_client = Groq(api_key=_groq_key)
        logger.info("Groq client initialized successfully (llama-3.3-70b-versatile).")
    except Exception as exc:  # noqa: BLE001 — any init failure must not crash the app
        logger.error("Groq initialization failed: %s", exc)
else:
    logger.warning("GROQ_API_KEY not found in environment - Groq fallback disabled.")


# ── Prompt builder ─────────────────────────────────────────────────────────────

def _format_prompt(
    owner: Owner,
    pet: Pet,
    plan: DailyPlan,
    conflicts: list,
    skipped_tasks: list,
) -> str:
    """Build a structured, context-rich prompt from the schedule data."""
    scheduled = plan.get_schedule()

    task_lines = [
        f"  • [{st.get_task().priority.value.upper()}] {st.get_task().task_name} "
        f"({st.get_task().duration_minutes} min) @ {st.get_time_slot()}"
        for st in scheduled
    ]
    skipped_lines = [
        f"  • [{t.priority.value.upper()}] {t.task_name} ({t.duration_minutes} min)"
        for t in skipped_tasks
    ]
    conflict_lines = [
        f"  • {c.replace('WARNING: ', '')}" for c in conflicts
    ]

    tasks_str    = "\n".join(task_lines)    if task_lines    else "  (none)"
    skipped_str  = "\n".join(skipped_lines) if skipped_lines else "  (none)"
    conflict_str = "\n".join(conflict_lines) if conflict_lines else "  (none)"

    return f"""Analyze the following pet care schedule and provide targeted advice.

CONTEXT:
  Owner : {owner.owner_name}
  Pet   : {pet.pet_name} ({pet.species.value})
  Available : {owner.available_hours_per_day}hrs/day | Time used : {plan.total_time_used / 60:.1f}h

SCHEDULED TASKS ({len(scheduled)}):
{tasks_str}

SKIPPED TASKS ({len(skipped_tasks)}):
{skipped_str}

DETECTED CONFLICTS ({len(conflicts)}):
{conflict_str}

Respond with:
1. A brief overall assessment of this schedule (1-2 sentences).
2. Any health or care concerns specific to {pet.pet_name} as a {pet.species.value}.
3. 2-3 concrete, actionable recommendations to improve this schedule.

Keep your response under 200 words. Address {pet.pet_name} by name."""


# ── Main analysis function ─────────────────────────────────────────────────────

def analyze_schedule(
    owner: Owner,
    pet: Pet,
    plan: DailyPlan,
    scheduler: Scheduler,
) -> Optional[str]:
    """
    Agentic workflow: analyze the daily plan and return insights.
    Tries Gemini first; falls back to Groq if Gemini is unavailable or fails.

    Returns:
        AI-generated insight string, or None if all providers fail.
    """
    if _gemini_model is None and _groq_client is None:
        logger.warning("analyze_schedule called but no AI provider is available.")
        return None

    # Step 1 — gather all schedule data
    scheduled = plan.get_schedule()
    conflicts = scheduler.detect_conflicts(scheduled) if scheduled else []
    scheduled_objs = [st.get_task() for st in scheduled]
    skipped = [t for t in pet.get_all_tasks() if t not in scheduled_objs]

    # Step 2 — build structured prompt
    prompt = _format_prompt(owner, pet, plan, conflicts, skipped)

    logger.info(
        "AI request | owner=%s | pet=%s (%s) | scheduled=%d | skipped=%d | conflicts=%d",
        owner.owner_name, pet.pet_name, pet.species.value,
        len(scheduled), len(skipped), len(conflicts),
    )

    # Step 3 — try Gemini first
    if _gemini_model is not None:
        try:
            response = _gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=400,
                    temperature=0.4,
                ),
            )
            text = response.text.strip()
            logger.info("Gemini response received | chars=%d", len(text))
            return text
        except Exception as exc:  # noqa: BLE001 — fall through to Groq on any failure
            logger.warning("Gemini failed, falling back to Groq: %s", exc)

    # Step 4 — fall back to Groq
    if _groq_client is not None:
        try:
            response = _groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=400,
                temperature=0.4,
            )
            text = response.choices[0].message.content.strip()
            logger.info("Groq response received | chars=%d", len(text))
            return text
        except Exception as exc:  # noqa: BLE001 — any API failure must not crash the app
            logger.error("Groq API call failed: %s", exc)

    return None