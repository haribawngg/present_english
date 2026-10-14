"""Run the complete Flask demo using Waitress: python run_demo.py."""
import argparse
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--models", default=os.environ.get("MODEL_DIR", "artifacts_neural_verified"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    os.chdir(root)
    if not (root / "frontend/dist/index.html").exists():
        parser.error("Frontend missing. Run npm --prefix frontend ci and npm --prefix frontend run build")
    from backend.main import create_app
    from waitress import serve
    app = create_app(args.models)
    print(f"SMS Lab: http://{args.host}:{args.port}", flush=True)
    serve(app, host=args.host, port=args.port, threads=4)


if __name__ == "__main__":
    main()
