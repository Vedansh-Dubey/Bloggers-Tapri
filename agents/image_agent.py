# agents/image_agent.py

from agno.agent import Agent
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.google import Gemini
from agno.tools.reasoning import ReasoningTools
from utils import Config

def create_image_keyword_agent(user_id: str = "image_agent") -> Agent:
    memory = Memory(
        model=Gemini(id="gemini-2.0-flash-lite"),
        db=SqliteMemoryDb(table_name="image_memories", db_file="tmp/image_agent.db"),
        delete_memories=True,
        clear_memories=True,
    )
    
    gemini_api_key = Config().GEMINI_API_KEY

    return Agent(
        model=Gemini(id="gemini-2.0-flash-lite", api_key=gemini_api_key),
        # tools=[ReasoningTools(add_instructions=True)],
        memory=memory,
        user_id=user_id,
        instructions=[
            "Only output one clear and descriptive keyword or phrase for image search.",
            "Keep it relevant to the topic. Don't be creative or visual as this image will be searched and retrieved from unsplash",
        ],
        enable_agentic_memory=True,
        markdown=True,
    )
