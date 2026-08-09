"""Firebase connection management module.

This module provides the FirebaseConnectionManager class which handles
database connections to Firebase Cloud Firestore and implements the singleton pattern
to ensure efficient connection reuse throughout the application.
"""

import os
from typing import Any, Optional
import firebase_admin
from firebase_admin import credentials, firestore
from app.core.config import settings


class FirebaseConnectionManager:
    """Singleton class for managing Firebase Admin SDK and Firestore connections."""

    _instance: Optional["FirebaseConnectionManager"] = None
    _db: Optional[Any] = None

    def __new__(cls):
        """Singleton implementation ensuring only one instance is created."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize FirebaseConnectionManager."""
        pass

    def get_db(self):
        """Get the Firestore client instance, creating it if it doesn't exist."""
        if self._db is None:
            if not firebase_admin._apps:
                cred_path = settings.FIREBASE_CREDENTIALS_PATH or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
                if cred_path and os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred, {"projectId": settings.FIREBASE_PROJECT_ID})
                    print(f"🔥 Initialized Firebase Admin SDK from credentials: {cred_path}")
                else:
                    # Clean invalid GOOGLE_APPLICATION_CREDENTIALS from env to prevent google.auth crash
                    g_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
                    if g_creds and not os.path.exists(g_creds):
                        os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)

                    options = {"projectId": settings.FIREBASE_PROJECT_ID}
                    try:
                        firebase_admin.initialize_app(options=options)
                        print(f"🔥 Initialized Firebase Admin SDK (Project ID: {settings.FIREBASE_PROJECT_ID})")
                    except Exception as e:
                        print(f"⚠️ Firebase initialization notice: {e}")
            
            # Clean invalid GOOGLE_APPLICATION_CREDENTIALS before initializing Firestore client
            g_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            if g_creds and not os.path.exists(g_creds):
                os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)

            self._db = firestore.client()
        return self._db

    def get_client(self):
        """Alias for get_db to maintain backwards compatibility."""
        return self.get_db()

    def collection(self, collection_name: str):
        """Get a reference to a Firestore collection.

        Args:
            collection_name: Name of the collection to query

        Returns:
            CollectionReference for CRUD operations
        """
        return self.get_db().collection(collection_name)

    # Table alias for compatibility with PostgREST/Supabase table semantics
    def table(self, table_name: str):
        return self.collection(table_name)


# Legacy alias for smooth transition
SupabaseConnectionManager = FirebaseConnectionManager
