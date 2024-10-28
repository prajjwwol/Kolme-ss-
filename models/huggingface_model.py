# models/huggingface_model.py
import os
from transformers import pipeline
from config import Config

os.environ['HUGGINGFACE_API_KEY'] = Config.HUGGINGFACE_API_KEY

def load_huggingface_model():
    return pipeline("text-classification", model="facebook/bart-large-mnli")
