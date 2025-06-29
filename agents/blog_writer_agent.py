# agents/blog_writer.py
import html
from agno.agent import Agent, RunResponse
from agno.team.team import Team
from agno.models.google import Gemini
from typing import Dict, Any, Optional, Iterator
import logging
import re
from utils.config import config
from textwrap import dedent

logger = logging.getLogger(__name__)


class BlogWriter:
    def __init__(self):
        self.architect = self._create_architect_agent()
        self.writer = self._create_writer_agent()
        self.editor = self._create_editor_agent()
        logger.info("Agno-based blog writing team initialized")

    def _create_architect_agent(self) -> Agent:
        return Agent(
            name="Content Architect",
            role="Design blog structure and outline",
            model=Gemini(id="gemini-2.0-flash", api_key=config.GEMINI_API_KEY),
            instructions=dedent(
                """
                Create comprehensive blog outlines from research data.
                Structure: Title, Introduction, 3-5 main sections with subheadings, Conclusion
                For each section, include 2-3 key points to cover.
                Output ONLY markdown-formatted outline.
                """
            ),
            markdown=True,
        )

    def _create_writer_agent(self) -> Agent:
        return Agent(
            name="Technical Writer",
            role="Draft blog content based on outline",
            model=Gemini(id="gemini-2.0-flash", api_key=config.GEMINI_API_KEY),
            instructions=dedent(
                """
                Create engaging technical blog content with rich visual elements:
                - Use nested bullet points for complex ideas
                - Include tables for comparisons (Markdown table syntax)
                - Add blockquotes for important insights
                - Include emojis sparingly for visual breaks but don't overuse it
                - Add section dividers (---) between major sections
                - Use bold/italic for emphasis on key terms
                - Create visual hierarchy with H2/H3 headers
                - Include 1-2 tables and 1-2 nested lists per long section if required
                
                Structure:
                1. Engaging hook in introduction
                2. 3-5 main sections with visual elements
                3. Conclusion with call-to-action
                
                Output ONLY markdown content with proper formatting.
                """
            ),
        )

    def _create_editor_agent(self) -> Agent:
        return Agent(
            name="Technical Editor",
            role="Polish content and add visual enhancements",
            model=Gemini(id="gemini-2.0-flash", api_key=config.GEMINI_API_KEY),
            instructions=dedent(
                """
                Enhance blog content for visual engagement:
                1. Ensure proper markdown formatting:
                    - Use # for headers
                    - Use * for emphasis
                    - Use > for blockquotes
                    - Use ` for inline code
                    - Use ``` for code blocks
                    - Convert \n to actual newlines
                    - Fix headers with proper spacing
                    - Format tables with alignment
                    - Ensure nested lists use consistent indentation
                2. Add visual elements where appropriate:
                    - Insert Mermaid diagrams for complex concepts
                    - Include relevant emojis in section headers
                    - Create comparison tables for technical specs
                3. Polish technical accuracy
                4. Add citations using [^1] notation
                5. Create reference section
                
                Critical Formatting Rules:
                - NEVER output literal "\n" - use actual line breaks
                - ALWAYS use proper Markdown syntax
                - Optimize for directly publishing to dev.to
                - Preserve emojis exactly as written (don't escape them)
                - Output ONLY the final formatted markdown without any confirmation text
                """
            ),
        )
        
    def _preserve_emojis(self, text: str) -> str:
        """Ensure emojis are properly formatted in markdown"""
        # Unescape HTML entities
        text = html.unescape(text)
        
        # Fix escaped emojis
        text = re.sub(r"\\:([a-z_]+):", r":\1:", text)
        
        # Fix HTML entity emojis
        text = re.sub(r"&#x([0-9A-Fa-f]+);", lambda m: chr(int(m.group(1), 16)), text)
        
        return text
        
    def _convert_escaped_newlines(self, raw: str) -> str:
        import re
        raw = re.sub(r'\\n', '\n', raw)
        raw = re.sub(r'\\t', '\t', raw)
        raw = re.sub(r'\\"', '"', raw)
        raw = re.sub(r"\\'", "'", raw)
        return raw


    def write_blog(self, research_data: Dict) -> Dict[str, Any]:
        """
        Generate technical blog using optimized workflow

        Args:
            research_data: Output from ResearchAnalysis

        Returns:
            Dictionary containing blog content
        """
        try:
            # Create outline
            outline = self._create_outline(research_data)

            # Draft content
            draft = self._draft_content(research_data, outline)

            # Finalize content
            
            final_blog = self._finalize_content(research_data, draft)
            final_blog = self._preserve_emojis(final_blog)
            final_blog = self._convert_escaped_newlines(final_blog)

            # Apply markdown formatting cleanup
            # final_blog = self._clean_markdown(final_blog)

            return {
                "research_topic": research_data.get("topic", ""),
                "final": final_blog,
            }
        except Exception as e:
            logger.exception(f"Blog creation failed: {str(e)}")
            return {"error": f"Blog creation failed: {str(e)}"}

    def _create_outline(self, research: Dict) -> str:
        """Generate blog structure from research"""
        prompt = dedent(
            f"""
        **Research Topic**: {research.get("topic", "")}
        **Key Findings**:
        {self._format_findings(research.get("key_findings", [])[:5])}
        
        **Task**: Create detailed blog outline with section key points.
        """
        )
        response = self.architect.run(prompt)
        return response.content.strip()  # type: ignore

    def _draft_content(self, research: Dict, outline: str) -> str:
        """Expand outline into full content"""
        prompt = dedent(
            f"""
        **Topic**: {research.get("topic", "")}
        **Outline**: 
        {outline}
        
        **Research Summary**:
        {research.get("summary", "")[:300]}
        
        **Task**: Write full blog content based on outline.
        """
        )
        response = self.writer.run(prompt)
        return response.content.strip()  # type: ignore

    def _finalize_content(self, research: Dict, content: str) -> str:
        """Polish and add citations"""
        prompt = dedent(
            f"""
        **Blog Content**:
        {content}
        
        **Research Sources**:
        {self._format_sources(research.get("key_findings", []))}
        
        **Task**: 
        - Add citations where needed using [^number] notation
        - Create references section at end
        - Polish grammar and flow
        - Output ONLY the final markdown content
        """
        )
        response = self.editor.run(prompt)
        
        # Decode escaped characters like \n into actual line breaks
        decoded_content = response.content.strip() # type: ignore
        return decoded_content 

    def _format_findings(self, findings: list) -> str:
        return "\n".join(f"- {f['fact']}" for f in findings)

    def _format_sources(self, findings: list) -> str:
        unique_sources = {}
        for f in findings:
            source = f.get("source_url", "User Provided")
            if source not in unique_sources:
                unique_sources[source] = f.get("source_credibility", "N/A")
        return "\n".join(f"- {url}" for url in unique_sources.keys())

    def apply_user_edits(self, blog_state: Dict, user_edits: str) -> Dict:
        """Apply user edits to blog content"""
        try:
            prompt = dedent(
                f"""
            **Current Blog**:
            {blog_state['final'][:3000]}
            
            **Requested Changes**:
            {user_edits}
            
            **Task**: Implement changes while preserving:
            - Technical accuracy
            - Citation format
            - Professional tone
            - Output ONLY the modified markdown
            """
            )

            response = self.editor.run(prompt)
            blog_state["final"] = response.content.strip()  # type: ignore
            blog_state["user_edits"] = user_edits
            return blog_state

        except Exception as e:
            logger.exception(f"Edit failed: {str(e)}")
            blog_state["error"] = f"Edit failed: {str(e)}"
            return blog_state


