import json
import base64
import os
import logging
import requests

import cloudinary
import cloudinary.uploader

logger = logging.getLogger()
logger.setLevel(logging.INFO)

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET")
)

MAX_IMAGE_BYTES = 10 * 1024 * 1024

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "POST,OPTIONS,GET",
    "Content-Type": "application/json",
}


def ok(body, status=200):
    return {
        "statusCode": status,
        "headers": CORS_HEADERS,
        "body": json.dumps(body)
    }


def error(message, status=400):
    return {
        "statusCode": status,
        "headers": CORS_HEADERS,
        "body": json.dumps({"error": message})
    }


def upload_to_cloudinary(image_bytes):

    result = cloudinary.uploader.upload(
        image_bytes,
        resource_type="image",
        folder="enhanced-images",
        overwrite=True
    )

    return result


def build_enhanced_url(public_id):

    cloud_name = os.environ["CLOUDINARY_CLOUD_NAME"]

    transformations = (
        "e_restore,"
        "e_improve,"
        "e_sharpen:250,"
        "w_2000,"
        "c_limit,"
        "e_upscale,"
        "q_auto:best,"
        "f_auto"
    )

    return (
        f"https://res.cloudinary.com/{cloud_name}/image/upload/"
        f"{transformations}/{public_id}"
    )

def download_image(url):

    response = requests.get(url, timeout=120)

    print("\n==============================")
    print("Cloudinary URL")
    print(url)
    print("==============================")

    print("\nStatus Code:")
    print(response.status_code)

    if response.status_code != 200:
        print("\nCloudinary Response:")
        print(response.text)

    response.raise_for_status()

    return response.content


def handle_enhance(payload):

    image_b64 = payload.get("image")

    if not image_b64:
        raise ValueError("image is required")

    try:
        image_bytes = base64.b64decode(image_b64)
    except Exception:
        raise ValueError("invalid base64 image")

    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise ValueError("image exceeds 10MB limit")

    upload_result = upload_to_cloudinary(image_bytes)

    public_id = upload_result["public_id"]

    enhanced_url = build_enhanced_url(public_id)

    logger.info("Enhanced URL: %s", enhanced_url)

    enhanced_bytes = download_image(enhanced_url)

    enhanced_b64 = base64.b64encode(
        enhanced_bytes
    ).decode("utf-8")

    return {
        "success": True,
        "public_id": public_id,
        "original_url": upload_result["secure_url"],
        "cloudinary_url": enhanced_url,
        "enhanced_image": enhanced_b64
    }


def lambda_handler(event, context):

    method = event.get("httpMethod")

    if method == "OPTIONS":
        return ok({"success": True})

    if method == "GET":
        return ok({
            "success": True,
            "service": "cloudinary-ai-upscale",
            "status": "healthy"
        })

    try:

        body = event.get("body")

        if not body:
            return error("missing request body")

        payload = json.loads(body)

        result = handle_enhance(payload)

        return ok(result)

    except ValueError as e:
        logger.warning(str(e))
        return error(str(e), 400)

    except Exception as e:
        logger.exception("Unhandled exception")
        return error(str(e), 500)