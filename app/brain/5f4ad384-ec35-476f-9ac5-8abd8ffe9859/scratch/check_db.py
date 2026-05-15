import asyncio
import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.database.connector import SupabaseConnectionManager

async def check_feedback_table():
    manager = SupabaseConnectionManager()
    client = manager.get_client()
    
    print(f"Checking table 'feedbacks'...")
    try:
        result = client.table("feedbacks").select("*").execute()
        print(f"Success! Found {len(result.data)} rows in 'feedbacks'.")
        if result.data:
            print("Latest feedback sample:")
            print(result.data[0])
    except Exception as e:
        print(f"Error accessing 'feedbacks' table: {e}")

if __name__ == "__main__":
    asyncio.run(check_feedback_table())
