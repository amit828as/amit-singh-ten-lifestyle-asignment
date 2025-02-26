from fastapi import Header, HTTPException, status
from typing import Optional
import os



API_KEY = os.getenv("API_KEY")  # Load the API key from environment

def api_key_auth(x_api_key: Optional[str] = Header(None)):
    """
    Simple auth function that expects an 'x-api-key' header.
    If not present or doesn't match the known key, raises 401.
    """
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )
    return x_api_key
