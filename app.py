# app.py
from flask import Flask, render_template, request, jsonify
from utils.prioritization import prioritize_requirements
from models.llama_model import load_llama_model, analyze_with_llama

app = Flask(__name__)

# Load the Llama model
llama_model, llama_tokenizer = load_llama_model()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/prioritize', methods=['POST'])
def prioritize():
    data = request.json
    requirements = data['requirements']
    responses = data.get('responses', {})

    # Prioritize requirements with user-provided responses and clarifications
    prioritized, information_requests, prioritized_explanations = prioritize_requirements(requirements, responses)

    return jsonify({
        "prioritized": prioritized,
        "information_requests": information_requests,
        "prioritized_explanations": prioritized_explanations
    })

if __name__ == '__main__':
    app.run(debug=True)
