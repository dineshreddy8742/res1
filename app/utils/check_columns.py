import asyncio
import os
from app.database.repositories.resume_repository import ResumeRepository

async def check_columns():
    repo = ResumeRepository()
    try:
        # We can try to select one and see keys
        result = repo._get_table().select("*").limit(1).execute()
        if result.data:
            print(f"Columns in {repo.table_name}:")
            print(list(result.data[0].keys()))
        else:
            print("No data in table to check columns")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_columns())
