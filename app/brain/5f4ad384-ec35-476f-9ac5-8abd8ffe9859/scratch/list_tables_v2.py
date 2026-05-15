import asyncio
import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.database.connector import SupabaseConnectionManager

async def list_tables():
    manager = SupabaseConnectionManager()
    client = manager.get_client()
    
    tables = ["users", "resumes", "feedback", "feedbacks", "organizations", "colleges"]
    for t in tables:
        try:
            client.table(t).select("count", count="exact").limit(1).execute()
            print(f"EXISTS: {t}")
        except Exception:
            print(f"MISSING: {t}")

if __name__ == "__main__":
    asyncio.run(list_tables())
