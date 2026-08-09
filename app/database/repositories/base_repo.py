"""Base repository module for database operations using Firebase Cloud Firestore."""

from typing import Any, Dict, List, Optional
from app.database.connector import FirebaseConnectionManager


class FirestoreQueryWrapper:
    """Compatibility wrapper mimicking PostgREST query chaining for Firestore."""

    def __init__(self, collection_ref):
        self.collection_ref = collection_ref
        self.query_ref = collection_ref
        self._action = "select"
        self._payload = None

    def select(self, columns: str = "*"):
        return self

    def eq(self, column: str, value: Any):
        self.query_ref = self.query_ref.where(field_path=column, op_string="==", value=value)
        return self

    def order(self, column: str, desc: bool = False):
        try:
            from firebase_admin import firestore
            direction = firestore.Query.DESCENDING if desc else firestore.Query.ASCENDING
            self.query_ref = self.query_ref.order_by(column, direction=direction)
        except Exception:
            pass
        return self

    def limit(self, count: int):
        self.query_ref = self.query_ref.limit(count)
        return self

    def insert(self, data: Any):
        self._action = "insert"
        self._payload = data
        return self

    def update(self, data: Any):
        self._action = "update"
        self._payload = data
        return self

    def delete(self):
        self._action = "delete"
        return self

    def execute(self):
        class Result:
            def __init__(self, data):
                self.data = data

        if self._action == "insert":
            inserted_docs = []
            items = self._payload if isinstance(self._payload, list) else [self._payload]
            for item in items:
                d = dict(item) if isinstance(item, dict) else item
                doc_id = str(d.get("id")) if d.get("id") else None
                if doc_id:
                    doc_ref = self.collection_ref.document(doc_id)
                else:
                    doc_ref = self.collection_ref.document()
                    doc_id = doc_ref.id
                    d["id"] = doc_id
                doc_ref.set(d)
                inserted_docs.append(d)
            return Result(inserted_docs)

        elif self._action == "update":
            updated_docs = []
            try:
                docs = list(self.query_ref.stream())
                for doc in docs:
                    doc.reference.update(self._payload)
                    updated = doc.to_dict()
                    updated.update(self._payload)
                    updated_docs.append(updated)
            except Exception as e:
                print(f"Error updating Firestore documents: {e}")
            return Result(updated_docs)

        elif self._action == "delete":
            deleted_docs = []
            try:
                docs = list(self.query_ref.stream())
                for doc in docs:
                    d = doc.to_dict()
                    doc.reference.delete()
                    deleted_docs.append(d)
            except Exception as e:
                print(f"Error deleting Firestore documents: {e}")
            return Result(deleted_docs)

        else:  # select
            try:
                docs = list(self.query_ref.stream())
            except Exception:
                docs = list(self.collection_ref.stream())
            result_data = []
            for doc in docs:
                d = doc.to_dict()
                if "id" not in d:
                    d["id"] = doc.id
                result_data.append(d)
            return Result(result_data)


class BaseRepository:
    """Base repository class for database operations using Firebase Cloud Firestore."""

    def __init__(self, table_name: str):
        self.table_name = table_name
        self.connection_manager = FirebaseConnectionManager()

    def _get_collection(self):
        return self.connection_manager.collection(self.table_name)

    def _get_table(self):
        """Backwards-compatible PostgREST chain builder for Firestore."""
        return FirestoreQueryWrapper(self._get_collection())

    async def insert_one(self, data: Dict[str, Any]) -> tuple[str, Optional[str]]:
        """Insert a single record into Firestore. Returns (id, error_msg)."""
        payload = {k: v for k, v in data.items() if v is not None}
        try:
            coll = self._get_collection()
            doc_id = str(payload.get("id")) if payload.get("id") else None
            if doc_id:
                doc_ref = coll.document(doc_id)
            else:
                doc_ref = coll.document()
                doc_id = doc_ref.id
                payload["id"] = doc_id

            doc_ref.set(payload)
            return doc_id, None
        except Exception as e:
            error_msg = str(e)
            print(f"[ERROR] FIRESTORE INSERT ERROR [{self.table_name}]: {error_msg}")
            return "", error_msg

    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single record in Firestore."""
        try:
            coll = self._get_collection()
            if "id" in query and len(query) == 1:
                doc = coll.document(str(query["id"])).get()
                if doc.exists:
                    d = doc.to_dict()
                    if "id" not in d:
                        d["id"] = doc.id
                    return d
                return None

            ref = coll
            for key, value in query.items():
                ref = ref.where(field_path=key, op_string="==", value=value)

            docs = list(ref.limit(1).stream())
            if docs:
                d = docs[0].to_dict()
                if "id" not in d:
                    d["id"] = docs[0].id
                return d
            return None
        except Exception as e:
            print(f"Error finding record in {self.table_name}: {e}")
            return None

    async def find_many(self, query: Dict[str, Any], sort: List = None) -> List[Dict[str, Any]]:
        """Find multiple records in Firestore with memory sorting fallback."""
        try:
            coll = self._get_collection()
            ref = coll
            for key, value in query.items():
                ref = ref.where(field_path=key, op_string="==", value=value)

            try:
                if sort:
                    from firebase_admin import firestore
                    for field, direction in sort:
                        dir_enum = firestore.Query.DESCENDING if direction == -1 else firestore.Query.ASCENDING
                        ref = ref.order_by(field, direction=dir_enum)

                docs = list(ref.stream())
            except Exception:
                # Fallback without DB order_by in case composite index is missing
                ref_fallback = coll
                for key, value in query.items():
                    ref_fallback = ref_fallback.where(field_path=key, op_string="==", value=value)
                docs = list(ref_fallback.stream())

            result_list = []
            for doc in docs:
                d = doc.to_dict()
                if "id" not in d:
                    d["id"] = doc.id
                result_list.append(d)

            if sort and result_list:
                for field, direction in reversed(sort):
                    reverse = (direction == -1)
                    result_list.sort(key=lambda x: str(x.get(field) or ""), reverse=reverse)

            return result_list
        except Exception as e:
            print(f"Error finding records in {self.table_name}: {e}")
            return []

    async def update_one(self, query: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Update a single record in Firestore."""
        payload = dict(data)
        try:
            coll = self._get_collection()
            if "id" in query and len(query) == 1:
                doc_ref = coll.document(str(query["id"]))
                doc_ref.update(payload)
                return True

            ref = coll
            for key, value in query.items():
                ref = ref.where(field_path=key, op_string="==", value=value)

            docs = list(ref.limit(1).stream())
            if docs:
                docs[0].reference.update(payload)
                return True
            return False
        except Exception as e:
            print(f"[ERROR] FIRESTORE UPDATE ERROR [{self.table_name}]: {e}")
            return False

    async def delete_one(self, query: Dict[str, Any]) -> bool:
        """Delete a single record in Firestore."""
        try:
            coll = self._get_collection()
            if "id" in query and len(query) == 1:
                coll.document(str(query["id"])).delete()
                return True

            ref = coll
            for key, value in query.items():
                ref = ref.where(field_path=key, op_string="==", value=value)

            docs = list(ref.limit(1).stream())
            if docs:
                docs[0].reference.delete()
                return True
            return False
        except Exception as e:
            print(f"Error deleting record from {self.table_name}: {e}")
            return False
