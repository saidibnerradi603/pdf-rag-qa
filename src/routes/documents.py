from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse
from typing import Optional
import json
import io

from controllers.document_controller import DocumentController
from services.document_service import DocumentService
from utils.dependencies import get_current_user, get_supabase_client
from models.schemas import (
    DocumentUploadResponse,
    DocumentResponse,
    DocumentListResponse,
    DocumentDeleteResponse,
    ErrorResponse
)

router = APIRouter(prefix="/documents", tags=["Documents"])


def get_document_service(supabase=Depends(get_supabase_client)) -> DocumentService:
    """Dependency to get DocumentService."""
    return DocumentService(supabase)


def get_document_controller(
    service: DocumentService = Depends(get_document_service)
) -> DocumentController:
    """Dependency to get DocumentController."""
    return DocumentController(service)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=202,
    summary="Upload PDF document",
    description="Upload a PDF file for processing. Maximum size: 50MB.",
    responses={
        202: {"description": "Upload successful, processing started"},
        400: {"model": ErrorResponse, "description": "Invalid file"},
        413: {"model": ErrorResponse, "description": "File too large"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def upload_document(
    file: UploadFile = File(..., description="PDF file to upload"),
    metadata: Optional[str] = Form(None, description="Optional JSON metadata"),
    current_user: dict = Depends(get_current_user),
    controller: DocumentController = Depends(get_document_controller)
) -> DocumentUploadResponse:
    """
    Upload a PDF document.
    
    - **file**: PDF file (max 50MB)
    - **metadata**: Optional JSON string with title, tags, description
    
    Returns document ID and status.
    """
    metadata_dict = None
    if metadata:
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Invalid metadata JSON")
    
    return await controller.handle_upload(
        file=file,
        user_id=current_user["id"],
        metadata=metadata_dict
    )


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="List user's documents",
    description="Get all documents uploaded by the current user.",
    responses={
        200: {"description": "Documents retrieved successfully"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
def list_documents(
    limit: int = Query(100, ge=1, le=100, description="Max results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: dict = Depends(get_current_user),
    controller: DocumentController = Depends(get_document_controller)
) -> DocumentListResponse:
    """
    List all documents for the authenticated user.
    
    Supports pagination via limit and offset parameters.
    """
    return controller.handle_list(
        user_id=current_user["id"],
        limit=limit,
        offset=offset
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get document details",
    description="Retrieve details of a specific document.",
    responses={
        200: {"description": "Document found"},
        404: {"model": ErrorResponse, "description": "Document not found"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    controller: DocumentController = Depends(get_document_controller)
) -> DocumentResponse:
    """Get document by ID."""
    return controller.handle_get(document_id, current_user["id"])


@router.delete(
    "/{document_id}",
    response_model=DocumentDeleteResponse,
    summary="Delete document",
    description="Delete a document and all associated data (chunks, embeddings).",
    responses={
        200: {"description": "Document deleted"},
        404: {"model": ErrorResponse, "description": "Document not found"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    controller: DocumentController = Depends(get_document_controller)
) -> DocumentDeleteResponse:
    """
    Delete document permanently.
    
    This will also delete all associated chunks and embeddings (CASCADE).
    """
    return await controller.handle_delete(document_id, current_user["id"])


@router.get(
    "/{document_id}/download",
    summary="Download document",
    description="Download the original PDF file.",
    responses={
        200: {"description": "File download", "content": {"application/pdf": {}}},
        404: {"model": ErrorResponse, "description": "Document not found"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
def download_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    controller: DocumentController = Depends(get_document_controller)
):
    """Download the original PDF file."""
    file_bytes, filename = controller.handle_download(document_id, current_user["id"])
    
    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
