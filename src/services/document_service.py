from supabase import Client
from fastapi import UploadFile, HTTPException, status
from typing import Dict, Any, Optional
import logging

from repositories.document_repository import DocumentRepository
from utils.file_utils import FileValidator
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class DocumentService:
    """Service for document management operations."""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.repository = DocumentRepository(supabase)
        self.bucket_name = settings.storage_bucket_name
    
    async def upload_document(
        self,
        file: UploadFile,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload PDF document to storage and create database record.
        
        Args:
            file: Uploaded PDF file
            user_id: User UUID
            metadata: Optional metadata
            
        Returns:
            Created document record
            
        Raises:
            HTTPException: If upload fails
        """
        try:
            # Validate file
            FileValidator.validate_pdf(
                file,
                max_size_mb=settings.max_file_size_mb,
                allowed_types=settings.allowed_mime_types
            )
            
            # Generate storage path
            document_id, storage_path = FileValidator.generate_storage_path(
                user_id,
                file.filename
            )
            
            # Read file content
            file_content = await file.read()
            
            # Upload to Supabase Storage
            try:
                self.supabase.storage.from_(self.bucket_name).upload(
                    path=storage_path,
                    file=file_content,
                    file_options={"content-type": "application/pdf"}
                )
            except Exception as storage_error:
                logger.error(f"Storage upload failed: {str(storage_error)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to upload file to storage"
                )
            
            # Create database record
            try:
                document = self.repository.create(
                    document_id=document_id,
                    user_id=user_id,
                    file_name=file.filename,
                    bucket_path=storage_path,
                    metadata=metadata
                )
                
                logger.info(f"Document uploaded successfully: {document_id}")
                return document
                
            except Exception as db_error:
               
                try:
                    self.supabase.storage.from_(self.bucket_name).remove([storage_path])
                except:
                    pass
                
                logger.error(f"Database insert failed: {str(db_error)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create document record"
                )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during upload: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Upload failed"
            )
    
    def get_document(self, document_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get document by ID.
        
        Args:
            document_id: Document UUID
            user_id: User UUID
            
        Returns:
            Document record
            
        Raises:
            HTTPException: If not found
        """
        document = self.repository.get_by_id(document_id, user_id)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return document
    
    def list_documents(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[list[Dict[str, Any]], int]:
        """
        List user's documents.
        
        Args:
            user_id: User UUID
            limit: Max results
            offset: Pagination offset
            
        Returns:
            Tuple of (documents, total_count)
        """
        return self.repository.list_by_user(user_id, limit, offset)
    
    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """
        Delete document (file + database record).
        
        Args:
            document_id: Document UUID
            user_id: User UUID
            
        Returns:
            True if deleted
            
        Raises:
            HTTPException: If not found or deletion fails
        """
        document = self.get_document(document_id, user_id)
        
        try:
            self.supabase.storage.from_(self.bucket_name).remove([document["bucket_path"]])
        except Exception as e:
            logger.warning(f"Failed to delete file from storage: {str(e)}")
        
        success = self.repository.delete(document_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete document"
            )
        
        logger.info(f"Document deleted: {document_id}")
        return True
    
    def download_document(self, document_id: str, user_id: str) -> bytes:
        """
        Download document file.
        
        Args:
            document_id: Document UUID
            user_id: User UUID
            
        Returns:
            File bytes
            
        Raises:
            HTTPException: If not found or download fails
        """
        document = self.get_document(document_id, user_id)
        
        try:
            file_bytes = self.supabase.storage.from_(self.bucket_name).download(
                document["bucket_path"]
            )
            return file_bytes
            
        except Exception as e:
            logger.error(f"Failed to download file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to download file"
            )
