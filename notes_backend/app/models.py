from datetime import datetime
import json
from typing import Any, Dict, List, Optional, Union

from .db import db


class Note(db.Model):
    """Note model representing a note entry."""
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    content = db.Column(db.Text, nullable=True)
    # Store tags as JSON text to keep requirements simple; can be migrated to JSON type later.
    tags = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_tags(self, value: Optional[Union[str, List[str]]]) -> None:
        """Set tags field from list or string. Stores as JSON-encoded string."""
        if value is None:
            self.tags = None
            return

        if isinstance(value, list):
            # Ensure all items are strings
            tags_list = [str(v) for v in value]
            self.tags = json.dumps(tags_list)
        elif isinstance(value, str):
            # Accept comma-separated string or JSON string list
            value_str = value.strip()
            try:
                parsed = json.loads(value_str)
                if isinstance(parsed, list):
                    parsed = [str(v) for v in parsed]
                    self.tags = json.dumps(parsed)
                else:
                    # Not a list, treat the whole string as single tag
                    self.tags = json.dumps([value_str])
            except json.JSONDecodeError:
                # Not JSON: interpret as comma-separated tags
                parts = [t.strip() for t in value_str.split(",") if t.strip()]
                self.tags = json.dumps(parts)
        else:
            self.tags = json.dumps([str(value)])

    def get_tags(self) -> Optional[List[str]]:
        """Return tags as Python list, or None."""
        if self.tags is None:
            return None
        try:
            parsed = json.loads(self.tags)
            if isinstance(parsed, list):
                return [str(v) for v in parsed]
            return [str(parsed)]
        except Exception:
            # Corrupted or non-JSON, return as a single-element list fallback
            return [self.tags]

    # PUBLIC_INTERFACE
    def to_dict(self) -> Dict[str, Any]:
        """Serialize the Note to a dictionary suitable for JSON responses."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "tags": self.get_tags(),
            "created_at": self.created_at.isoformat() + "Z" if self.created_at else None,
            "updated_at": self.updated_at.isoformat() + "Z" if self.updated_at else None,
        }
