import re
import datetime

# Placeholder bot context – in real integration replace with actual context object
class BotContext:
    """Simple placeholder for the bot's current model and thinking mode.
    In production this would be provided by the bot framework.
    """
    model = "gemini-3.2-flash-lite"
    thinking_mode = "low"

    @classmethod
    async def set_model(cls, model_name: str, thinking_mode: str = None):
        """Switch the bot's model and optionally its thinking mode.
        This stub just updates the class attributes.
        """
        cls.model = model_name
        if thinking_mode:
            cls.thinking_mode = thinking_mode
        # In a real system you would call the appropriate API/CLI here.
        print(f"[BotContext] Model switched to {model_name} (mode: {cls.thinking_mode})")


def detect_category(text: str) -> str:
    """Classify the user request into one of three categories.
    Returns one of: "routine", "philosophy", "coding".
    """
    # Define keyword patterns (case‑insensitive)
    low_keywords = r"\b(schedule|meeting|deadline|task list|how to|what is|explain)\b"
    medium_keywords = r"\b(meaning|purpose|why|feel|thought|opinion|philosophy|ethical|subjective)\b"
    code_keywords = r"\b(code|function|bug|error|compile|algorithm|refactor|python|javascript|java|sql|api|debug)\b"

    if re.search(code_keywords, text, re.IGNORECASE):
        return "coding"
    if re.search(medium_keywords, text, re.IGNORECASE):
        return "philosophy"
    if re.search(low_keywords, text, re.IGNORECASE):
        return "routine"
    # Default fallback – treat as routine
    return "routine"


async def ensure_correct_model(task_intent: str) -> str:
    """Detect the appropriate model & mode and switch the bot if needed.

    Args:
        task_intent: The raw user message or a pre‑extracted intent string.
    Returns:
        Human‑readable message describing the action taken.
    """
    category = detect_category(task_intent)
    config_map = {
        "routine": ("gemini-3.2-flash-lite", "low"),
        "philosophy": ("gemini-3.2-flash-lite", "medium"),
        "coding": ("gemini-4-hydrogen", "medium"),
    }
    desired_model, desired_mode = config_map[category]

    if (BotContext.model != desired_model) or (BotContext.thinking_mode != desired_mode):
        await BotContext.set_model(desired_model, thinking_mode=desired_mode)
        timestamp = datetime.datetime.now().isoformat()
        # Simple log – in a real system use structured logging
        print(f"[{timestamp}] Switched to {desired_model} (mode: {desired_mode}) for {category} task")
        return f"Switched to {desired_model} (mode: {desired_mode}) for {category} task."
    return "Current model and mode already appropriate."

# Example usage (remove or replace in production)
if __name__ == "__main__":
    import asyncio
    user_input = "Can you help me debug this Python function?"
    result = asyncio.run(ensure_correct_model(user_input))
    print(result)
