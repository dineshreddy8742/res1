"""AI-powered resume optimization module.

This module provides the AtsResumeOptimizer class that leverages AI language models
(primarily via OpenRouter's OpenAI-compatible API) to analyze and optimize resumes 
based on job descriptions, improving compatibility with Applicant Tracking Systems (ATS).
"""

import json
import os
import re
import random
from typing import Any, Dict, List, Optional

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from app.services.ai.ats_scoring import ATSScorerLLM
from app.utils.token_tracker import TokenTracker


from app.core.config import settings

class AtsResumeOptimizer:
    """ATS Resume Optimizer.

    A class that uses AI language models to optimize resumes for Applicant Tracking
    Systems (ATS) based on specific job descriptions.
    """

    def __init__(
        self,
        model_name: str = None,
        resume: str = None,
        api_key: str = None,
        api_base: str = None,
        user_id: str = None,
    ) -> None:
        """Initialize the AI model for resume processing.

        Args:
            model_name: The name of the model to use (e.g., 'google/gemini-2.0-flash-001' via OpenRouter).
            resume: The resume text to be optimized.
            api_key: OpenRouter API key (OpenAI-compatible).
            api_base: Base URL for the API (e.g., 'https://openrouter.ai/api/v1').
            user_id: Optional user ID for token tracking.
        """
        self.model_name = model_name or settings.MODEL_NAME
        self.resume = resume
        # Support single key or rotation from pool
        self.api_keys = [api_key] if api_key else getattr(settings, 'API_KEYS', [])
        self.api_key = random.choice(self.api_keys) if self.api_keys else None
        self.api_base = api_base or settings.API_BASE
        self.user_id = user_id

        # Initialize LLM component and output parser
        self.llm = self._get_openai_model()
        self.output_parser = JsonOutputParser()
        self.chain = None
        
        # Initialize ATS scorer for skill extraction and analysis
        self.ats_scorer = None
        if self.api_key and self.api_base and self.model_name:
            self.ats_scorer = ATSScorerLLM(
                model_name=self.model_name,
                api_key=self.api_key,
                api_base=self.api_base,
                user_id=self.user_id,
            )

        self._setup_chain()

    def _get_openai_model(self) -> ChatOpenAI:
        """Initialize the model with appropriate settings.
        
        Returns:
            ChatOpenAI: Configured language model instance (OpenRouter compatible)
        """
        if self.model_name:
            # Create LLM instance with token tracking for usage monitoring
            return TokenTracker.get_tracked_langchain_llm(
                model_name=self.model_name,
                temperature=0,
                api_key=self.api_key,
                api_base=self.api_base,
                feature="resume_optimization",
                user_id=self.user_id,
                metadata={"resume_length": len(self.resume) if self.resume else 0}
            )
        else:
            # Fallback to standard model if no specific model is configured
            return ChatOpenAI(
                temperature=0,
                openai_api_key=self.api_key,
                openai_api_base=self.api_base,
                default_headers={
                    "HTTP-Referer": "https://aurarise.app",
                    "X-Title": "AuraRise Protocol (OpenRouter)"
                }
            )

    def _get_prompt_template(self, missing_skills: Optional[List[str]] = None) -> PromptTemplate:
        """Create the PromptTemplate for ATS resume optimization.
        
        Args:
            missing_skills: A list of skills identified as missing from the resume
                        that should be incorporated if the candidate has them.

        Returns:
            PromptTemplate: A prompt template with instructions for resume optimization.
        """
        recommended_skills_section = ""
        if missing_skills and len(missing_skills) > 0:
            skills_list = ", ".join([f"'{skill}'" for skill in missing_skills])
            recommended_skills_section = f"""
        ## RECOMMENDED SKILLS TO ADD
        
        The following skills were identified as potentially valuable for this position but may be missing or not prominently featured in the resume:
        
        {skills_list}
        
        If the candidate has any experience with these skills, even minor exposure:
        - Highlight them prominently in the skills section
        - Look for ways to showcase these skills in past experience descriptions
        - Ensure you're using the exact terminology as listed
        - Look for related skills or experience that could be reframed to match these requirements
        - Reframe transferable or implied experience to match the job requirements where ethically possible
        - Be assertive in surfacing any relevant experience, even if it is not an exact match, as long as it is truthful
        - Do NOT fabricate experience with these skills, only highlight them if they exist
        """
        
        template = f"""
        # ROLE: Elite ATS Resume Architect & Career Strategist
        You are a world-class ATS (Applicant Tracking System) Specialist specializing in high-performance career optimization. Your mission is to re-engineer the candidate's raw resume into a surgically precise, ATS-dominating master document.
        
        ## TARGET AUDIENCE: FRESHERS & STUDENTS
        For candidates with < 2 years of industry experience (Freshers/Students), you MUST:
        - **Aggressively Surface Potential**: Transform academic projects, hackathon wins, and internships into "Professional Experience" or high-impact "Project" narratives.
        - **Highlight Hackathons**: Treat major hackathon wins (especially Google Cloud, Smart India Hackathon, etc.) as critical proof of delivery and technical prowess.
        - **Technical Density**: Ensure the "Skills" and "Projects" sections are dense with industry-standard keywords from the Job Description.
        - **Resilience & Leadership**: Showcase leadership roles (e.g., Campus Ambassador, Team Lead) as evidence of soft-skill maturity.

        ## INPUT DATA:
        
        ### TARGET JOB DESCRIPTION:
        {{job_description}}

        ### CANDIDATE'S SOURCE DATA:
        {{resume}}
        
        {recommended_skills_section}

        ## STRICT ARCHITECTURAL CONSTRAINTS:

        1. **SURGICAL ALIGNMENT (JD-FIRST)**
            - Every single bullet point MUST map to a core requirement in the Job Description.
            - Use the EXACT terminology found in the JD (e.g., if it says 'LLMs', don't just say 'Large Language Models').
            - If a skill is missing from the resume but hinted at (e.g., Python is there but 'FastAPI' is needed), bridge the gap through project descriptions where valid.

        2. **THE 'RESULT-FIRST' FORMULA**
            - Every task/goal MUST follow: [Strong Action Verb] + [Quantifiable Impact/Metric] + [Technical Tool Used].
            - Example: "Engineered a RAG-based chatbot using LangChain that reduced query latency by 40%."
            - Avoid weak phrases like "Responsible for", "Helped with", "Knowledge of".

        3. **FRESHER ENHANCEMENT PROTOCOL**
            - Transform "Student Hackathon Winner" into "Grand Finalist & Team Lead - Gen AI Exchange Hackathon (Google Cloud)".
            - Expand internships (e.g., L&T AI Intern) to show production-level impact (Agentic AI, Workflow Orchestration).
            - Ensure the 'Education' section highlights the CGPA and relevant specializations clearly.

        4. **FORMATTING & ATS HYGIENE**
            - No tables, no columns, no fancy symbols.
            - Standard Headings: "Professional Experience", "Education", "Projects", "Skills", "Extra-Curricular Activities".
            - Precise Dates: MM/YYYY - MM/YYYY or MM/YYYY - Present.
            - **NO PLACEHOLDERS**: If a field (like LinkedIn, GitHub, Portfolio, or specific dates) is missing from the source data, leave it as an empty string ("") or omit it. DO NOT use "Not Specified", "N/A", or other negative placeholders.

        5. **STRICT DATA VALIDATION**:
            - **EXPERIENCES**: Exactly 4 high-impact tasks per role. No more, no less.
            - **PROJECTS**: Exactly 2 strategic goals + 1 end result per project.
            - **SKILLS**: Group into 'Hard Skills' (Technical) and 'Soft Skills' (Leadership/Communication).
            - **METRICS**: Aim for at least 2 bullet points with numbers (%, $, hours, or counts) per experience.

        ## OUTPUT SCHEMA (STRICT JSON ONLY):

        You MUST return ONLY a valid JSON object with NO additional text, explanation, or commentary.
        The JSON must follow this EXACT structure:

        {{{{
            "user_information": {{{{
                "name": "",
                "main_job_title": "",
                "profile_description": "",
                "email": "user@example.com",
                "phone": "+1-234-567-890",
                "portfolio": "https://portfolio.me",
                "linkedin": "https://linkedin.com/in/user",
                "github": "https://github.com/user",
                "leetcode": "",
                "geeksforgeeks": "",
                "experiences": [
                    {{{{
                        "job_title": "",
                        "company": "",
                        "start_date": "",
                        "end_date": "",
                        "location": "",
                        "four_tasks": [
                            "Task 1: strong action verb + result",
                            "Task 2: strong action verb + result",
                            "Task 3: strong action verb + result",
                            "Task 4: strong action verb + result"
                        ]
                    }}}}
                ],
                "education": [
                    {{{{
                        "institution": "",
                        "degree": "",
                        "location": "",
                        "description": "",
                        "start_date": "",
                        "end_date": ""
                    }}}}
                ],
                "skills": {{{{
                    "hard_skills": [],
                    "soft_skills": []
                }}}},
                "hobbies": []
            }}}},
            "projects": [
                {{{{
                    "project_name": "",
                    "two_goals_of_the_project": [
                        "Goal 1: objective cleared",
                        "Goal 2: objective cleared"
                    ],
                    "project_end_result": "",
                    "tech_stack": []
                }}}}
            ],
            "certificate": [
                {{{{
                    "name": "",
                    "institution" : "",
                    "description": "",
                    "date": ""
                }}}}
            ],
            "extra_curricular_activities": [
                {{{{
                    "name": "",
                    "description": "",
                    "start_date": "",
                    "end_date": ""
                }}}}
            ],
            "ats_metrics": {{{{
                "optimized_score": 0,
                "matching_skills": [],
                "missing_skills": [],
                "recommendation": ""
            }}}}
        }}}}

        IMPORTANT REQUIREMENTS:
        1. The "four_tasks" array must contain EXACTLY 4 items for each experience
        2. The "two_goals_of_the_project" array must contain EXACTLY 2 items for each project
        3. Make sure all dates follow a consistent format (YYYY-MM or MM/YYYY)
        4. Ensure all fields are filled with appropriate data extracted from the resume
        5. Return ONLY the JSON object with no other text
        """
        return PromptTemplate.from_template(template=template)

    def _setup_chain(self, missing_skills: Optional[List[str]] = None) -> None:
        """Set up the processing pipeline for job descriptions and resumes.

        This method configures the functional composition approach with the pipe operator
        to create a processing chain from prompt template to language model.
        
        Args:
            missing_skills: List of skills identified as missing that should be incorporated
                        into the optimization prompt.
        """
        prompt_template = self._get_prompt_template(missing_skills)
        self.chain = prompt_template | self.llm

    async def generate_ats_optimized_resume_json_async(
        self, job_description: str, missing_skills: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate an ATS-optimized resume asynchronously for better speed."""
        if not self.resume:
            return {"error": "Resume not provided"}

        try:
            score_results = {}

            provided_missing_skills = missing_skills if missing_skills is not None else None

            # Step 1: Analyze resume against job description asynchronously only
            # when we were not already given missing skills by the caller.
            if provided_missing_skills is None and self.ats_scorer:
                try:
                    score_results = await self.ats_scorer.compute_match_score_async(
                        self.resume, job_description
                    )
                    provided_missing_skills = score_results.get("missing_skills", [])
                except Exception as e:
                    print(f"Warning: Async ATS scoring failed: {e}")

            self._setup_chain(provided_missing_skills)

            # Step 2: Generate optimized resume
            result = await self.chain.ainvoke(
                {"job_description": job_description, "resume": self.resume}
            )

            # Step 3: Parse JSON
            content = result.content if hasattr(result, "content") else result
            try:
                # Direct JSON parsing or extraction
                json_match = re.search(r"(\{[\s\S]*\})", content)
                if json_match:
                    json_result = json.loads(json_match.group(1))
                    
                    # Merge initial score if we computed it
                    if score_results:
                        if "ats_metrics" not in json_result:
                            json_result["ats_metrics"] = {}
                        json_result["ats_metrics"]["initial_score"] = score_results.get("final_score", 0)
                        # Only fill if LLM didn't fill its own metrics
                        if not json_result["ats_metrics"].get("matching_skills"):
                             json_result["ats_metrics"]["matching_skills"] = score_results.get("matching_skills", [])
                        if not json_result["ats_metrics"].get("missing_skills"):
                             json_result["ats_metrics"]["missing_skills"] = score_results.get("missing_skills", [])
                    
                    return json_result
            except Exception as e:
                return {"error": f"JSON parse error: {e}", "raw": content[:500]}

            return {"error": "Failed to generate valid JSON"}

        except Exception as e:
            return {"error": f"Async processing error: {e}"}

    def generate_ats_optimized_resume_json(
        self, job_description: str, missing_skills: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate an ATS-optimized resume in JSON format (synchronous)."""
        if not self.resume:
            return {"error": "Resume not provided"}

        try:
            score_results = {}
            provided_missing_skills = missing_skills if missing_skills is not None else None

            if provided_missing_skills is None and self.ats_scorer:
                score_results = self.ats_scorer.compute_match_score(self.resume, job_description)
                provided_missing_skills = score_results.get("missing_skills", [])

            self._setup_chain(provided_missing_skills)

            result = self.chain.invoke({"job_description": job_description, "resume": self.resume})
            content = result.content if hasattr(result, "content") else result
            
            json_match = re.search(r"(\{[\s\S]*\})", content)
            if json_match:
                json_result = json.loads(json_match.group(1))
                
                # Merge initial score
                if score_results:
                    if "ats_metrics" not in json_result:
                        json_result["ats_metrics"] = {}
                    json_result["ats_metrics"]["initial_score"] = score_results.get("final_score", 0)
                
                return json_result
            return {"error": "JSON not found"}
        except Exception as e:
            return {"error": str(e)}


if __name__ == "__main__":
    pass
