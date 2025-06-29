# agents/research_merger.py
from agno.agent import Agent
from agno.models.groq import Groq
from typing import Dict, List, Any
import logging
import json
import re
from utils.config import config
from .web_research_agent import WebResearchAgent
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class ResearchAnalysis:
    def __init__(self):
        self.research_agent = WebResearchAgent()
        self.parser_agent = self._create_parser_agent()
        self.summary_agent = self._create_summary_agent()
        logger.info("Agno-based research merger initialized")

    def _create_parser_agent(self) -> Agent:
        """Create agent for parsing user research"""
        return Agent(
            model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct", api_key=config.GROQ_API_KEY),
            instructions=[
                "You are a research analysis specialist.",
                "Convert unstructured research notes into structured JSON format.",
                "Extract key facts with their supporting evidence and sources.",
                "For each finding, include: fact, supporting_evidence, source_url, source_credibility",
                "Use 'User Provided' for missing URLs/credibility",
                "Output ONLY valid JSON with the specified structure",
            ],
            markdown=True,
        )

    def _create_summary_agent(self) -> Agent:
        """Create agent for generating summaries"""
        return Agent(
            model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct", api_key=config.GROQ_API_KEY),
            instructions=[
                "You are a research synthesis expert.",
                "Combine findings from multiple sources into a comprehensive summary.",
                "Maintain neutral, professional tone",
                "Structure: Overview, Key Insights, Conclusion",
                "Cover all key points while eliminating redundancy",
                "Output a well-structured text summary",
                "DOES NOT include any thinking process or internal tags"
            ],
        )

    def analyse_research(self, topic: str, user_research: str) -> Dict[str, Any]:
        """
        Merge user-provided research with automated research using Agno agents

        Args:
            topic: Research topic
            user_research: User's research text (unstructured)

        Returns:
            Combined research in structured format
        """
        try:
            user_structured = self._parse_user_research(topic, user_research)

            auto_research = self.research_agent.research_topic(topic)

            combined = self._combine_research(user_structured, auto_research)

            combined["summary"] = self._generate_summary(combined)

            return combined
        except Exception as e:
            logger.exception(f"Research merge failed: {str(e)}")
            return {"error": f"Research merge failed: {str(e)}", "topic": topic}

    def _parse_user_research(self, topic: str, user_research: str) -> Dict[str, Any]:
        """Convert unstructured user research to structured format using Agno"""
        prompt = f"""
        **Topic**: {topic}
        
        **User Research**:
        {user_research}
        
        **Required Output Structure**:
        {{
            "topic": "Research topic",
            "key_findings": [
                {{
                    "fact": "Specific fact or claim",
                    "supporting_evidence": "Brief supporting details",
                    "source_url": "Source URL or 'User Provided'",
                    "source_credibility": "High/Medium/Low/User Provided"
                }}
            ]
        }}
        """

        response = self.parser_agent.run(prompt)
        return self._parse_research_output(response.content)  # type: ignore

    def _parse_research_output(self, output: str) -> Dict[str, Any]:
        """Parse structured research from agent output"""
        try:
            # Extract JSON from markdown
            json_match = re.search(r"```json\n(.*?)\n```", output, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            return json.loads(output)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse research output: {output[:200]}...")
            return {"topic": "Unparsed Research", "key_findings": []}

    def _combine_research(self, user_data: Dict, auto_data: Dict) -> Dict[str, Any]:
        """Combine and deduplicate research findings"""
        # Handle errors in automated research
        if "error" in auto_data:
            logger.warning("Using only user research due to automated research error")
            return user_data

        # Combine topic names
        topic = auto_data.get("topic", user_data.get("topic", "Unknown Topic"))

        # Combine findings
        combined_findings = user_data.get("key_findings", []) + auto_data.get(
            "key_findings", []
        )

        # Deduplicate based on fact similarity
        unique_findings = self._deduplicate_findings(combined_findings)

        return {
            "topic": topic,
            "key_findings": unique_findings,
            "sources": {
                "user": len(user_data.get("key_findings", [])),
                "auto": len(auto_data.get("key_findings", [])),
            },
        }

    def _deduplicate_findings(self, findings: List[Dict]) -> List[Dict]:
        """Remove duplicate findings using text similarity"""
        unique_findings = []
        seen_facts = set()

        for finding in findings:
            # Normalize fact text
            fact_text = finding["fact"].lower().strip()

            # Check for duplicates
            is_duplicate = False
            for seen in seen_facts:
                if self._similarity(fact_text, seen) > 0.8:  # 80% similarity threshold
                    is_duplicate = True
                    break

            if not is_duplicate:
                seen_facts.add(fact_text)
                unique_findings.append(finding)

        return unique_findings

    def _similarity(self, a: str, b: str) -> float:
        """Calculate text similarity ratio"""
        return SequenceMatcher(None, a, b).ratio()

    def _generate_summary(self, research_data: Dict) -> str:
        """Generate unified research summary using Agno agent"""
        findings_str = "\n".join(
            f"- {finding['fact']} (Source: {finding['source_url']})"
            for finding in research_data["key_findings"]
        )

        prompt = f"""
        **Topic**: {research_data["topic"]}
        
        **Key Findings**:
        {findings_str}
        
        **Task**:
        Create a comprehensive research summary that:
        1. Provides an overview of the topic
        2. Highlights key insights from all sources
        3. Identifies patterns and relationships between findings
        4. Concludes with significant implications
        5. Maintains a neutral, professional tone
        6. Is approximately 300-500 words
        7. DOES NOT include any thinking process or internal tags
        """

        response = self.summary_agent.run(prompt)
        return response.content  # type: ignore

    def _clean_summary(self, summary: str) -> str:
        """Remove any internal thinking tags or markers from summary"""
        # Remove <think>...</think> blocks
        cleaned = re.sub(r"<think>.*?</think>", "", summary, flags=re.DOTALL)

        # Remove any other internal reasoning markers
        cleaned = re.sub(r"\(internal note:.*?\)", "", cleaned, flags=re.DOTALL)
        cleaned = re.sub(r"\[thinking:.*?\]", "", cleaned, flags=re.DOTALL)

        # Remove any remaining XML-like tags
        cleaned = re.sub(r"</?[a-z]+>", "", cleaned)

        # Remove excessive line breaks
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

        return cleaned.strip()
