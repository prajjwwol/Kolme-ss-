from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from huggingface_hub import InferenceClient
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Serve static files (like HTML) from 'static' directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Hugging Face Inference Client for EleutherAI/gpt-neo-2.7B model
huggingface_api_token = os.getenv("HUGGING")
if not huggingface_api_token:
    raise ValueError("Environment variable 'HUGGING' is missing.")
hf_client = InferenceClient(model="EleutherAI/gpt-neo-2.7B", token=huggingface_api_token)

# Define PriorityInput class for individual priority input
class PriorityInput(BaseModel):
    requirement: str
    importance: int

# Define the input model for prioritization requests
class PrioritizationRequest(BaseModel):
    priorities: List[PriorityInput]

# Define the input model for follow-up requests
class FollowUpInput(BaseModel):
    follow_up: str
    history: List[str]

# Route to serve the HTML file at the root URL
@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open("static/index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        logger.error("index.html not found in static directory.")
        raise HTTPException(status_code=404, detail="index.html not found in static directory.")

# Route to handle the requirement prioritization
@app.post("/prioritize")
async def prioritize_request(input_data: PrioritizationRequest):
    priorities = input_data.priorities

    # Refined prompt with guiding example to help the model focus on structured output
    prompt = (
        "You are a software consultant providing prioritization analysis. For each requirement, "
        "give a one-sentence summary of complexity and business value. List requirements in order of importance.\n"
        "Example output:\n"
        "Requirement: User Registration - Complexity: Medium, Business Value: High.\n\n"
    )
    for priority in priorities:
        prompt += f"Requirement: {priority.requirement}, rated {priority.importance}/10 in importance.\n"

    prompt += "End of requirements. Provide concise analysis as shown in the example."

    try:
        # Send prompt to the model with controlled generation settings
        response = hf_client.text_generation(
            prompt,
            max_new_tokens=75,  # Reduced max tokens for concise output
            temperature=0.7,     # Controlled randomness
            top_p=0.9            # Focus on high-likelihood outputs
        )
        logger.info(f"Raw response from LLM: {response}")

        # Process the response and handle irrelevant output with a fallback
        generated_text = response.strip() if isinstance(response, str) else response.get('generated_text', '').strip()
        
        # Check for irrelevant responses and handle them gracefully
        if not generated_text or "website" in generated_text.lower():
            return {"response": "The model could not produce a relevant prioritization. Try rephrasing the requirements or consider a model upgrade."}

        return {"response": generated_text}

    except Exception as e:
        logger.error(f"Error in prioritize_request: {str(e)}")
        return {"response": "An error occurred while processing your request. Please try again later."}

# Route to handle follow-up questions
@app.post("/followup")
async def handle_followup(input_data: FollowUpInput):
    conversation_history = "\n".join(input_data.history)
    followup_prompt = (
        f"You are a helpful assistant. Here's a follow-up question: '{input_data.follow_up}'.\n"
        f"Here is the conversation history so far:\n{conversation_history}\n"
        "Please provide additional insights."
    )

    try:
        # Send follow-up prompt to the LLM with controlled generation length
        response = hf_client.text_generation(
            followup_prompt,
            max_new_tokens=250,
            temperature=0.7,
            top_p=0.9
        )
        logger.info(f"Raw response from LLM: {response}")

        # Handle empty or irrelevant responses with a fallback
        generated_text = response.strip() if isinstance(response, str) else response.get('generated_text', '').strip()
        if not generated_text or "website" in generated_text.lower():
            return {"response": "No follow-up response was generated. Please try again later."}

        # Append the model's response to conversation history
        input_data.history.append(f"AI: {generated_text}")
        return {"response": generated_text, "history": input_data.history}

    except Exception as e:
        logger.error(f"Error in handle_followup: {str(e)}")
        return {"response": "An error occurred while processing your follow-up. Please try again later."}
