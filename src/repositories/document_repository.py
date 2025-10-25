from supabase import Client
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DocumentRepository:
    """Repository for document database operations."""
    
    def __init__(self, supabase: Client):
        self.db = supabase
    
    def create(
        self,
        document_id: str,
        user_id: str,
        file_name: str,
        bucket_path: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create new document record.
        
        Args:
            document_id: Document UUID
            user_id: User UUID
            file_name: Original filename
            bucket_path: Path in storage bucket
            metadata: Optional metadata
            
        Returns:
            Created document record
        """
        try:
            data = {
                "id": document_id,
                "user_id": user_id,
                "file_name": file_name,
                "bucket_path": bucket_path,
                "status": "pending",
                "metadata": metadata or {}
            }
            
            result = self.db.table("documents").insert(data).execute()
            
            if not result.data:
                raise Exception("Failed to create document record")
            
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Error creating document: {str(e)}")
            raise
    
    def get_by_id(self, document_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get document by ID (with ownership check via RLS).
        
        Args:
            document_id: Document UUID
            user_id: User UUID (for RLS)
            
        Returns:
            Document record or None
        """
        try:
            result = self.db.table("documents")\
                .select("*")\
                .eq("id", document_id)\
                .execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Error fetching document: {str(e)}")
            return None
    
    def list_by_user(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[list[Dict[str, Any]], int]:
        """
        List all documents for a user.
        
        Args:
            user_id: User UUID
            limit: Max results
            offset: Pagination offset
            
        Returns:
            Tuple of (documents, total_count)
        """
        try:
           
            result = self.db.table("documents")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            
            
            count_result = self.db.table("documents")\
                .select("id", count="exact")\
                .eq("user_id", user_id)\
                .execute()
            
            total = count_result.count if count_result.count else 0
            
            return result.data, total
            
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            return [], 0
    
    def delete(self, document_id: str, user_id: str) -> bool:
        """
        Delete document record (RLS ensures ownership).
        
        Args:
            document_id: Document UUID
            user_id: User UUID
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            result = self.db.table("documents")\
                .delete()\
                .eq("id", document_id)\
                .execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return False
    
    def update_status(
        self,
        document_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update document status.
        
        Args:
            document_id: Document UUID
            status: New status (pending, processing, completed, failed)
            error_message: Optional error message
            
        Returns:
            True if updated
        """
        try:
            data = {"status": status}
            
            if error_message:
                data["metadata"] = {"error": error_message}
            
            result = self.db.table("documents")\
                .update(data)\
                .eq("id", document_id)\
                .execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Error updating document status: {str(e)}")
            return False
