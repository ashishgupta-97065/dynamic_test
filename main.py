"""FastAPI application entry point with in-memory note storage."""

import datetime
import time
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response

from schemas import Note, NoteCreate, VersionResponse

APP_VERSION: str = "1.0.0"
START_TIME: float = time.time()

# Initialize FastAPI app
app = FastAPI()

# In-memory storage
notes: Dict[int, dict] = {}
next_id: int = 1


class NoteData:
    """Internal representation stored in memory dict."""

    def __init__(self, id: int, title: str, content: str, created_at: str):
        self.id = id
        self.title = title
        self.content = content
        self.created_at = created_at


@app.post("/notes", status_code=201)
def create_note(note_create: NoteCreate) -> Note:
    """
    Create a new note.

    Validate input (Pydantic handles this automatically).
    Generate new id from next_id counter, increment counter.
    Create NoteData with auto-generated id and current UTC timestamp.
    Store in notes dict.
    Return Note response model.
    """
    global next_id

    # Generate new ID
    note_id = next_id
    next_id += 1

    # Get current UTC timestamp in ISO 8601 format
    created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Create internal NoteData object
    note_data = NoteData(
        id=note_id,
        title=note_create.title,
        content=note_create.content,
        created_at=created_at
    )

    # Store in notes dict
    notes[note_id] = note_data

    # Return Note response model
    return Note(
        id=note_data.id,
        title=note_data.title,
        content=note_data.content,
        created_at=note_data.created_at
    )


@app.get("/notes")
def list_notes() -> List[Note]:
    """
    List all notes.

    Extract all values from notes dict.
    Convert to list of Note response models.
    Return list (may be empty).
    """
    return [
        Note(
            id=note_data.id,
            title=note_data.title,
            content=note_data.content,
            created_at=note_data.created_at
        )
        for note_data in notes.values()
    ]


@app.get("/notes/{id}")
def get_note(id: int) -> Note:
    """
    Get a single note by ID.

    Look up id in notes dict.
    If found, convert NoteData to Note response model and return.
    If not found, raise HTTPException(404).
    """
    if id not in notes:
        raise HTTPException(status_code=404, detail="Note not found")

    note_data = notes[id]
    return Note(
        id=note_data.id,
        title=note_data.title,
        content=note_data.content,
        created_at=note_data.created_at
    )


@app.delete("/notes/{id}")
def delete_note(id: int) -> Response:
    """
    Delete a note by ID.

    Look up id in notes dict.
    If found, delete it and return Response(status_code=204).
    If not found, raise HTTPException(404).
    """
    if id not in notes:
        raise HTTPException(status_code=404, detail="Note not found")

    del notes[id]
    return Response(status_code=204)


@app.get("/version")
def get_version() -> VersionResponse:
    """
    Return application version and process uptime.

    No authentication. No input. Reads APP_VERSION (module constant)
    and computes uptime as int(time.time() - START_TIME).
    """
    return VersionResponse(
        version=APP_VERSION,
        uptime=int(time.time() - START_TIME),
    )
