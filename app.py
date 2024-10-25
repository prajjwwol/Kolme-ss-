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

# Set up Hugging Face Inference Client for DialoGPT-large model
huggingface_api_token = os.getenv("HUGGING")
if not huggingface_api_token:
    raise ValueError("Environment variable 'HUGGING' is missing.")
hf_client = InferenceClient(model="microsoft/DialoGPT-large", token=huggingface_api_token)

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

    # Build the prompt for the LLM
    prompt = "Analyze and prioritize the following requirements based on complexity and business value:\n"
    for priority in priorities:
        prompt += f"\nRequirement: {priority.requirement}\nImportance: {priority.importance}/10\n"

    prompt += "\nProvide an analysis with insights on complexity, business value, and recommended prioritization."

    try:
        # Send the prompt to the LLM for generation
        response = hf_client.text_generation(prompt, max_new_tokens=300)
        logger.info(f"Raw response from LLM: {response}")

        # Handle the response as a string or dictionary
        if isinstance(response, str):
            generated_text = response.strip()
        elif isinstance(response, dict) and 'generated_text' in response:
            generated_text = response['generated_text'].strip()
        else:
            logger.warning("Unexpected response format from LLM.")
            raise HTTPException(status_code=500, detail="Unexpected response format from language model.")

        # Check if generated text is empty
        if not generated_text:
            logger.warning("Empty response received from LLM.")
            raise HTTPException(status_code=500, detail="Received an empty response from the language model.")

        return {"response": generated_text}

    except Exception as e:
        logger.error(f"Error in prioritize_request: {str(e)}")
        raise HTTPException(status_code=500, detail="Error while processing prioritization request.")

# Route to handle follow-up questions
@app.post("/followup")
async def handle_followup(input_data: FollowUpInput):
    conversation_history = "\n".join(input_data.history)
    followup_prompt = f"""
    Follow-up: "{input_data.follow_up}"
    Conversation history:
    {conversation_history}

    Provide additional insights or recommendations based on this context.
    """

    try:
        # Send follow-up prompt to the LLM
        response = hf_client.text_generation(followup_prompt, max_new_tokens=250)
        logger.info(f"Raw response from LLM: {response}")

        # Process the response
        if isinstance(response, str):
            generated_text = response.strip()
        elif isinstance(response, dict) and 'generated_text' in response:
            generated_text = response['generated_text'].strip()
        else:
            logger.warning("Unexpected response format from LLM.")
            raise HTTPException(status_code=500, detail="Unexpected response format from language model.")

        # Check if generated text is empty
        if not generated_text:
            logger.warning("Empty response received from LLM.")
            raise HTTPException(status_code=500, detail="Received an empty response from the language model.")

        # Append AI's response to history
        input_data.history.append(f"AI: {generated_text}")

        return {"response": generated_text, "history": input_data.history}

    except Exception as e:
        logger.error(f"Error in handle_followup: {str(e)}")
        raise HTTPException(status_code=500, detail="Error while processing follow-up request.")
