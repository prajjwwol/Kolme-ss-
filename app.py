from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from huggingface_hub import InferenceClient
from pydantic import BaseModel
import os

# Initialize FastAPI
app = FastAPI()

# Serve static files from 'static' directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Define Hugging Face client with DialogGPT
huggingface_api_token = os.getenv("HUGGING")
hf_client = InferenceClient(model="microsoft/DialoGPT-large", token=huggingface_api_token)

# Models for request data
class RequirementInput(BaseModel):
    requirement: str
    importance: int
    complexity: int
    business_value: int
    history: list

class FollowUpInput(BaseModel):
    follow_up: str
    history: list

# Serve index.html at root URL
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r") as f:
        return f.read()

# Prioritization route
@app.post("/prioritize")
async def prioritize_requirement(input_data: RequirementInput):
    conversation_history = "\n".join(input_data.history)
    prompt = f"""
    You are an expert software development consultant. Analyze the following requirement for prioritization:

    **Requirement**: {input_data.requirement}
    **Stakeholder Importance**: {input_data.importance}/10
    **Implementation Complexity**: {input_data.complexity}/10
    **Business Value**: {input_data.business_value}/10

    **History**: {conversation_history}

    Please:
    1. Assess prioritization for this requirement.
    2. Discuss implications, risks, and provide actionable next steps.
    """

    try:
        response = hf_client.text_generation(prompt, max_new_tokens=200)
        generated_text = response.strip()
        input_data.history.append(f"AI: {generated_text}")
        return {"response": generated_text, "history": input_data.history}
    except Exception as e:
        return {"response": f"Error: {str(e)}", "history": input_data.history}

# Follow-up route
@app.post("/followup")
async def handle_followup(input_data: FollowUpInput):
    conversation_history = "\n".join(input_data.history)
    followup_prompt = f"""
    You asked: "{input_data.follow_up}". Here is the conversation history:
    {conversation_history}

    Please provide further insights on the discussed requirement.
    """

    try:
        response = hf_client.text_generation(followup_prompt, max_new_tokens=200)
        generated_text = response.strip()
        input_data.history.append(f"AI: {generated_text}")
        return {"response": generated_text, "history": input_data.history}
    except Exception as e:
        return JSONResponse(content={"response": f"Error: {str(e)}", "history": input_data.history}, status_code=500)
