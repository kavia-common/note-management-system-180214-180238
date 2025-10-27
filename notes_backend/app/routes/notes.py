from typing import Any, Dict, Optional, Tuple

from flask import Blueprint, request
from sqlalchemy import or_

from ..db import db
from ..models import Note

notes_bp = Blueprint("notes", __name__, url_prefix="/notes")


def ok(data: Any, status: int = 200):
    return {"data": data, "error": None}, status


def err(message: str, status: int = 400):
    return {"data": None, "error": {"message": message}}, status


def parse_pagination() -> Tuple[int, int]:
    """Parse limit and offset with defaults and caps."""
    try:
        limit = int(request.args.get("limit", "20"))
    except ValueError:
        limit = 20
    try:
        offset = int(request.args.get("offset", "0"))
    except ValueError:
        offset = 0
    # Safety bounds
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    return limit, offset


def validate_note_payload(payload: Dict[str, Any], partial: bool = False) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Validate incoming payload for note creation/update.

    Args:
        payload: Raw JSON dict
        partial: If True, allow missing title on update.
    Returns:
        (normalized_payload, error_message)
    """
    if not isinstance(payload, dict):
        return None, "Invalid JSON body."

    title = payload.get("title")
    content = payload.get("content")
    tags = payload.get("tags")

    normalized: Dict[str, Any] = {}

    if title is None:
        if not partial:
            return None, "Field 'title' is required."
    else:
        if not isinstance(title, str):
            return None, "Field 'title' must be a string."
        title = title.strip()
        if len(title) < 1 or len(title) > 200:
            return None, "Field 'title' length must be between 1 and 200 characters."
        normalized["title"] = title

    if content is not None:
        if not isinstance(content, str):
            return None, "Field 'content' must be a string."
        normalized["content"] = content

    if tags is not None and not isinstance(tags, (list, str)):
        return None, "Field 'tags' must be a list of strings or a comma-separated string."
    if tags is not None:
        normalized["tags"] = tags

    return normalized, None


@notes_bp.get("")
def list_notes():
    """List notes with optional search, limit, and offset."""
    limit, offset = parse_pagination()
    search = request.args.get("search", "").strip()

    query = Note.query
    if search:
        like = f"%{search}%"
        query = query.filter(or_(Note.title.ilike(like), Note.content.ilike(like)))

    total = query.count()
    items = query.order_by(Note.created_at.desc()).offset(offset).limit(limit).all()

    return ok(
        {
            "items": [n.to_dict() for n in items],
            "limit": limit,
            "offset": offset,
            "total": total,
        }
    )


@notes_bp.post("")
def create_note():
    """Create a new note."""
    payload = request.get_json(silent=True) or {}
    validated, error = validate_note_payload(payload, partial=False)
    if error:
        return err(error, 400)

    note = Note(
        title=validated["title"],
        content=validated.get("content"),
    )
    if "tags" in validated:
        note.set_tags(validated["tags"])

    db.session.add(note)
    db.session.commit()
    return ok(note.to_dict(), 201)


@notes_bp.get("/<int:note_id>")
def get_note(note_id: int):
    """Fetch a note by id."""
    note = Note.query.get(note_id)
    if not note:
        return err("Note not found.", 404)
    return ok(note.to_dict())


@notes_bp.put("/<int:note_id>")
def update_note(note_id: int):
    """Update (partial or full) a note, preserving created_at."""
    note = Note.query.get(note_id)
    if not note:
        return err("Note not found.", 404)

    payload = request.get_json(silent=True) or {}
    validated, error = validate_note_payload(payload, partial=True)
    if error:
        return err(error, 400)

    if "title" in validated:
        note.title = validated["title"]
    if "content" in validated:
        note.content = validated["content"]
    if "tags" in validated:
        note.set_tags(validated["tags"])

    db.session.commit()
    return ok(note.to_dict())


@notes_bp.delete("/<int:note_id>")
def delete_note(note_id: int):
    """Delete a note by id."""
    note = Note.query.get(note_id)
    if not note:
        return err("Note not found.", 404)
    db.session.delete(note)
    db.session.commit()
    return ok({"id": note_id, "deleted": True})
