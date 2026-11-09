from pathlib import Path
from flask import Flask, send_from_directory
from flask_cors import CORS
from .core.config import Config
from .api.health_routes import health_bp
from .api.vehicle_routes import vehicle_bp
from .api.anpr_routes import anpr_bp
from .api.challan_routes import challan_bp
from .api.auth_routes import auth_bp
from .api.inspection_routes import inspection_bp
from .api.helmet_routes import helmet_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS for frontend integration
    CORS(app, resources={r"/api/*": {"origins": config_class.CORS_ORIGINS}})

    # Register blueprints
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(vehicle_bp, url_prefix="/api")
    app.register_blueprint(anpr_bp, url_prefix="/api")
    app.register_blueprint(challan_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(inspection_bp, url_prefix="/api")
    app.register_blueprint(helmet_bp, url_prefix="/api")

    # Serve built frontend SPA if frontend/dist exists
    dist_dir = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
    if dist_dir.is_dir():
        @app.route("/", defaults={"path": ""})
        @app.route("/<path:path>")
        def serve_frontend(path):
            # Do not intercept api or static uploads
            if path.startswith("api/") or path.startswith("static/"):
                return {"error": "Not Found"}, 404
            target_file = dist_dir / path
            if path and target_file.is_file():
                return send_from_directory(str(dist_dir), path)
            return send_from_directory(str(dist_dir), "index.html")

    return app
