from fastapi import FastAPI, Request
import openai
import os
from pydantic import BaseModel

# Initialize FastAPI
app = FastAPI()

# Set your OpenAI API key here (ensure you have an API key)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define a data model for input
class Query(BaseModel):
    prompt: str

# Simple health check route
@app.get("/")
def read_root():
    return {"message": "Welcome to the GPT-based Web App!"}

from fastapi.staticfiles import StaticFiles

# Serve the static HTML page
app.mount("/static", StaticFiles(directory="static"), name="static")

# Endpoint to interact with the GPT model
@app.post("/ask")
async def ask_gpt(query: Query):
    # Call OpenAI API (or other pre-trained APIs) to get the response
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=query.prompt,
        max_tokens=100
    )
    
    # Send back the generated response
    return {"response": response.choices[0].text.strip()}
