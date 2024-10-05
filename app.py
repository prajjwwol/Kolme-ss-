from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from huggingface_hub import InferenceApi  # Hugging Face Inference API
from pydantic import BaseModel
import os

# Initialize FastAPI
app = FastAPI()

# Serve static files from the 'static' directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the index.html file when the root URL ("/") is accessed
@app.get("/")
def serve_index():
    return FileResponse(os.path.join("static", "index.html"))

# Set up Hugging Face Inference API
# Ensure your HUGGINGFACEHUB_API_TOKEN is set in the environment
huggingface_api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
hf_api = InferenceApi(repo_id="gpt2", token=huggingface_api_token)  # Using GPT-2 model

# Define a data model for the incoming requirement prioritization request
class RequirementInput(BaseModel):
    requirement: str
    importance: int
    complexity: int
    business_value: int

# Route to handle the requirement prioritization
@app.post("/prioritize")
async def prioritize_requirement(input_data: RequirementInput):
    # Build the prompt to send to the model based on the input
    prompt = f"""
    Requirement: {input_data.requirement}
    Stakeholder Importance: {input_data.importance}/10
    Implementation Complexity: {input_data.complexity}/10
    Business Value: {input_data.business_value}/10

    Please prioritize this requirement and explain the reasoning.
    """

    try:
        # Call Hugging Face Inference API to generate the response
        response = hf_api(inputs=prompt)

        # Print the full response to see its structure (for debugging)
        print(f"Response from Hugging Face API: {response}")

        # Assuming the response is a dictionary with a 'generated_text' key
        generated_text = response.get("generated_text", "No text found")

        # Return the generated text as the response
        return {"response": generated_text}

    except Exception as e:
        # Handle API errors and provide useful feedback
        print(f"Error calling Hugging Face API: {str(e)}")  # Log the error for debugging
        return {"response": f"Error: {str(e)}"}
