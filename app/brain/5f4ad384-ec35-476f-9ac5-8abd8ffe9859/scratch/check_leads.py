import asyncio
import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.database.connector import SupabaseConnectionManager

async def check_leads():
    manager = SupabaseConnectionManager()
    client = manager.get_client()
    try:
        result = client.table("leads").select("*").limit(5).execute()
        print(f"Leads content: {result.data}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_leads())
