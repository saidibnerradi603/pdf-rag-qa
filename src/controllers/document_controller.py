from fastapi import UploadFile, HTTPException
from typing import Dict, Any, Optional
import logging

from services.document_service import DocumentService
from models.schemas import (
    DocumentUploadResponse,
    DocumentResponse,
    DocumentListResponse,
    DocumentDeleteResponse
)

logger = logging.getLogger(__name__)


class DocumentController:
    """Controller for document management."""
    
    def __init__(self, document_service: DocumentService):
        self.service = document_service
    
    async def handle_upload(
        self,
        file: UploadFile,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DocumentUploadResponse:
        """Handle document upload request."""
        try:
            document = await self.service.upload_document(file, user_id, metadata)
            
            return DocumentUploadResponse(
                document_id=document["id"],
                file_name=document["file_name"],
                status=document["status"],
                bucket_path=document["bucket_path"],
                created_at=document["created_at"],
                message="Upload successful. Document is pending processing."
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Upload handler error: {str(e)}")
            raise HTTPException(status_code=500, detail="Upload failed")
    
    def handle_get(self, document_id: str, user_id: str) -> DocumentResponse:
        """Handle get document request."""
        document = self.service.get_document(document_id, user_id)
        return DocumentResponse(**document)
    
    def handle_list(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> DocumentListResponse:
        """Handle list documents request."""
        documents, total = self.service.list_documents(user_id, limit, offset)
        
        return DocumentListResponse(
            documents=[DocumentResponse(**doc) for doc in documents],
            total=total
        )
    
    async def handle_delete(
        self,
        document_id: str,
        user_id: str
    ) -> DocumentDeleteResponse:
        """Handle delete document request."""
        await self.service.delete_document(document_id, user_id)
        
        return DocumentDeleteResponse(
            message="Document deleted successfully",
            document_id=document_id
        )
    
    def handle_download(self, document_id: str, user_id: str) -> tuple[bytes, str]:
        """
        Handle download document request.
        
        Returns:
            Tuple of (file_bytes, filename)
        """
        document = self.service.get_document(document_id, user_id)
        file_bytes = self.service.download_document(document_id, user_id)
        
        return file_bytes, document["file_name"]
