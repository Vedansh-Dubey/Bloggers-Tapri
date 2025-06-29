# agents/tag_agent.py

from agno.agent import Agent
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.google import Gemini
from agno.tools.reasoning import ReasoningTools
from utils import Config

import re


def create_tag_agent(user_id: str = "tag_agent") -> Agent:
    gemini_api_key = Config().GEMINI_API_KEY

    return Agent(
        model=Gemini(id="gemini-2.0-flash-lite", api_key=gemini_api_key),
        user_id=user_id,
        instructions=[
            "Only output a comma-separated list of clear, SEO-friendly tags relevant to the topic.",
            "Each tag must be a single lowercase word or a hyphenated phrase (e.g., 'machine-learning').",
            "Strictly no special characters except hyphens. No spaces allowed.",
            "Output only the list, no extra explanation or markdown."
        ],
        enable_agentic_memory=True,
        markdown=False,
    )
