# agents/research_agent.py
from agno.agent import Agent, RunResponse
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.models.google import Gemini
from typing import Dict, Any
from utils.config import config
import json
import re
import logging

logger = logging.getLogger(__name__)


class WebResearchAgent:
    def __init__(self):
        self.agent = self._create_research_agent()
        logger.info("Research agent initialized")

    def _create_research_agent(self) -> Agent:
        """Create and configure the research agent with DuckDuckGo tool"""
        try:
            return Agent(
                model=Gemini(id="gemini-2.0-flash", api_key=config.GEMINI_API_KEY),
                tools=[DuckDuckGoTools()],
                instructions=[
                    "You are a professional research assistant specialized in technical topics.",
                    "Use the duckduckgo_search tool to research the topic",
                    "Analyze search results to identify key information and credible sources.",
                    "For each key finding, provide:",
                    "1. A clear fact/claim (string)",
                    "2. Brief supporting evidence (string)",
                    "3. The source URL (string)",
                    "4. Source credibility rating: High/Medium/Low (string)",
                    "Output in valid JSON format with EXACTLY this structure:",
                    """{
                "topic": "Research topic",
                "key_findings": [
                    {
                        "fact": "Specific fact or claim",
                        "supporting_evidence": "Supporting details",
                        "source_url": "Full source URL",
                        "source_credibility": "High/Medium/Low"
                    }
                ],
                "summary": "Brief research summary"
            }""",
                    "DO NOT include categories or grouped findings",
                    "Each finding should have its own source information",
                    "List findings directly under 'key_findings' without nesting",
                ],
                markdown=True,
                show_tool_calls=True,
            )
        except Exception as e:
            logger.error(f"Failed to create research agent: {str(e)}")
            raise

    def research_topic(self, topic: str) -> Dict[str, Any]:
        """Conduct comprehensive research on a given topic"""
        logger.info(f"Starting research on: {topic}")
        try:
            research_response: RunResponse = self.agent.run(
                f"Research the topic: {topic} and provide findings in JSON format"
            )

            research_data = self._parse_research_output(research_response.content.strip())  # type: ignore

            if "error" in research_data:
                logger.error(f"Research failed: {research_data['error']}")
            else:
                logger.info(
                    f"Research completed with {len(research_data.get('key_findings', []))} findings"
                )

            return research_data
        except Exception as e:
            logger.exception(f"Research failed: {str(e)}")
            return {"error": f"Research process failed: {str(e)}", "topic": topic}

    def _parse_research_output(self, output: str) -> Dict[str, Any]:
        try:
            clean_output = re.sub(r"```json|```", "", output).strip()
            research_data = json.loads(clean_output)

            if "key_findings" in research_data and research_data["key_findings"]:
                first_item = research_data["key_findings"][0]
                if "sources" in first_item and isinstance(first_item["sources"], list):
                    transformed_findings = []
                    for category in research_data["key_findings"]:
                        for source in category.get("sources", []):
                            transformed_findings.append(
                                {
                                    "fact": source.get("claim", ""),
                                    "supporting_evidence": source.get("evidence", ""),
                                    "source_url": source.get("url", "Unknown source"),
                                    "source_credibility": source.get(
                                        "credibility", "Medium"
                                    ),
                                }
                            )
                    research_data["key_findings"] = transformed_findings

            if "key_findings" not in research_data:
                raise ValueError("Missing key_findings in research output")

            if not isinstance(research_data["key_findings"], list):
                raise ValueError("key_findings should be a list")

            valid_findings = []
            for finding in research_data["key_findings"]:
                if "fact" not in finding:
                    finding["fact"] = finding.get("claim", "No fact provided")

                if "supporting_evidence" not in finding:
                    finding["supporting_evidence"] = finding.get(
                        "evidence", "No evidence provided"
                    )

                if "source_url" not in finding:
                    finding["source_url"] = finding.get("url", "Unknown source")

                if "source_credibility" not in finding:
                    finding["source_credibility"] = finding.get("credibility", "Medium")

                for field in [
                    "claim",
                    "evidence",
                    "url",
                    "credibility",
                    "sources",
                    "category",
                ]:
                    if field in finding:
                        del finding[field]

                valid_findings.append(finding)

            research_data["key_findings"] = valid_findings

            if "summary" not in research_data:
                research_data["summary"] = "Research summary not available"

            return research_data

        except (json.JSONDecodeError, ValueError) as e:
            return {
                "error": f"Research parsing failed: {str(e)}",
                "raw_output": output[:500] + "..." if len(output) > 500 else output,
            }
        except Exception as e:
            return {
                "error": f"Unexpected parsing error: {str(e)}",
                "raw_output": output[:500] + "..." if len(output) > 500 else output,
            }
