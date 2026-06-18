import base64


def encode_image(image_file) -> tuple[str, str]:
    """Encode uploaded image to base64 and return (b64_string, mime_type)."""
    img_bytes = image_file.read()
    b64 = base64.b64encode(img_bytes).decode("utf-8")
    name = image_file.name.lower()
    if name.endswith(".png"):
        mime = "image/png"
    elif name.endswith(".gif"):
        mime = "image/gif"
    else:
        mime = "image/jpeg"
    return b64, mime


def analyze_image(image_file) -> dict:
    """Prepare image data for Groq vision API."""
    b64, mime = encode_image(image_file)
    return {
        "type": "image_url",
        "image_url": {
            "url": f"data:{mime};base64,{b64}"
        }
    }
