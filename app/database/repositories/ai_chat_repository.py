"""AI Chat Repository for persisting conversational resume builder sessions."""

from typing import List, Dict, Optional
from datetime import datetime
import uuid
from app.database.repositories.base_repo import BaseRepository


class AIChatRepository(BaseRepository):
    """Repository for managing AI chat sessions in Firestore."""

    def __init__(self):
        super().__init__("ai_chats")

    async def get_user_chats(self, user_id: str) -> List[Dict]:
        """Fetch all chat sessions for a user, ordered by updated_at descending."""
        try:
            res = self._get_table().select("*").eq("user_id", user_id).order("updated_at", desc=True).execute()
            chats = res.data or []
            # Sort manually if Firestore ordering is pending index
            chats.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
            return chats
        except Exception as e:
            print(f"Error fetching user chats: {e}")
            return []

    async def get_chat(self, chat_id: str, user_id: str) -> Optional[Dict]:
        """Get a specific chat session by ID and user ID."""
        try:
            res = self._get_table().select("*").eq("id", chat_id).eq("user_id", user_id).execute()
            if res.data:
                return res.data[0]
            return None
        except Exception as e:
            print(f"Error fetching chat {chat_id}: {e}")
            return None

    async def save_chat(self, user_id: str, chat_id: Optional[str], title: str, messages: List[Dict]) -> str:
        """Create or update a chat session."""
        now_iso = datetime.now().isoformat()
        
        # Truncate title if needed
        clean_title = title.strip()[:50] or "Resume Chat"

        if chat_id:
            existing = await self.get_chat(chat_id, user_id)
            if existing:
                update_data = {
                    "title": clean_title,
                    "messages": messages,
                    "updated_at": now_iso
                }
                await self.update_one({"id": chat_id}, update_data)
                return chat_id

        # Create new chat session
        new_id = chat_id or str(uuid.uuid4())
        chat_doc = {
            "id": new_id,
            "user_id": user_id,
            "title": clean_title,
            "messages": messages,
            "created_at": now_iso,
            "updated_at": now_iso
        }
        res_id, _ = await self.insert_one(chat_doc)
        return res_id or new_id

    async def delete_chat(self, chat_id: str, user_id: str) -> bool:
        """Delete a chat session."""
        try:
            return await self.delete_one({"id": chat_id, "user_id": user_id})
        except Exception as e:
            print(f"Error deleting chat {chat_id}: {e}")
            return False
