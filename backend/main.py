import dspy
import os
import json

model = dspy.LM(
    model='groq/openai/gpt-oss-120b',
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.1
)

dspy.settings.configure(lm=model)


class UserAnalysis(dspy.Signature):
    """
    You are a strict but caring friend who genuinely worries about someone's
    phone addiction.  Think like a REAL HUMAN — not a bot.
    Be blunt, be honest, and give advice the way a concerned friend would.
    No corporate language, no sugar-coating.
    """

    user_data = dspy.InputField(
        desc="JSON containing user screen time, apps, and usage patterns"
    )

    insights = dspy.OutputField(
        desc=(
            "Give SHORT, DIRECT, ACTIONABLE insights in a MARKDOWN TABLE.\n"
            "Think like a real person — what would YOU tell your friend?\n"
            "- Each row = one insight.\n"
            "- Columns: Issue | Action\n"
            "- Be strict, be real. Use command-style language.\n"
            "- If someone is watching 3h of reels, don't say 'consider reducing' — say 'STOP wasting 3h on reels, limit to 30 min MAX'.\n"
            "- If gaming >1h, tell them to set a hard timer.\n"
            "- If productivity is low, call it out directly.\n"
            "- If total screen time >10h, tell them their eyes and brain both need rest.\n"
            "- No explanations, no fluff, no generic advice.\n"
            "- Example:\n"
            "| Issue | Action |\n"
            "| 3h on Instagram reels | You're throwing away 3h daily. Cut to ≤30 min. Use app timer. |\n"
            "| No exercise or outdoor time | Get off the phone. Walk 30 min daily, non-negotiable. |\n"
            "| Only 1h of study | That's way too low. Add 2h focused study blocks. |\n"
            "- Keep everything concise, practical, and brutally honest.\n"
        )
    )

    summary = dspy.OutputField(
        desc=(
            "Give a VERY SHORT human-like summary (2–3 lines max).\n"
            "Think about how a real concerned friend would react seeing this data.\n"
            "- If total >10h: be alarmed. Something like '12 hours on your phone? Your eyes, your health — everything is taking a hit.'\n"
            "- If social media dominates: call it out. 'You are scrolling your life away.'\n"
            "- If there is some good (education, work): acknowledge it but still push harder.\n"
            "- If usage is balanced and under 6h: appreciate them genuinely.\n"
            "- Sound like a REAL person — not a textbook. Be direct, emotional, honest.\n"
            "- No generic statements like 'Your usage is moderate'. Be specific.\n"
        )
    )

    isAddicted = dspy.OutputField(
        desc=(
            "Return ONLY True or False. Nothing else.\n"
            "Rules (think like a doctor diagnosing screen addiction):\n"
            "- True → if TOTAL daily screen time > 10 hours (no matter what apps).\n"
            "- True → if entertainment + social media usage is > 60% of total time.\n"
            "- True → if gaming > 2 hours per day.\n"
            "- True → if any single social media app > 3 hours.\n"
            "- False → if total is ≤ 10h AND user has meaningful productivity/study usage.\n"
            "- False → if most time is on work/education apps (Notion, Wikipedia, VS Code, etc.).\n"
            "- Productivity apps are NOT addiction. But even productive people become unhealthy at >10h total.\n"
            "- Do NOT explain. Only output True or False.\n"
        )
    )


def analyze_user(user_data_dict):
    # Hard validation: a day only has 24 hours
    total = user_data_dict.get("daily_usage_hours", 0)
    if total > 24:
        raise ValueError(
            f"A day only has 24 hours! "
            f"You entered {total:.1f} hours of total usage — that is not possible. "
            f"Please correct your app hours and try again."
        )

    predictor = dspy.ChainOfThought(UserAnalysis)
    return predictor(user_data=json.dumps(user_data_dict))


if __name__ == "__main__":
    userusage = {
        "user_id": "101",
        "daily_usage_hours": 16,
        "apps": [
            {"name": "wikipedia", "hours": 2, "type": "education"},
            {"name": "bgmi", "hours": 2, "type": "games"},
            {"name": "instagram", "hours": 2, "type": "social media"},
            {"name": "whatsapp", "hours": 2, "type": "social media"},
            {"name": "facebook", "hours": 2, "type": "social media"},
            {"name": "twitter", "hours": 2, "type": "social media"},
            {"name": "youtube", "hours": 2, "type": "social media"},
            {"name": "youtube", "hours": 2, "type": "social media"},
        ]
    }

    # Use a predictor to handle the signature
    analysis = analyze_user(userusage)
    print(f"\n\nInsights: {analysis.insights}")
    print(f"\n\nSummary: {analysis.summary}")
    print(f"\n\nIs Addicted: {analysis.isAddicted}")
