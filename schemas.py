"""Pydantic models for request/response validation."""

from pydantic import BaseModel


class NoteCreate(BaseModel):
    """Request model for POST /notes."""
    title: str
    content: str


class Note(BaseModel):
    """Response model for all GET and POST endpoints."""
    id: int
    title: str
    content: str
    created_at: str


class VersionResponse(BaseModel):
    """Response model for GET /version."""
    version: str
    uptime: int


class PingResponse(BaseModel):
    """Response model for GET /ping."""
    message: str
