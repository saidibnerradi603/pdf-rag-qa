from fastapi import UploadFile, HTTPException, status
import re
import uuid
from pathlib import Path


class FileValidator:
    """Utility class for file validation."""
    
    @staticmethod
    def validate_pdf(
        file: UploadFile,
        max_size_mb: int = 5,
        allowed_types: list[str] = ["application/pdf"]
    ) -> None:
        """
        Validate uploaded PDF file.
        
        Args:
            file: Uploaded file
            max_size_mb: Maximum file size in MB
            allowed_types: Allowed MIME types
            
        Raises:
            HTTPException: If validation fails
        """
        # Check if file exists
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Check MIME type
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Only PDF files are allowed. Got: {file.content_type}"
            )
        
        # Check file extension
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must have .pdf extension"
            )
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        size_bytes = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        max_size_bytes = max_size_mb * 1024 * 1024
        if size_bytes > max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {max_size_mb}MB"
            )
        
        # Check if file is empty
        if size_bytes == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal attacks.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        filename = Path(filename).name
        
        filename = re.sub(r'[^\w\s\-\.]', '', filename)
        
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1)
            filename = name[:250] + '.' + ext
        
        return filename
    
    @staticmethod
    def generate_storage_path(user_id: str, filename: str) -> tuple[str, str]:
        """
        Generate unique storage path for file.
        
        Args:
            user_id: User UUID
            filename: Original filename
            
        Returns:
            Tuple of (document_id, storage_path)
        """
        document_id = str(uuid.uuid4())
        sanitized_name = FileValidator.sanitize_filename(filename)
        
        # Path structure: {user_id}/{document_id}_{filename}
        storage_path = f"{user_id}/{document_id}_{sanitized_name}"
        
        return document_id, storage_path
