import requests

try:
    r = requests.get('https://pulsecheck-mobile-app-production.up.railway.app/openapi.json')
    endpoints = list(r.json()['paths'].keys())
    admin_endpoints = [ep for ep in endpoints if 'admin' in ep]
    
    print(f"Total endpoints: {len(endpoints)}")
    print(f"Admin endpoints found: {len(admin_endpoints)}")
    
    if admin_endpoints:
        print("Admin endpoints:")
        for ep in admin_endpoints:
            print(f"  {ep}")
    else:
        print("❌ No admin endpoints found - beta optimization features not loaded")
    
    print("\nAll endpoints:")
    for ep in sorted(endpoints):
        print(f"  {ep}")
        
except Exception as e:
    print(f"Error: {e}") 