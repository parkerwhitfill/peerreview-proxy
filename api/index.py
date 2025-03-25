from flask import Flask, request, jsonify
import os
import json
import requests
from flask_cors import CORS

# Create Flask app
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Get API keys from environment variables
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# API endpoints
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# Define routes
@app.route('/', methods=['GET'])
def home():
    """Simple home page with status info"""
    return jsonify({
        "service": "AI API Proxy",
        "status": "active",
        "endpoints": [
            "/health",
            "/proxy/claude",
            "/proxy/openai",
            "/proxy/gemini"
        ]
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "available_models": {
            "claude": CLAUDE_API_KEY is not None,
            "openai": OPENAI_API_KEY is not None,
            "gemini": GEMINI_API_KEY is not None
        }
    })

@app.route('/proxy/claude', methods=['POST'])
def proxy_claude():
    """
    Proxy requests to Claude API
    
    Expected JSON payload:
    {
        "model": "claude-3-7-sonnet-20250219",
        "system": "System prompt text",
        "messages": [
            {"role": "user", "content": "User message"},
            {"role": "assistant", "content": "Assistant response"}
        ],
        "max_tokens": 1024,
        "temperature": 0.7
    }
    """
    try:
        # Check API key
        if not CLAUDE_API_KEY:
            return jsonify({"error": "Claude API key not configured on server"}), 500
        
        # Get request data
        data = request.get_json()
        
        # Forward to Claude API
        headers = {
            "Content-Type": "application/json",
            "x-api-key": CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01",
            "Authorization": f"Bearer {CLAUDE_API_KEY}"
        }
        
        # Make request to Claude API
        response = requests.post(
            CLAUDE_API_URL,
            headers=headers,
            json=data,
            timeout=60
        )
        
        # Return the response
        return response.json(), response.status_code
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/proxy/openai', methods=['POST'])
def proxy_openai():
    """
    Proxy requests to OpenAI API
    
    Expected JSON payload:
    {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "System prompt text"},
            {"role": "user", "content": "User message"}
        ],
        "temperature": 0.7
    }
    """
    try:
        # Check API key
        if not OPENAI_API_KEY:
            return jsonify({"error": "OpenAI API key not configured on server"}), 500
        
        # Get request data
        data = request.get_json()
        
        # Forward to OpenAI API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        # Make request to OpenAI API
        response = requests.post(
            OPENAI_API_URL,
            headers=headers,
            json=data,
            timeout=60
        )
        
        # Return the response
        return response.json(), response.status_code
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/proxy/gemini', methods=['POST'])
def proxy_gemini():
    """
    Proxy requests to Gemini API
    
    Expected JSON payload:
    {
        "model": "gemini-pro",
        "content": "User prompt text",
        "temperature": 0.7
    }
    """
    try:
        # Check API key
        if not GEMINI_API_KEY:
            return jsonify({"error": "Gemini API key not configured on server"}), 500
        
        # Get request data
        data = request.get_json()
        
        # Currently, we don't support Gemini API directly in this simplified version
        # to avoid additional dependencies, but we acknowledge the request
        return jsonify({
            "text": "Gemini API proxy is configured but requires additional setup",
            "model": data.get('model', 'gemini-pro')
        })
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500