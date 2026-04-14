"""
Scalability module — Background task queue management for resume optimization.

Handles thousands of concurrent users by:
- Processing AI optimization in the background (non-blocking)
- Limiting concurrent AI calls with a semaphore (prevents LLM rate limits)
- Tracking job status (pending → processing → done/failed)
- Auto-retrying failed jobs once
"""

import asyncio
import logging
import os
import traceback
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ────────────────────────────────────────────────────────────────────────────────
# Concurrency Gate
# Limits simultaneous AI calls to avoid OpenAI/DeepSeek RPM limits.
# Rule of thumb: 1 concurrent call ≈ ~15–30s, so 20 concurrent = handles ~80 req/min
# Increase MAX_CONCURRENT_AI_CALLS if you have a higher-tier API plan.
# ────────────────────────────────────────────────────────────────────────────────
MAX_CONCURRENT_AI_CALLS = int(os.getenv("MAX_CONCURRENT_AI_CALLS", "20"))
_ai_semaphore: Optional[asyncio.Semaphore] = None


def get_ai_semaphore() -> asyncio.Semaphore:
    """Get or create the global AI concurrency semaphore."""
    global _ai_semaphore
    if _ai_semaphore is None:
        _ai_semaphore = asyncio.Semaphore(MAX_CONCURRENT_AI_CALLS)
    return _ai_semaphore


# ────────────────────────────────────────────────────────────────────────────────
# In-memory job tracker (fast status lookup without DB round-trip)
# ────────────────────────────────────────────────────────────────────────────────
_job_status: Dict[str, Dict[str, Any]] = {}


def set_job_status(resume_id: str, status: str, error: Optional[str] = None):
    """Update the in-memory job status for fast polling."""
    _job_status[resume_id] = {
        "status": status,
        "error": error,
        "updated_at": datetime.now().isoformat(),
    }


def get_job_status(resume_id: str) -> Optional[Dict[str, Any]]:
    """Get the current in-memory job status."""
    return _job_status.get(resume_id)


def clear_job_status(resume_id: str):
    """Remove completed job from in-memory tracker to free memory."""
    _job_status.pop(resume_id, None)


# ────────────────────────────────────────────────────────────────────────────────
# Background Task Runner
# ────────────────────────────────────────────────────────────────────────────────
async def run_optimization_background(
    resume_id: str,
    resume_content: str,
    job_description: str,
    api_key: str,
    api_base_url: str,
    model_name: str,
    repo,  # ResumeRepository instance
):
    """
    Run resume optimization in background with:
    - Concurrency limiting (semaphore)
    - Status tracking (pending → processing → done/failed)
    - Auto-retry once on failure
    - DB status updates so the frontend can poll

    This function is fire-and-forget — call with FastAPI BackgroundTasks.
    """
    set_job_status(resume_id, "processing")

    # Update DB status to 'processing'
    try:
        await repo.update_one(
            {"id": resume_id},
            {"status": "processing", "updated_at": datetime.now().isoformat()},
        )
    except Exception as db_err:
        logger.warning(f"[{resume_id}] Could not set DB status to processing: {db_err}")

    semaphore = get_ai_semaphore()
    max_retries = 2

    for attempt in range(1, max_retries + 1):
        try:
            async with semaphore:
                logger.info(
                    f"[{resume_id}] Starting AI optimization (attempt {attempt}/{max_retries}), "
                    f"semaphore slots used: {MAX_CONCURRENT_AI_CALLS - semaphore._value}"
                )
                result = await _do_optimization(
                    resume_id=resume_id,
                    resume_content=resume_content,
                    job_description=job_description,
                    api_key=api_key,
                    api_base_url=api_base_url,
                    model_name=model_name,
                    repo=repo,
                )

            if result:
                set_job_status(resume_id, "done")
                logger.info(f"[{resume_id}] Optimization completed successfully.")
                return  # success — exit retry loop

        except Exception as e:
            err_msg = str(e)
            logger.error(
                f"[{resume_id}] Optimization attempt {attempt} failed: {err_msg}\n"
                + traceback.format_exc()
            )
            if attempt == max_retries:
                # Final failure — record error in DB
                set_job_status(resume_id, "failed", error=err_msg)
                try:
                    await repo.update_one(
                        {"id": resume_id},
                        {
                            "status": "failed",
                            "error_message": err_msg[:1000],
                            "updated_at": datetime.now().isoformat(),
                        },
                    )
                except Exception as db_err:
                    logger.error(f"[{resume_id}] Could not persist failure status: {db_err}")
            else:
                # Wait before retry (exponential backoff)
                await asyncio.sleep(2**attempt)


async def _do_optimization(
    resume_id: str,
    resume_content: str,
    job_description: str,
    api_key: str,
    api_base_url: str,
    model_name: str,
    repo,
) -> bool:
    """
    Internal: Runs the actual AI scoring + optimization + DB update.
    Runs in a thread pool so synchronous LangChain calls don't block the event loop.
    """
    import json
    from app.services.ai.ats_scoring import ATSScorerLLM
    from app.services.ai.model_ai import AtsResumeOptimizer
    from app.database.models.resume import ResumeData

    loop = asyncio.get_event_loop()

    # --- Step 1: Score original resume (runs sync LangChain in thread) ---
    def score_original():
        scorer = ATSScorerLLM(
            model_name=model_name, api_key=api_key, api_base=api_base_url
        )
        return scorer.compute_match_score(resume_content, job_description)

    original_score_result = await loop.run_in_executor(None, score_original)
    original_ats_score = int(original_score_result.get("final_score", 0))
    missing_skills = original_score_result.get("missing_skills", [])
    logger.info(f"[{resume_id}] Original ATS score: {original_ats_score}")

    # --- Step 2: Generate optimized resume ---
    def optimize():
        optimizer = AtsResumeOptimizer(
            model_name=model_name,
            resume=resume_content,
            api_key=api_key,
            api_base=api_base_url,
        )
        return optimizer.generate_ats_optimized_resume_json(job_description)

    result = await loop.run_in_executor(None, optimize)

    if "error" in result:
        raise RuntimeError(f"AI error: {result['error']}")

    # --- Step 3: Validate result ---
    optimized_data = ResumeData.parse_obj(result)

    # --- Step 4: Score optimized resume ---
    def score_optimized():
        scorer = ATSScorerLLM(
            model_name=model_name, api_key=api_key, api_base=api_base_url
        )
        return scorer.compute_match_score(json.dumps(result), job_description)

    optimized_score_result = await loop.run_in_executor(None, score_optimized)
    optimized_ats_score = int(optimized_score_result.get("final_score", 0))
    score_improvement = optimized_ats_score - original_ats_score

    logger.info(
        f"[{resume_id}] Optimized ATS: {optimized_ats_score} "
        f"(improvement: +{score_improvement})"
    )

    # --- Step 5: Persist everything to DB ---
    await repo.update_optimized_data(
        resume_id,
        optimized_data,
        optimized_ats_score,
        original_ats_score=original_ats_score,
        matching_skills=optimized_score_result.get("matching_skills", []),
        missing_skills=optimized_score_result.get("missing_skills", []),
        score_improvement=score_improvement,
        recommendation=optimized_score_result.get("recommendation", ""),
    )

    # Update status to 'done' in DB
    await repo.update_one(
        {"id": resume_id},
        {"status": "done", "updated_at": datetime.now().isoformat()},
    )

    return True
