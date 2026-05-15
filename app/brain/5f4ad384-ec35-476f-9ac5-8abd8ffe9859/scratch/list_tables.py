import asyncio
import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.database.connector import SupabaseConnectionManager

async def list_tables():
    manager = SupabaseConnectionManager()
    client = manager.get_client()
    
    print("Attempting to list tables via a select from common tables...")
    tables = ["users", "resumes", "feedback", "feedbacks", "organizations", "colleges"]
    for t in tables:
        try:
            client.table(t).select("count", count="exact").limit(1).execute()
            print(f"✅ Table '{t}' exists.")
        except Exception:
            print(f"❌ Table '{t}' does NOT exist.")

if __name__ == "__main__":
    asyncio.run(list_tables())
