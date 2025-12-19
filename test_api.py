"""Simple test script for the API server."""

import requests
import json

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("Testing /health endpoint...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_formats():
    """Test formats endpoint."""
    print("Testing /formats endpoint...")
    response = requests.get(f"{API_URL}/formats")
    print(f"Status: {response.status_code}")
    print(f"Formats: {response.json()}")
    print()

def test_convert():
    """Test convert endpoint."""
    print("Testing /convert endpoint...")
    test_markdown = "# Hello World\n\nThis is a **test**."
    
    response = requests.post(
        f"{API_URL}/convert",
        json={
            "content": test_markdown,
            "output_format": "html",
            "options": {"standalone": True},
        },
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content Length: {len(response.content)} bytes")
        print("Conversion successful!")
    else:
        print(f"Error: {response.text}")
    print()

if __name__ == "__main__":
    print("=" * 50)
    print("mdconv API Server Test")
    print("=" * 50)
    print()
    print("Make sure the API server is running: python api_server.py")
    print()
    
    try:
        test_health()
        test_formats()
        test_convert()
        print("All tests completed!")
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API server.")
        print("Make sure the server is running: python api_server.py")
    except Exception as e:
        print(f"ERROR: {e}")


