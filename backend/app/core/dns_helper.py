"""
DNS Helper for Railway deployment
Helps resolve DNS issues when connecting to external services
"""

import socket
import os
import logging

logger = logging.getLogger(__name__)

def configure_dns():
    """
    Configure DNS resolution for Railway environment
    """
    try:
        # Test if we can resolve Supabase
        supabase_url = os.getenv("SUPABASE_URL", "")
        if supabase_url:
            # Extract hostname from URL
            hostname = supabase_url.replace("https://", "").replace("http://", "").split("/")[0]
            logger.info(f"Testing DNS resolution for: {hostname}")
            
            try:
                # Try to resolve the hostname
                ip = socket.gethostbyname(hostname)
                logger.info(f"✅ DNS resolution successful: {hostname} -> {ip}")
                return True
            except socket.gaierror as e:
                logger.error(f"❌ DNS resolution failed for {hostname}: {e}")
                
                # Try alternative DNS resolution methods
                logger.info("Attempting alternative DNS resolution...")
                
                # Try using Google's DNS directly
                import subprocess
                try:
                    result = subprocess.run(
                        ["nslookup", hostname, "8.8.8.8"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        logger.info(f"✅ Alternative DNS resolution successful via Google DNS")
                        logger.info(f"DNS Output: {result.stdout}")
                    else:
                        logger.error(f"❌ Alternative DNS also failed: {result.stderr}")
                except Exception as dns_error:
                    logger.error(f"❌ Alternative DNS error: {dns_error}")
                
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"DNS configuration error: {e}")
        return False

# Run DNS configuration on module import
configure_dns() 