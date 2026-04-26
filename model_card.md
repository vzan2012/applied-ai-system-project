# PawPal+ AI Advisor: Model Card Summary

**Overview**
PawPal+ started as a scheduling tool and grew into something that actually gives you feedback on the plan it just made. After generating a daily schedule, it analyzes the full context - what got scheduled, what got skipped, any conflicts, the pet's species - and returns care advice specific to that run, not a generic tips list.

**Key Mechanism**
It tries Gemini 2.0 Flash first. When Gemini hit its free-tier quota during testing (which it did, repeatedly), Groq with Llama 3.3 picked up automatically as a fallback. The user never saw an error. Every call gets logged into `pawpal_ai.log` so that the information and failures are traceable.

**Notable Strengths**
The advice actually reflects the data. For a cat named Justin, it flagged that cats aren't typically walked on leashes - because the schedule had a "Morning walk" task. For a dog named Mochi with a 60-minute grooming block, it suggested splitting it into shorter sessions to reduce stress. That's the schedule talking, not boilerplate.

**Critical Limitations**
It knows species but not the individual animal. It doesn't know the pet's age, health conditions, or breed. It also got one thing clearly wrong - it told me a schedule "exceeded available time" when 1.7 hours were still remaining. Confident, wrong, and easy to miss if you weren't looking at the metrics yourself.

**Key Insight**
The hard part wasn't the AI - it was making the feature not break. Quota limits, API errors, missing keys - any of these would have silently killed the feature. The fallback chain and logging turned those failures into something manageable.
