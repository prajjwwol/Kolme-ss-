from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from huggingface_hub import InferenceClient
from pydantic import BaseModel
import os

# Initialize FastAPI
app = FastAPI()

# Serve static files from the 'static' directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Hugging Face Inference Client
huggingface_api_token = os.getenv("HUGGING")
hf_client = InferenceClient(model="google/flan-t5-large", token=huggingface_api_token)

# Route to serve the HTML file
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html") as f:
        return f.read()

# Define a data model for the incoming requirement prioritization request
class RequirementInput(BaseModel):
    requirement: str
    importance: int
    complexity: int
    business_value: int
    history: list

class FollowUpInput(BaseModel):
    follow_up: str
    history: list

# Route to handle the requirement prioritization
# Route to handle the requirement prioritization
# Route to handle the requirement prioritization
@app.post("/prioritize")
async def prioritize_requirement(input_data: RequirementInput):
    conversation_history = "\n".join(input_data.history)

    prompt = f"""
    You are an expert software development consultant. Analyze the following requirement for prioritization:

    **Requirement**: {input_data.requirement}
    **Stakeholder Importance**: {input_data.importance}/10
    **Implementation Complexity**: {input_data.complexity}/10
    **Business Value**: {input_data.business_value}/10

    **Conversation History**: 
    {conversation_history}

    Please provide a well-structured response that avoids repetition, including:
    1. **Recommendation**: Should this requirement be prioritized for the next release? Please explain why with specific details.
    2. **Analysis**: Discuss the implications of the importance, complexity, and business value on the prioritization decision.
    3. **Actionable Insights**: List potential risks and challenges, and provide suggestions on how to mitigate them.
    4. **Next Steps**: If you recommend proceeding, outline specific steps for successful implementation.
    5. **Alternatives**: If not, explain why and suggest what should be focused on instead.

    Provide a concise, detailed, and coherent response without repeating the same points.
    """

    try:
        response = hf_client.text_generation(prompt, max_new_tokens=150)  # Adjust token limit
        generated_text = response.strip()

        # Update history with AI response
        input_data.history.append(f"AI: {generated_text}")

        return {"response": generated_text, "history": input_data.history}

    except Exception as e:
        return {"response": f"Error: {str(e)}", "history": input_data.history}
    
# Route to handle follow-up questions
@app.post("/followup")
async def handle_followup(input_data: FollowUpInput):
    conversation_history = "\n".join(input_data.history)

    followup_prompt = f"""
    You asked: "{input_data.follow_up}". Here is the conversation history:
    {conversation_history}

    Please provide additional insights or suggestions based on this input.
    """

    try:
        response = hf_client.text_generation(followup_prompt, max_new_tokens=250)
        generated_text = response.strip()

        # Update history with AI response
        input_data.history.append(f"AI: {generated_text}")

        return {"response": generated_text, "history": input_data.history}

    except Exception as e:
        return {"response": f"Error: {str(e)}", "history": input_data.history}
