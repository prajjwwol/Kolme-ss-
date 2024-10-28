# models/llama_model.py
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODEL_ID = "facebook/bart-large-mnli"

def load_llama_model():
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    return model, tokenizer

def analyze_with_llama(requirement, model, tokenizer):
    inputs = tokenizer(requirement, return_tensors="pt")
    outputs = model(**inputs)
    return outputs.logits
