"""
Vision Agent for ChatterFix
This module uses Google Cloud Vision AI to analyze images for text and objects,
enabling functionality like identifying parts from a picture.
"""

import io
from google.cloud import vision
from PIL import Image
# Assuming backend modules are accessible for integration
from backend import inventory, assets, models

def get_vision_client():
    """Initializes and returns a Vision AI client."""
    # This uses Application Default Credentials to authenticate.
    # Ensure you have run `gcloud auth application-default login`
    try:
        return vision.ImageAnnotatorClient()
    except Exception as e:
        print(f"Error initializing Vision client: {e}")
        print("Please ensure you are authenticated with `gcloud auth application-default login`")
        return None

def analyze_image_for_text(image_content: bytes) -> str:
    """
    Analyzes an image and extracts any text found using Google Cloud Vision OCR.

    Args:
        image_content: The byte content of the image.

    Returns:
        The detected text as a single string, with newlines, or an empty string.
    """
    client = get_vision_client()
    if not client:
        return "Error: Vision API client not available."

    image = vision.Image(content=image_content)
    
    response = client.text_detection(image=image)
    if response.error.message:
        raise Exception(
            f'{response.error.message}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'
        )

    texts = response.text_annotations
    if texts:
        # The first text annotation contains the full detected text block.
        return texts[0].description.strip()
    return ""

def process_image_and_find_part(image_content: bytes) -> dict:
    """
    Orchestrates the process of analyzing an image to find a part.

    Args:
        image_content: The byte content of the uploaded image.

    Returns:
        A dictionary containing the result, extracted text, and any found part.
    """
    try:
        # Step 1: Extract text from the image
        extracted_text = analyze_image_for_text(image_content)
        if not extracted_text or "Error" in extracted_text:
            return {"status": "error", "message": "Could not extract text from image or Vision API is unavailable."}

        # Step 2: Clean up the text and search for potential part numbers/names
        # This can be improved with more sophisticated parsing logic.
        potential_ids = extracted_text.split('\n')
        found_part = None
        
        # Step 3: Search for a part using the extracted text
        for pid in potential_ids:
            pid = pid.strip()
            if not pid:
                continue
            
            # Use the inventory module to find the part
            part = inventory.get_part_by_id_or_name(pid)
            if part:
                found_part = part
                break # Stop when the first match is found

        if found_part:
            return {
                "status": "success",
                "message": f"Found part: {found_part.name}",
                "extracted_text": extracted_text,
                "part": found_part.to_dict() # Assuming a to_dict method on the model
            }
        else:
            return {
                "status": "not_found",
                "message": "Text was extracted, but no matching part was found in the inventory.",
                "extracted_text": extracted_text,
                "part": None
            }

    except Exception as e:
        return {"status": "error", "message": str(e)}
