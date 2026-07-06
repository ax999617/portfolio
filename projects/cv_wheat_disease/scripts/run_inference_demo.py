from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from inference.model_inference import predict_image
from services.response_builder import build_predict_response
from services.risk_engine import evaluate_risk


def main() -> int:
    default_image = PROJECT_ROOT.parent.parent / "assets" / "results" / "cv_wheat_disease" / "02_frontend_upload_result_1.png"
    parser = argparse.ArgumentParser(description="Run the wheat disease demo inference chain.")
    parser.add_argument("--image", default=str(default_image), help="Input image path.")
    args = parser.parse_args()

    image_path = Path(args.image)
    image_bytes = image_path.read_bytes()
    inference = predict_image(image_bytes, image_path.name)
    risk = evaluate_risk(inference["class_id"], float(inference["confidence"]))
    response = build_predict_response(inference, risk)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
