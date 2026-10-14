"""API process owned by npm run dev; no frontend build or fixed port needed."""
import os
from pathlib import Path

from waitress import create_server
from backend.app import create_app


def main():
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    model_dir = os.environ.get("MODEL_DIR", str(root / "artifacts_neural_verified"))
    app = create_app(model_dir)
    if not app.extensions["prediction_service"].ready:
        raise SystemExit("Cannot load models. Check MODEL_DIR, Python dependencies and NLTK resources.")
    # OS chooses a free port; never reuse or terminate another user's server.
    server = create_server(app, host="127.0.0.1", port=0, threads=4)
    print(f"SMS_LAB_READY=http://127.0.0.1:{server.effective_port}", flush=True)
    try:
        server.run()
    finally:
        server.close()


if __name__ == "__main__":
    main()
