# Notes Backend (Flask)

A simple RESTful API for managing notes. Provides CRUD endpoints with search and pagination. Uses SQLAlchemy with SQLite by default.

## Features
- CRUD for notes at /notes and /notes/<id>
- Search (title/content), limit, offset for listing
- JSON response shape:
  - { "data": ..., "error": null } on success
  - { "data": null, "error": { "message": "..." } } on error
- Health endpoint: GET /health and GET /
- CORS enabled for development
- OpenAPI docs available at /docs

## Requirements
- Python 3.10+
- Dependencies in requirements.txt

## Setup
1. Create and activate a virtual environment.
2. Install requirements:
   pip install -r requirements.txt
3. Configure environment (optional):
   - Copy .env.example to .env and set DATABASE_URL if you want a different database.
   - Default is sqlite:///notes.db in the working directory.

## Running
The service is started by the environment's preview mechanism. For local dev:
  export FLASK_APP=run.py
  flask run  # or python run.py

Note: Port binding is controlled by the environment. This app does not hardcode the port.

## Environment
- DATABASE_URL: SQLAlchemy database URI. Example:
  - sqlite:///notes.db
  - postgresql+psycopg://user:pass@host:5432/dbname
  - mysql+pymysql://user:pass@host:3306/dbname

## API

- GET /health
  - Response: { "data": { "status": "ok" }, "error": null }

- GET /
  - Response: { "data": { "status": "ok" }, "error": null } (for backward compatibility)

- GET /notes?search=term&limit=20&offset=0
  - List notes with optional search by title/content.

- POST /notes
  - Body:
    {
      "title": "My note",
      "content": "Lorem ipsum",
      "tags": ["work","ideas"] // or "work, ideas"
    }

- GET /notes/<id>
  - Fetch a note by id.

- PUT /notes/<id>
  - Partial/full update. Preserve created_at.
  - Body: any subset of { "title", "content", "tags" }

- DELETE /notes/<id>
  - Delete a note.

### Response Examples

Success:
{
  "data": {"id":1,"title":"Example","content":"...","tags":["a"],"created_at":"...Z","updated_at":"...Z"},
  "error": null
}

Error:
{"data": null, "error": {"message": "Note not found."}}

### Curl examples

- Create:
  curl -X POST http://localhost:3001/notes -H "Content-Type: application/json" -d '{"title":"Test","content":"Hello","tags":["a","b"]}'

- List:
  curl "http://localhost:3001/notes?search=test&limit=10&offset=0"

- Get:
  curl http://localhost:3001/notes/1

- Update:
  curl -X PUT http://localhost:3001/notes/1 -H "Content-Type: application/json" -d '{"title":"Updated"}'

- Delete:
  curl -X DELETE http://localhost:3001/notes/1

## Migrations
This project initializes tables automatically. If you add Flask-Migrate later, it will work with the current SQLAlchemy setup.

## License
MIT
