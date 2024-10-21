from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from huggingface_hub import InferenceClient  # Hugging Face Inference Client
from pydantic import BaseModel
import os

# Initialize FastAPI
app = FastAPI()

# Serve static files from the 'static' directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the index.html file at the root URL
@app.get("/")
def serve_index():
    return FileResponse(os.path.join(os.path.abspath("static"), "index.html"))

# Set up Hugging Face Inference Client
huggingface_api_token = os.getenv("HUGGING")  # Use 'HUGGING' as the environment variable
hf_client = InferenceClient(model="google/flan-t5-large", token=huggingface_api_token)  # Use Flan-T5 large

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
    You are an expert software development advisor. Help me prioritize the following requirement by considering its importance, complexity, and business value.

    Requirement: {input_data.requirement}
    Stakeholder Importance: {input_data.importance}/10
    Implementation Complexity: {input_data.complexity}/10
    Business Value: {input_data.business_value}/10

    Please analyze and explain whether this requirement should be prioritized in the next release. Provide a detailed explanation, focusing on how these factors influence the prioritization, and feel free to suggest improvements or ask clarifying questions if necessary.
    """

    try:
        # Call Hugging Face Inference Client to generate the response, with max_length specified
        response = hf_client.text_generation(prompt, max_new_tokens=200)

        # Return the generated text as the response
        return {"response": response}

    except Exception as e:
        # Handle errors and provide useful feedback
        print(f"Error generating response: {str(e)}")  # Log the error for debugging
        return {"response": f"Error: {str(e)}"}
