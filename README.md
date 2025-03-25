# AI API Proxy

A simple proxy server for securely handling AI API calls without exposing API keys in client-side code.

## Features

- Secure proxying for Claude, OpenAI, and Gemini API calls
- Simple REST endpoints for each API provider
- CORS support for browser access
- Easy deployment to Vercel

## API Endpoints

- `/health` - Check server health and available APIs
- `/proxy/claude` - Proxy requests to Claude API
- `/proxy/openai` - Proxy requests to OpenAI API  
- `/proxy/gemini` - Proxy requests to Gemini API

## Deployment

This proxy is designed to be deployed to Vercel's serverless platform.

### Requirements

- Vercel account (free tier is fine)
- API keys for the services you want to use

### Environment Variables

Required environment variables (set in Vercel dashboard):

- `CLAUDE_API_KEY` or `ANTHROPIC_API_KEY` - Your Claude API key
- `OPENAI_API_KEY` - Your OpenAI API key (optional)
- `GEMINI_API_KEY` - Your Gemini API key (optional)

## Example Usage

### Claude API

```javascript
// Call Claude through the proxy
fetch("https://your-proxy.vercel.app/proxy/claude", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    model: "claude-3-7-sonnet-20250219",
    system: "You are a helpful assistant.",
    messages: [
      { role: "user", content: "Hello, world!" }
    ],
    max_tokens: 1024
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

### OpenAI API

```javascript
// Call OpenAI through the proxy
fetch("https://your-proxy.vercel.app/proxy/openai", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    model: "gpt-4",
    messages: [
      { role: "system", content: "You are a helpful assistant." },
      { role: "user", content: "Hello, world!" }
    ]
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Security

This proxy keeps API keys secure by:

1. Storing them as environment variables on the server
2. Never exposing them to client-side code
3. Using HTTPS for all communications

## Local Development

To run locally:

```bash
pip install -r requirements.txt
python index.py
```

The server will be available at http://localhost:3340