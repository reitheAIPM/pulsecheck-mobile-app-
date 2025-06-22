export default async function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, PATCH');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With');
  
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
    
    console.log(`Proxying ${req.method} request to: ${url}`);
    
    // Prepare headers - forward important ones but avoid conflicts
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'User-Agent': 'PulseCheck-Web-Proxy/1.0'
    };
    
    // Add Authorization header if present
    if (req.headers.authorization) {
      headers.Authorization = req.headers.authorization;
    }
    
    // Parse request body for non-GET requests
    let bodyData;
    if (req.method !== 'GET' && req.body) {
      bodyData = typeof req.body === 'string' ? req.body : JSON.stringify(req.body);
    }
    
    // Forward the request to Railway backend
    const response = await fetch(url, {
      method: req.method,
      headers: headers,
      body: bodyData
    });
    
    // Get response data
    const contentType = response.headers.get('content-type') || '';
    let data;
    
    if (contentType.includes('application/json')) {
      data = await response.json();
      res.status(response.status).json(data);
    } else {
      data = await response.text();
      res.status(response.status).send(data);
    }
    
    console.log(`Proxy response: ${response.status} ${response.statusText}`);
    
  } catch (error) {
    console.error('Proxy error:', error);
    res.status(500).json({ 
      error: 'Proxy request failed', 
      message: error.message,
      timestamp: new Date().toISOString()
    });
  }
} 