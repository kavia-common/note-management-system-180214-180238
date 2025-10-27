from flask import Flask, jsonify
from flask_cors import CORS
from flask_smorest import Api

from .db import init_db
from .routes.health import blp as health_blp
from .routes.notes import notes_bp

# Initialize application
app = Flask(__name__)
app.url_map.strict_slashes = False

# Enable CORS for development (all origins)
CORS(app, resources={r"/*": {"origins": "*"}})

# OpenAPI / Swagger UI configuration
app.config["API_TITLE"] = "Notes API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/docs"
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

# Initialize database
init_db(app)

# Setup API and register blueprints
api = Api(app)
api.register_blueprint(health_blp)

# Register notes routes (Blueprint from standard Flask)
app.register_blueprint(notes_bp)


# PUBLIC_INTERFACE
@app.get("/health")
def health():
    """Health check endpoint returning service status."""
    return jsonify({"data": {"status": "ok"}, "error": None}), 200
