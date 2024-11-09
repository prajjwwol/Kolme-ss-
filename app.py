# app.py
from flask import Flask, request, jsonify, render_template
from models.huggingface_model import analyze_with_model
from utils.prioritization import prioritize_requirements

app = Flask(__name__)

# Serve the main HTML interface
@app.route('/')
def home():
    return render_template('index.html')

# Handle prioritization requests
@app.route('/prioritize', methods=['POST'])
def prioritize():
    data = request.json
    requirements = data.get("requirements", [])
    responses = data.get("responses", {})

    # Process each requirement
    prioritized, information_requests, prioritized_explanations = prioritize_requirements(requirements, responses)
    
    return jsonify({
        "prioritized": prioritized,
        "informationRequests": information_requests,
        "explanations": prioritized_explanations
    })

if __name__ == "__main__":
    app.run(debug=True)
