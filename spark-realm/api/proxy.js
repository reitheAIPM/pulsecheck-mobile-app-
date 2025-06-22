export default async function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', '*');
  
  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }
  
  try {
    // Get the path from the URL (everything after /api/proxy/)
    const path = req.url.replace('/api/proxy', '') || '/';
    const backendUrl = 'https://pulsecheck-mobile-app-production.up.railway.app';
    
    // Construct the full URL
    const url = `${backendUrl}${path}`;
    
    console.log('Proxying request:', req.method, url);
    
    // Forward the request to Railway backend
    const response = await fetch(url, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        // Don't forward all headers to avoid conflicts
        'Accept': 'application/json'
      },
      body: req.method !== 'GET' && req.body ? JSON.stringify(req.body) : undefined
    });
    
    const data = await response.text();
    
    // Forward the response
    res.status(response.status);
    
    // Try to parse as JSON, fallback to text
    try {
      res.json(JSON.parse(data));
    } catch {
      res.send(data);
    }
    
  } catch (error) {
    console.error('Proxy error:', error);
    res.status(500).json({ error: 'Proxy failed', message: error.message });
  }
} 