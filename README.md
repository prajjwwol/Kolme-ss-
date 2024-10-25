# Kolme Ässää
AI agents made to analyze requirements

To initialise:

- pip install fastapi uvicorn huggingface-hub transformers torch
- uvicorn app:app --reload --host 0.0.0.0 --port 8000
- http://localhost:8000/static/index.html

@startuml
actor User

rectangle Frontend {
    entity "HTML/JavaScript\nInterface" as UI
    UI --> Backend : "Submit Requirement\nor Follow-up"
    Backend --> UI : "Display Response"
}

rectangle Backend {
    control "FastAPI Server" as API
    API --> LLM : "Process Requirement\nRequest"
    API --> History : "Store Conversation\nHistory"
}

rectangle Language_Model {
    entity "DialoGPT Model\n(Hugging Face API)" as LLM
    API --> LLM : "Generate\nResponse"
    LLM --> API : "Send Generated\nResponse"
}

rectangle "Conversation History" {
    entity "Stored chat history\nused for context" as History
    API <--> History : "Maintain history\nfor conversational context"
}

User --> UI : "Enter Requirements\nor Follow-up"
UI --> API : "Request (JSON)"
API --> UI : "Response (JSON)"

@enduml

