import asyncio
import os
from app.database.repositories.resume_repository import ResumeRepository

async def check_resume():
    repo = ResumeRepository()
    # Using the ID from the user's log
    resume_id = "82ded8e2-8177-4cc4-b18c-c314a836c6be"
    print(f"Checking for resume ID: {resume_id}")
    
    resume = await repo.get_resume_by_id(resume_id)
    if resume:
        print("✅ Found resume:")
        print(resume)
    else:
        print("❌ Resume NOT found in DB")
        
    # List a few resumes to see if any exist
    print("\nRecent resumes:")
    # We don't have a get_all_resumes, but we can use find_many
    resumes = await repo.find_many({}, sort=[("created_at", -1)])
    for r in resumes[:5]:
        print(f"- {r.get('id')} | {r.get('title')} | {r.get('status')}")

if __name__ == "__main__":
    asyncio.run(check_resume())
