import os
from app import create_app
from app.core.config import Config

app = create_app(Config)

if __name__ == "__main__":
    port = Config.PORT
    debug = Config.DEBUG
    print(f"🚀 Starting Traffic Enforcement Backend on port {port} (Debug: {debug})...")
    app.run(host="0.0.0.0", port=port, debug=debug)
