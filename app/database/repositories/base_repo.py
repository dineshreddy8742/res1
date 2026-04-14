"""Base repository module for database operations using Supabase."""

import re
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.database.connector import SupabaseConnectionManager

class BaseRepository:
    """Base repository class for database operations using Supabase."""

    def __init__(self, table_name: str):
        self.table_name = table_name
        self.connection_manager = SupabaseConnectionManager()

    def _get_table(self):
        return self.connection_manager.table(self.table_name)

    @staticmethod
    def _get_missing_column_name(error: Exception) -> Optional[str]:
        """Extract a missing column name from a Supabase/PostgREST error."""
        message = str(error)
        match = re.search(r"Could not find the '([^']+)' column", message)
        return match.group(1) if match else None

    def _remove_unsupported_columns(
        self, data: Dict[str, Any], missing_column: Optional[str]
    ) -> Dict[str, Any]:
        """Drop the reported unsupported column so older schemas still work."""
        if not missing_column or missing_column not in data:
            return data
        return {key: value for key, value in data.items() if key != missing_column}

    async def insert_one(self, data: Dict[str, Any]) -> str:
        """Insert a single record into Supabase."""
        payload = dict(data)
        try:
            result = self._get_table().insert(payload).execute()
            if result.data and len(result.data) > 0:
                # Return the ID of the newly created record
                return str(result.data[0].get("id", ""))
            return ""
        except Exception as e:
            missing_column = self._get_missing_column_name(e)
            retry_payload = self._remove_unsupported_columns(payload, missing_column)
            if retry_payload != payload:
                try:
                    result = self._get_table().insert(retry_payload).execute()
                    if result.data and len(result.data) > 0:
                        return str(result.data[0].get("id", ""))
                    return ""
                except Exception as retry_error:
                    print(f"Error inserting record into {self.table_name}: {retry_error}")
                    return ""
            print(f"Error inserting record into {self.table_name}: {e}")
            return ""

    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single record in Supabase."""
        try:
            table = self._get_table().select("*")
            for key, value in query.items():
                table = table.eq(key, value)
            
            result = table.limit(1).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error finding record in {self.table_name}: {e}")
            return None

    async def find_many(self, query: Dict[str, Any], sort: List = None) -> List[Dict[str, Any]]:
        """Find multiple records in Supabase."""
        try:
            table = self._get_table().select("*")
            for key, value in query.items():
                table = table.eq(key, value)
            
            if sort:
                for field, direction in sort:
                    # direction -1 is DESC, 1 is ASC
                    table = table.order(field, desc=(direction == -1))
            
            result = table.execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error finding records in {self.table_name}: {e}")
            return []

    async def update_one(self, query: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Update a single record in Supabase."""
        payload = dict(data)
        try:
            # Build the update query properly
            table = self._get_table().update(payload)
            
            # Apply filters from query dict
            for key, value in query.items():
                table = table.eq(key, value)

            result = table.execute()
            return len(result.data) > 0 if result.data else False
        except Exception as e:
            missing_column = self._get_missing_column_name(e)
            retry_payload = self._remove_unsupported_columns(payload, missing_column)
            if retry_payload != payload:
                try:
                    table = self._get_table().update(retry_payload)
                    for key, value in query.items():
                        table = table.eq(key, value)
                    result = table.execute()
                    return len(result.data) > 0 if result.data else False
                except Exception as retry_error:
                    print(f"Error updating record in {self.table_name}: {retry_error}")
                    return False
            print(f"Error updating record in {self.table_name}: {e}")
            return False

    async def delete_one(self, query: Dict[str, Any]) -> bool:
        """Delete a single record in Supabase."""
        try:
            # Build the delete query properly
            table = self._get_table().delete()
            
            # Apply filters from query dict
            for key, value in query.items():
                table = table.eq(key, value)

            result = table.execute()
            return len(result.data) > 0 if result.data else False
        except Exception as e:
            print(f"Error deleting record from {self.table_name}: {e}")
            return False

