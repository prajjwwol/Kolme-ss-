# models/huggingface_model.py
import os
from huggingface_hub import InferenceClient
from config import Config

API_TOKEN = Config.HUGGINGFACE_API_KEY
MODEL_ID = "google/flan-t5-xxl"

# Initialize the InferenceClient
client = InferenceClient(token=API_TOKEN)

def analyze_with_flan(requirement):
    # Create a prompt for the model
    prompt = (
        f"Prioritize the requirement: '{requirement}' based on importance, complexity, and urgency. "
        "Provide a detailed prioritization analysis."
    )

    # Use the `client.text_generation` method correctly for text generation
    try:
        response = client.text_generation(model=MODEL_ID, prompt=prompt, max_length=200)
        result = response[0]["generated_text"] if response and "generated_text" in response[0] else "No text generated"
    except Exception as e:
        result = f"Error in calling model: {e}"

    return result
