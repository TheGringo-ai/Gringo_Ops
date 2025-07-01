"""
ChatterFix AI Assistant Logic
This file contains the logic for the AI-powered features of ChatterFix,
including a troubleshooting assistant.
"""

import google.generativeai as genai
from ..config import GOOGLE_API_KEY
from . import app as backend

# Configure the generative AI model
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def get_troubleshooting_suggestion(work_order_id: str) -> str:
    """
    Generates a troubleshooting suggestion for a given work order based on its
    description and historical data.
    """
    work_order = backend.get_work_order(work_order_id)
    if not work_order:
        return "Work order not found."

    # Create a prompt for the AI model
    prompt = f"""
    I am a maintenance technician. Please provide troubleshooting suggestions for the following work order:

    **Title:** {work_order.title}
    **Description:** {work_order.description}
    **Priority:** {work_order.priority}
    **Equipment ID:** {work_order.equipment_id}

    Based on this information, what are the most likely causes of the problem and what steps should I take to resolve it? 
    Please be concise and provide a step-by-step guide.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating suggestion: {e}"
