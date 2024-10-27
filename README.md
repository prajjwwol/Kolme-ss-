# Kolme Ässää
AI agents made to analyze and prioritize requirements.

## Project Overview
Kolme Ässää is an AI-driven tool designed to assist software consultants in analyzing and prioritizing requirements based on their importance and complexity. Powered by FastAPI and Hugging Face's DialoGPT, this application supports structured requirement submissions, analyses, and follow-up interactions to provide actionable insights for project prioritization.

## Setup and Installation

### Prerequisites
- Python 3.8+
- [Hugging Face API Token](https://huggingface.co/docs/hub/security-tokens) with access to DialoGPT

### Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/KolmeAssaa.git
    cd KolmeAssaa
    ```

2. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up environment variables:
   Ensure your Hugging Face API token is available by setting it as an environment variable:
   ```bash
   export HUGGING=<your_huggingface_api_token>
   
4. Start the application
uvicorn app:app --reload --host 0.0.0.0 --port 8000


Notes:
Create Pythin Virtual Env
 - C:\Python311\python.exe -m venv env
Activate the Virtual Env
 - env\Scripts\activate
Install requirements
 -pip install -r requirements.txt

 Deletes Cache from Virtual Env
 -rmdir /S /Q %USERPROFILE%\.cache\huggingface

 Run APP:
 uvicorn app:app --reload --host 0.0.0.0 --port 8000


