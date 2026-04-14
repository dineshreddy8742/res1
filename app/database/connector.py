"""Supabase connection management module.

This module provides the SupabaseConnectionManager class which handles
database connections to Supabase and implements the singleton pattern
to ensure efficient connection reuse throughout the application.
"""

from typing import Optional
from supabase import Client, create_client
from app.core.config import settings


class SupabaseConnectionManager:
    """Singleton class for managing Supabase connections.

    This class implements the singleton pattern to ensure only one instance of the
    connection manager exists. It provides methods for retrieving the Supabase client.

    Attributes:
        _instance: Class-level singleton instance reference
        _client: Supabase client instance
    """

    _instance: Optional["SupabaseConnectionManager"] = None
    _client: Optional[Client] = None

    def __new__(cls):
        """Singleton implementation ensuring only one instance is created.

        Returns:
            The singleton SupabaseConnectionManager instance
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the SupabaseConnectionManager."""
        pass

    def get_client(self) -> Client:
        """Get the Supabase client instance, creating it if it doesn't exist.

        Uses SERVICE ROLE KEY for admin operations (bypasses RLS).
        Falls back to ANON KEY if service role is not available.

        Returns:
            Client: Supabase client for database operations
        """
        if self._client is None:
            # Prefer service role key for admin operations (bypasses RLS)
            api_key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
            
            if settings.SUPABASE_SERVICE_ROLE_KEY:
                print("Using Supabase SERVICE ROLE KEY (admin mode)")
            else:
                print("WARNING: Using Supabase ANON KEY - RLS policies may block access")
            
            self._client = create_client(settings.SUPABASE_URL, api_key)
        return self._client

    def table(self, table_name: str):
        """Get a reference to a Supabase table.

        Args:
            table_name: Name of the table to query

        Returns:
            Supabase table reference for CRUD operations
        """
        return self.get_client().table(table_name)
