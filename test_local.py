import argparse
import base64
import json
import os
from pathlib import Path

# --------------------------------------------------
# Load .env before importing lambda_function
# --------------------------------------------------
env_file = Path(".env")

if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        if "=" in line:
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip()

from lambda_function import lambda_handler


# --------------------------------------------------
# Build Lambda Event
# --------------------------------------------------
def make_event(image_path: str):
    image_bytes = Path(image_path).read_bytes()

    body = {
        "image": base64.b64encode(image_bytes).decode("utf-8")
    }

    return {
        "httpMethod": "POST",
        "body": json.dumps(body)
    }


# --------------------------------------------------
# Main
# --------------------------------------------------
def main():

    parser = argparse.ArgumentParser(
        description="Cloudinary Image Enhancement Test"
    )

    parser.add_argument(
        "--image",
        required=True,
        help="Input image path"
    )

    args = parser.parse_args()

    image_path = Path(args.image)

    if not image_path.exists():
        print(f"\n[ERROR] File not found: {image_path}")
        return

    print(f"\n[INFO] Processing: {image_path}")

    event = make_event(str(image_path))

    try:

        result = lambda_handler(event, {})

        print("\nStatus Code:")
        print(result["statusCode"])

        body = json.loads(result["body"])

        # ------------------------------------------
        # Show clean response (hide base64 image)
        # ------------------------------------------
        display_body = body.copy()

        if "enhanced_image" in display_body:
            display_body["enhanced_image"] = (
                f"<base64 omitted ({len(body['enhanced_image'])} chars)>"
            )

        print("\nResponse:")
        print(json.dumps(display_body, indent=2))

        if not body.get("success"):
            print("\n[ERROR] Enhancement failed")
            return

        # ------------------------------------------
        # Save image
        # ------------------------------------------
        enhanced_b64 = body["enhanced_image"]

        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)

        output_file = results_dir / (
            f"{image_path.stem}_enhanced.jpg"
        )

        with open(output_file, "wb") as f:
            f.write(base64.b64decode(enhanced_b64))

        print("\n[SUCCESS]")
        print(f"Saved: {output_file}")

        if body.get("cloudinary_url"):
            print(f"Cloudinary URL: {body['cloudinary_url']}")

    except Exception as e:
        print("\n[ERROR]")
        print(str(e))


# --------------------------------------------------
# Entry Point
# --------------------------------------------------
if __name__ == "__main__":
    main()