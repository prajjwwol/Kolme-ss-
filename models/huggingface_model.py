from transformers import pipeline


MODEL_ID = "google/flan-t5-large"

# Initialize the pipeline
pipe = pipeline("text2text-generation", model=MODEL_ID)

def analyze_with_model(requirement):
    prompt = (
        f"Prioritize the requirement: '{requirement}' based on importance, complexity, and urgency. "
        "Provide a detailed prioritization analysis."
    )

    # Generate the response
    try:
        response = pipe(prompt, max_length=200)
        result = response[0]["generated_text"] if "generated_text" in response[0] else "No text generated"
    except Exception as e:
        result = f"Error in calling model: {e}"

    return result
