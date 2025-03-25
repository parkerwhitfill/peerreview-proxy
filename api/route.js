// Edge function for Vercel
export const config = {
  runtime: 'edge'
};

export default async function handler(request) {
  // Get the path from the request URL
  const url = new URL(request.url);
  const path = url.pathname;

  // Set up CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Content-Type': 'application/json'
  };

  // Handle OPTIONS requests (CORS preflight)
  if (request.method === 'OPTIONS') {
    return new Response(null, { headers, status: 200 });
  }

  // Environment variables for API keys
  const CLAUDE_API_KEY = process.env.CLAUDE_API_KEY;
  const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
  const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

  // Health check endpoint
  if (path === '/health' && request.method === 'GET') {
    const healthData = {
      status: 'healthy',
      available_models: {
        claude: !!CLAUDE_API_KEY,
        openai: !!OPENAI_API_KEY,
        gemini: !!GEMINI_API_KEY
      }
    };
    return new Response(JSON.stringify(healthData), { headers, status: 200 });
  }

  // Home endpoint
  if ((path === '/' || path === '') && request.method === 'GET') {
    const homeData = {
      service: 'AI API Proxy',
      status: 'active',
      endpoints: [
        '/health',
        '/proxy/claude',
        '/proxy/openai',
        '/proxy/gemini'
      ]
    };
    return new Response(JSON.stringify(homeData), { headers, status: 200 });
  }

  // Claude API Proxy
  if (path === '/proxy/claude' && request.method === 'POST') {
    if (!CLAUDE_API_KEY) {
      return new Response(
        JSON.stringify({ error: 'Claude API key not configured on server' }), 
        { headers, status: 500 }
      );
    }

    try {
      // Get request data
      const data = await request.json();

      // Create Claude API request
      const claudeResponse = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': CLAUDE_API_KEY,
          'anthropic-version': '2023-06-01',
          'Authorization': `Bearer ${CLAUDE_API_KEY}`
        },
        body: JSON.stringify(data)
      });

      // Return Claude's response
      const responseData = await claudeResponse.json();
      return new Response(JSON.stringify(responseData), { 
        headers, 
        status: claudeResponse.status 
      });
    } catch (error) {
      return new Response(
        JSON.stringify({ error: `Server error: ${error.message}` }), 
        { headers, status: 500 }
      );
    }
  }

  // OpenAI API Proxy
  if (path === '/proxy/openai' && request.method === 'POST') {
    if (!OPENAI_API_KEY) {
      return new Response(
        JSON.stringify({ error: 'OpenAI API key not configured on server' }), 
        { headers, status: 500 }
      );
    }

    try {
      // Get request data
      const data = await request.json();

      // Create OpenAI API request
      const openaiResponse = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${OPENAI_API_KEY}`
        },
        body: JSON.stringify(data)
      });

      // Return OpenAI's response
      const responseData = await openaiResponse.json();
      return new Response(JSON.stringify(responseData), { 
        headers, 
        status: openaiResponse.status 
      });
    } catch (error) {
      return new Response(
        JSON.stringify({ error: `Server error: ${error.message}` }), 
        { headers, status: 500 }
      );
    }
  }

  // Gemini API Proxy (simplified)
  if (path === '/proxy/gemini' && request.method === 'POST') {
    return new Response(
      JSON.stringify({
        text: "Gemini API proxy is available but requires additional setup",
        model: "gemini-pro"
      }), 
      { headers, status: 200 }
    );
  }

  // Default response for unmatched routes
  return new Response(
    JSON.stringify({ error: 'Endpoint not found' }), 
    { headers, status: 404 }
  );
}