from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import openai
import os
from pydantic import BaseModel

# Initialize FastAPI
app = FastAPI()

# Serve static files (like index.html) from the 'static' directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set your OpenAI API key here (make sure it's set in your Codespaces environment)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define a data model for the incoming requirement prioritization request
class RequirementInput(BaseModel):
    requirement: str
    importance: int
    complexity: int
    business_value: int

# Simple health check route
@app.get("/")
def read_root():
    return {"message": "Welcome to the GPT-based Web App!"}

# Route to handle the requirement prioritization
@app.post("/prioritize")
async def prioritize_requirement(input_data: RequirementInput):
    # Build the prompt for OpenAI based on input
    prompt = f"""
    We are prioritizing software requirements. Here is the input for one requirement:
    - Requirement: {input_data.requirement}
    - Stakeholder Importance: {input_data.importance}/10
    - Implementation Complexity: {input_data.complexity}/10
    - Business Value: {input_data.business_value}/10
    
    Based on these factors, please provide a prioritization score (higher is more priority) 
    and an explanation of why this requirement should be prioritized at that level.
    """

    # Call OpenAI's API to get a response for prioritization
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=200
    )

    # Return the GPT response as the prioritization result
    prioritization_result = response.choices[0].text.strip()
    return {"response": prioritization_result}
