# services/agno.py
from typing import Any, Dict
from agents import WebResearchAgent
from agents import create_image_keyword_agent
from agents import ResearchAnalysis
from agents import BlogWriter
from agents import create_tag_agent
from utils import *
import logging

# Initialize logger
logger = logging.getLogger(__name__)


class AgnoService:
    def __init__(self):
        self.research_agent = WebResearchAgent()
        self.image_agent = create_image_keyword_agent()
        self.tag_agent = create_tag_agent()
        self.research_merger = ResearchAnalysis()
        self.blog_writer = BlogWriter()
        logger.info("Agno service initialized with research merger and blog writer")

    def research_topic(self, topic: str) -> dict:
        """Conduct in-depth research on a topic"""
        logger.info(f"Researching topic: {topic}")
        return self.research_agent.research_topic(topic)

    def generate_image_keyword(self, topic: str) -> str:
        """Generate an image search keyword for a blog topic"""
        logger.info(f"Generating image keyword for: {topic}")
        response = self.image_agent.run(
            message=topic,
            input=f"Generate a keyword for an image related to this blog topic: {topic}",
            stream=False,
            show_full_reasoning=False,
        )
        logger.debug(f"Image keyword generated: {response.content}")
        return response.content.strip()  # type: ignore
    
    def generate_tag(self, topic: str) -> str:
        """Generate tags for a blog topic"""
        logger.info(f"Generating tags for: {topic}")
        response = self.tag_agent.run(
            message=topic,
            input=f"Generate a keyword for an image related to this blog topic: {topic}",
            stream=False,
            show_full_reasoning=False,
        )
        logger.debug(f"Tags keyword generated: {response.content}")
        tags = clean_tag_output(response.content.strip() ) # type: ignore
        return tags  # type: ignore

    def research_analysis(self, topic: str, user_research: str) -> Dict[str, Any]:
        """
        Merge user research with automated research
        """
        logger.info(f"Merging research for topic: {topic}")
        return self.research_merger.analyse_research(topic, user_research)

    def write_blog(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a professional technical blog from research data

        Args:
            research_data: Output from research_analysis

        Returns:
            Dictionary containing blog content and metadata
        """
        logger.info(f"Writing blog for topic: {research_data.get('topic', 'Unknown')}")
        return self.blog_writer.write_blog(research_data)

    def edit_blog(self, blog_state: Dict[str, Any], user_edits: str) -> Dict[str, Any]:
        """
        Apply user edits to an existing blog

        Args:
            blog_state: Current blog state from write_blog
            user_edits: User's modification instructions

        Returns:
            Updated blog state
        """
        logger.info("Applying user edits to blog")
        return self.blog_writer.apply_user_edits(blog_state, user_edits)
    

    def run_agno_services(self, topic: str, user_research: str):
        logger.info(f"Testing Agno service for topic: {topic}")
        
        keyword = agno_service.generate_image_keyword(topic)

        logger.info(f"User research input:\n{user_research[:200]}...")
        
        research_data = agno_service.research_analysis(topic, user_research)
        
        logger.info("Research Results:")

            
        blog = agno_service.write_blog(research_data)
        
        tags = agno_service.generate_tag(topic)
        
        return keyword, research_data, blog, tags


agno_service = AgnoService()
