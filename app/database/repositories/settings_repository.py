"""Settings repository module for handling global application settings."""

from typing import Dict, Optional
from app.database.repositories.base_repo import BaseRepository


class SettingsRepository(BaseRepository):
    """Repository for managing key-value system settings."""

    def __init__(self, table_name: str = "system_settings"):
        super().__init__(table_name)

    async def get_setting(self, key: str, default: str = None) -> str:
        """Get system setting by key."""
        try:
            result = self._get_table().select("value").eq("key", key).execute()
            if result.data and len(result.data) > 0:
                return result.data[0].get("value", default)
            return default
        except Exception as e:
            print(f"Error getting setting {key}: {e}")
            return default

    async def set_setting(self, key: str, value: str) -> bool:
        """Set or update system setting."""
        try:
            # Check if key exists
            existing = self._get_table().select("key").eq("key", key).execute()
            if existing.data and len(existing.data) > 0:
                result = self._get_table().update({"value": value}).eq("key", key).execute()
            else:
                result = self._get_table().insert({"key": key, "value": value}).execute()
            return len(result.data) > 0 if result.data else False
        except Exception as e:
            print(f"Error setting {key} to {value}: {e}")
            return False
