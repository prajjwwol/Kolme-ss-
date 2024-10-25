from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load GPT-J-6B with memory-efficient settings
model_name = "EleutherAI/gpt-j-6B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,  # Use float16 for lower memory usage
    device_map="auto"           # Spread model across available devices
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

class PriorityInput(BaseModel):
    requirement: str
    importance: int

class PrioritizationRequest(BaseModel):
    priorities: List[PriorityInput]

class FollowUpInput(BaseModel):
    follow_up: str
    history: List[str]

@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open("static/index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        logger.error("index.html not found in static directory.")
        raise HTTPException(status_code=404, detail="index.html not found in static directory.")

@app.post("/prioritize")
async def prioritize_request(input_data: PrioritizationRequest):
    priorities = input_data.priorities
    prompt = (
        "You are a software consultant. Please analyze the following requirements:\n"
        "- For each, provide:\n  - Complexity: Low, Medium, or High\n  - Business Value: Low, Medium, or High\n"
        "Requirements:\n"
    )
    for priority in priorities:
        prompt += f"- {priority.requirement} (Importance: {priority.importance}/10)\n"
    prompt += "Provide your analysis of each requirement."

    try:
        logger.info(f"Prompt to model: {prompt}")
        inputs = tokenizer(prompt, return_tensors="pt", padding=True)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        outputs = model.generate(
            inputs["input_ids"], 
            attention_mask=inputs["attention_mask"],
            max_new_tokens=100,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        logger.info("Model generation completed.")
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        logger.info(f"Response: {generated_text}")
        return {"response": generated_text}

    except Exception as e:
        logger.error(f"Error in prioritize_request: {str(e)}")
        return {"response": "An error occurred while processing your request. Please try again later."}

@app.post("/followup")
async def handle_followup(input_data: FollowUpInput):
    conversation_history = "\n".join(input_data.history)
    followup_prompt = (
        f"You are a helpful assistant. Here's a follow-up question: '{input_data.follow_up}'.\n"
        f"Conversation history:\n{conversation_history}\nPlease provide insights."
    )

    try:
        logger.info(f"Follow-up prompt to model: {followup_prompt}")
        inputs = tokenizer(followup_prompt, return_tensors="pt", padding=True)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        outputs = model.generate(
            inputs["input_ids"], 
            attention_mask=inputs["attention_mask"],
            max_new_tokens=150,
            temperature=0.7, 
            top_p=0.9,
            do_sample=True
        )
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        logger.info(f"Response: {generated_text}")
        input_data.history.append(f"AI: {generated_text}")
        return {"response": generated_text, "history": input_data.history}

    except Exception as e:
        logger.error(f"Error in handle_followup: {str(e)}")
        return {"response": "An error occurred while processing your follow-up. Please try again later."}
