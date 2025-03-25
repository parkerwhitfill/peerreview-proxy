from http.server import BaseHTTPRequestHandler
import json
import os
import requests

# Get API keys from environment variables
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# API endpoints
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

class handler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type="application/json"):
        self.send_response(status_code)
        self.send_header("Content-type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()
        self.wfile.write("".encode())

    def do_GET(self):
        if self.path == "/health":
            self._set_headers()
            response = {
                "status": "healthy",
                "available_models": {
                    "claude": CLAUDE_API_KEY is not None,
                    "openai": OPENAI_API_KEY is not None,
                    "gemini": GEMINI_API_KEY is not None
                }
            }
            self.wfile.write(json.dumps(response).encode())
        elif self.path == "/":
            self._set_headers()
            response = {
                "service": "AI API Proxy",
                "status": "active",
                "endpoints": [
                    "/health",
                    "/proxy/claude",
                    "/proxy/openai",
                    "/proxy/gemini"
                ]
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length:
            request_body = self.rfile.read(content_length)
            try:
                data = json.loads(request_body)
            except json.JSONDecodeError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
                return
        else:
            data = {}

        try:
            if self.path == "/proxy/claude":
                if not CLAUDE_API_KEY:
                    self._set_headers(500)
                    self.wfile.write(json.dumps({"error": "Claude API key not configured"}).encode())
                    return

                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": CLAUDE_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "Authorization": f"Bearer {CLAUDE_API_KEY}"
                }

                response = requests.post(
                    CLAUDE_API_URL,
                    headers=headers,
                    json=data,
                    timeout=60
                )

                self._set_headers(response.status_code)
                self.wfile.write(response.content)
                
            elif self.path == "/proxy/openai":
                if not OPENAI_API_KEY:
                    self._set_headers(500)
                    self.wfile.write(json.dumps({"error": "OpenAI API key not configured"}).encode())
                    return

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {OPENAI_API_KEY}"
                }

                response = requests.post(
                    OPENAI_API_URL,
                    headers=headers,
                    json=data,
                    timeout=60
                )

                self._set_headers(response.status_code)
                self.wfile.write(response.content)
                
            elif self.path == "/proxy/gemini":
                self._set_headers(200)
                self.wfile.write(json.dumps({
                    "text": "Gemini API proxy is available but requires additional setup",
                    "model": data.get("model", "gemini-pro")
                }).encode())
                
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())
                
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": f"Server error: {str(e)}"}).encode())