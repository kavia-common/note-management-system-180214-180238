from flask_smorest import Blueprint
from flask.views import MethodView

# Keep blueprint for root path to not break existing docs, but standardize name/desc
blp = Blueprint("Health", "health", url_prefix="/", description="Health check route")


@blp.route("/")
class HealthCheck(MethodView):
    def get(self):
        # Align with consistent response shape
        return {"data": {"status": "ok"}, "error": None}, 200
