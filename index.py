#!/usr/bin/env python

"""
API Proxy Server - Simple proxy to handle AI API calls with secure API keys.
This is a minimal server that only forwards requests to AI providers with proper authentication.
"""

import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api_proxy")

# Load environment variables
load_dotenv()

# Get API keys
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# API endpoints
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# Check if API keys are available
if CLAUDE_API_KEY:
    logger.info(f"Claude API key found with length: {len(CLAUDE_API_KEY)}, starts with: {CLAUDE_API_KEY[:5]}...")
else:
    logger.warning("No Claude API key found in environment variables")

if OPENAI_API_KEY:
    logger.info(f"OpenAI API key found with length: {len(OPENAI_API_KEY)}, starts with: {OPENAI_API_KEY[:5]}...")
else:
    logger.warning("No OpenAI API key found in environment variables")

if GEMINI_API_KEY:
    logger.info(f"Gemini API key found with length: {len(GEMINI_API_KEY)}, starts with: {GEMINI_API_KEY[:5]}...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        GEMINI_AVAILABLE = True
    except ImportError:
        logger.warning("Google Generative AI package not installed. Run: pip install google-generativeai")
        GEMINI_AVAILABLE = False
else:
    GEMINI_AVAILABLE = False
    logger.warning("No Gemini API key found in environment variables")

# Create Flask app
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

@app.route('/')
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
            "gemini": GEMINI_AVAILABLE
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
        data = request.json
        logger.info(f"Claude proxy request for model: {data.get('model', 'unspecified')}")
        
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
        logger.error(f"Error in Claude proxy: {str(e)}")
        import traceback
        traceback.print_exc()
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
        data = request.json
        logger.info(f"OpenAI proxy request for model: {data.get('model', 'unspecified')}")
        
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
        logger.error(f"Error in OpenAI proxy: {str(e)}")
        import traceback
        traceback.print_exc()
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
        # Check if Gemini is available
        if not GEMINI_AVAILABLE:
            return jsonify({"error": "Gemini API not configured on server"}), 500
        
        # Get request data
        data = request.json
        logger.info(f"Gemini proxy request for model: {data.get('model', 'gemini-pro')}")
        
        # Process with Gemini API
        model = genai.GenerativeModel(model_name=data.get('model', 'gemini-pro'))
        response = model.generate_content(data.get('content', ''))
        
        # Return response in standardized format
        return jsonify({
            "text": response.text,
            "model": data.get('model', 'gemini-pro')
        })
    
    except Exception as e:
        logger.error(f"Error in Gemini proxy: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# For Vercel serverless deployment
def handler(request, context):
    with app.request_context(request):
        return app(request)
        
# Flask development server (not used in Vercel)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3340, debug=True)