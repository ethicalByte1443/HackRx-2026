#!/bin/bash

# Install spaCy model if not present
python -m spacy download en_core_web_sm || echo "SpaCy model installation failed, continuing with fallback"

# Start the server
uvicorn main:app --host 0.0.0.0 --port $PORT
