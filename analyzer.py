"""Groq: a vision model reads the screenshot, gpt-oss-120b does the thinking."""
import base64
import re

from groq import Groq

import config

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = Groq()   # reads GROQ_API_KEY
    return _client


def _clean(text):
    # some reasoning models emit <think>...</think>; hide it
    return re.sub(r"<think>.*?</think>", "", text or "", flags=re.DOTALL).strip()


def _vision(jpeg, text, max_tokens):
    b64 = base64.b64encode(jpeg).decode()
    resp = _get_client().chat.completions.create(
        model=config.VISION_MODEL,
        max_completion_tokens=max_tokens,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": text},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
            ],
        }],
    )
    return _clean(resp.choices[0].message.content)


def describe(jpeg, app, title, taskbar_apps):
    """Short summary saved to history (runs automatically on window change)."""
    apps = ", ".join(taskbar_apps) if taskbar_apps else "(unavailable)"
    text = (f"Active app: {app}\nWindow title: {title}\n"
            f"Open taskbar apps: {apps}\n\n{config.DESCRIBE_PROMPT}")
    return _vision(jpeg, text, config.MAX_TOKENS_DESCRIBE)


def ask(jpeg, app, title, question, history):
    """Stage 1: vision model reads the screen. Stage 2: gpt-oss-120b answers."""
    screen = _vision(
        jpeg,
        f"Active app: {app}\nWindow title: {title}\n\n"
        "Describe this screen in detail: every visible app/window, all brands and logos, "
        "and all readable text (transcribe important text exactly). "
        f"The user will ask: \"{question}\" so focus on what helps answer it. "
        "Do not identify real people by their faces.",
        config.MAX_TOKENS_SCREEN,
    )
    resp = _get_client().chat.completions.create(
        model=config.CHAT_MODEL,
        max_completion_tokens=config.MAX_TOKENS_CHAT,
        reasoning_effort=config.CHAT_REASONING_EFFORT,
        messages=[
            {"role": "system",
             "content": "You are a desktop assistant. You cannot see images directly; a vision "
                        "model has described the user's current screen for you. Answer from that "
                        "description and the activity log. If it isn't there, say so."},
            {"role": "user",
             "content": f"Recent activity log (oldest first):\n{history or '(none yet)'}\n\n"
                        f"Current screen description:\n{screen}\n\n"
                        f"Active app: {app}\nWindow title: {title}\n\n"
                        f"Question: {question}"},
        ],
    )
    return _clean(resp.choices[0].message.content)
