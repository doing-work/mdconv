#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for mdconv API with file upload support.

Tests the synchronous file upload endpoint that returns converted files directly.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# Fix Windows console encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import requests
except ImportError:
    print("Error: 'requests' library is required. Install it with: pip install requests")
    sys.exit(1)

# API Configuration - UPDATE THIS WITH YOUR API URL
API_BASE_URL = "https://kgwlr9qp1m.execute-api.eu-west-2.amazonaws.com"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_success(message: str):
    """Print success message."""
    print(f"{Colors.GREEN}[OK]{Colors.RESET} {message}")


def print_error(message: str):
    """Print error message."""
    print(f"{Colors.RED}[FAIL]{Colors.RESET} {message}")


def print_info(message: str):
    """Print info message."""
    print(f"{Colors.CYAN}[INFO]{Colors.RESET} {message}")


def print_warning(message: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}[WARN]{Colors.RESET} {message}")


def print_header(message: str):
    """Print header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")


def test_health(api_url: str) -> bool:
    """Test the health endpoint."""
    print_header("Testing Health Endpoint")
    
    try:
        response = requests.get(f"{api_url}/health", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print_success(f"Health check passed: {data.get('status', 'unknown')}")
        print(f"  Service: {data.get('service', 'unknown')}")
        print(f"  Orchestrator: {data.get('orchestrator', 'unknown')}")
        return True
    except requests.exceptions.RequestException as e:
        print_error(f"Health check failed: {e}")
        return False


def test_formats(api_url: str) -> bool:
    """Test the formats endpoint."""
    print_header("Testing Formats Endpoint")
    
    try:
        response = requests.get(f"{api_url}/formats", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        formats = data.get('formats', [])
        print_success(f"Formats endpoint working. Found {len(formats)} formats:")
        for fmt in formats:
            print(f"  - {fmt}")
        return True
    except requests.exceptions.RequestException as e:
        print_error(f"Formats check failed: {e}")
        return False


def test_file_upload(api_url: str, file_path: Path, output_format: str, output_file: Optional[str] = None, max_wait: int = 120) -> bool:
    """Test file upload and conversion (async with polling)."""
    print_header(f"Testing File Upload Conversion ({output_format})")
    
    if not file_path.exists():
        print_error(f"File not found: {file_path}")
        return False
    
    file_size = file_path.stat().st_size
    print_info(f"Uploading file: {file_path.name} ({file_size:,} bytes)")
    print_info(f"Target format: {output_format}")
    
    try:
        # Read the markdown file
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # Prepare multipart form data
        files = {
            'file': (file_path.name, file_content, 'text/markdown')
        }
        data = {
            'output_format': output_format
        }
        
        print_info("Sending conversion request...")
        
        # Send request with file upload (async - returns job_id)
        response = requests.post(
            f"{api_url}/convert",
            files=files,
            data=data,
            timeout=30
        )
        
        # Handle response codes
        if response.status_code == 202:
            # Async conversion started - get job_id and task endpoint
            data = response.json()
            job_id = data.get('job_id')
            task_endpoint = data.get('task_endpoint')
            status_url = data.get('status_url')
            result_url = data.get('result_url')
            
            if not job_id or not task_endpoint:
                print_error("Missing job_id or task_endpoint in response")
                return False
            
            print_success(f"Conversion started (job_id: {job_id})")
            print_info(f"Task endpoint: {task_endpoint}")
            print_info("Polling FastAPI task for status...")
            
            # Poll FastAPI task directly for status
            import time
            start_time = time.time()
            poll_interval = 2  # Poll every 2 seconds
            
            while (time.time() - start_time) < max_wait:
                try:
                    status_response = requests.get(status_url, timeout=10)
                    if status_response.status_code == 404:
                        print_error("Job not found")
                        return False
                    
                    status_data = status_response.json()
                    status = status_data.get('status')
                    
                    if status == 'completed':
                        print_success("Conversion completed!")
                        break
                    elif status == 'failed':
                        error_msg = status_data.get('error', 'Unknown error')
                        print_error(f"Conversion failed: {error_msg}")
                        return False
                    elif status in ['pending', 'processing']:
                        elapsed = int(time.time() - start_time)
                        print_info(f"Status: {status} (elapsed: {elapsed}s)")
                        time.sleep(poll_interval)
                    else:
                        print_warning(f"Unknown status: {status}")
                        time.sleep(poll_interval)
                except requests.exceptions.RequestException as e:
                    print_warning(f"Error polling status: {e}")
                    time.sleep(poll_interval)
            else:
                print_error(f"Conversion timed out after {max_wait}s")
                return False
            
            # Get result from FastAPI task
            print_info("Retrieving result from FastAPI task...")
            try:
                result_response = requests.get(result_url, timeout=30)
                
                if result_response.status_code == 200:
                    # Success - save the converted file
                    if output_file is None:
                        output_file = f"output_{file_path.stem}.{output_format}"
                    
                    with open(output_file, 'wb') as f:
                        f.write(result_response.content)
                    
                    file_size = Path(output_file).stat().st_size
                    print_success(f"Conversion successful!")
                    print(f"  Output file: {output_file}")
                    print(f"  File size: {file_size:,} bytes")
                    print(f"  Content-Type: {result_response.headers.get('Content-Type', 'unknown')}")
                    
                    return True
                elif result_response.status_code == 202:
                    print_error("Result not ready yet")
                    return False
                else:
                    print_error(f"Failed to get result: {result_response.status_code}")
                    try:
                        error_data = result_response.json()
                        error_msg = error_data.get('detail', error_data.get('error', 'Unknown error'))
                        print(f"  Error: {error_msg}")
                    except:
                        print(f"  Response: {result_response.text[:200]}")
                    return False
            except requests.exceptions.RequestException as e:
                print_error(f"Failed to retrieve result: {e}")
                return False
        
        elif response.status_code == 503:
            print_error("Service unavailable (503)")
            print_info("The service might be busy or initializing. Try again in a few seconds.")
            return False
        
        elif response.status_code == 400:
            print_error(f"Bad request (400)")
            try:
                error_data = response.json()
                error_msg = error_data.get('error') or error_data.get('detail', 'Unknown error')
                print(f"  Error: {error_msg}")
            except:
                print(f"  Response: {response.text[:200]}")
            return False
        
        else:
            print_error(f"Conversion failed with status {response.status_code}")
            try:
                error_data = response.json()
                error_msg = error_data.get('error') or error_data.get('detail', 'Unknown error')
                print(f"  Error: {error_msg}")
            except:
                print(f"  Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Request timed out. The conversion might be taking too long.")
        return False
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    parser = argparse.ArgumentParser(
        description="Test mdconv API with file upload",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test with default sample file
  python test_file_upload.py --format html
  
  # Test with custom file
  python test_file_upload.py --file mydoc.md --format pdf
  
  # Test all formats
  python test_file_upload.py --file test_sample.md --all-formats
        """
    )
    parser.add_argument(
        "--file",
        type=str,
        default="test_sample.md",
        help="Path to markdown file to convert (default: test_sample.md)"
    )
    parser.add_argument(
        "--format",
        choices=["html", "pdf", "docx", "pptx", "epub", "latex"],
        default="html",
        help="Output format (default: html)"
    )
    parser.add_argument(
        "--all-formats",
        action="store_true",
        help="Test all supported formats"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output filename (default: output_<input_name>.<format>)"
    )
    parser.add_argument(
        "--skip-health",
        action="store_true",
        help="Skip health check"
    )
    parser.add_argument(
        "--skip-formats",
        action="store_true",
        help="Skip formats endpoint test"
    )
    parser.add_argument(
        "--api-url",
        type=str,
        default=None,
        help=f"API base URL (default: {API_BASE_URL})"
    )
    
    args = parser.parse_args()
    
    # Update API URL if provided
    api_url = args.api_url if args.api_url else API_BASE_URL
    
    print_header("mdconv API File Upload Test")
    print(f"API URL: {api_url}")
    print(f"Input file: {args.file}\n")
    
    results = {
        "health": False,
        "formats": False,
        "conversions": []
    }
    
    # Test health endpoint
    if not args.skip_health:
        results["health"] = test_health(api_url)
    
    # Test formats endpoint
    if not args.skip_formats:
        results["formats"] = test_formats(api_url)
    
    # Test file upload
    file_path = Path(args.file)
    
    if args.all_formats:
        formats_to_test = ["html", "pdf", "docx", "pptx", "epub", "latex"]
    else:
        formats_to_test = [args.format]
    
    for fmt in formats_to_test:
        output_file = args.output
        if output_file is None and len(formats_to_test) == 1:
            output_file = f"output_{file_path.stem}.{fmt}"
        elif output_file is None:
            output_file = f"output_{file_path.stem}_{fmt}.{fmt}"
        
        success = test_file_upload(api_url, file_path, fmt, output_file)
        results["conversions"].append({
            "format": fmt,
            "success": success,
            "output_file": output_file if success else None
        })
        
        # Small delay between requests
        if len(formats_to_test) > 1:
            import time
            time.sleep(2)
    
    # Summary
    print_header("Test Summary")
    
    if not args.skip_health:
        status = "✓ PASS" if results["health"] else "✗ FAIL"
        print(f"Health Check: {status}")
    
    if not args.skip_formats:
        status = "✓ PASS" if results["formats"] else "✗ FAIL"
        print(f"Formats Endpoint: {status}")
    
    print(f"\nConversions:")
    for conv in results["conversions"]:
        status = "✓ PASS" if conv["success"] else "✗ FAIL"
        print(f"  {status} {conv['format']}: ", end="")
        if conv["success"]:
            print(f"{conv['output_file']}")
        else:
            print("Failed")
    
    # Overall status
    all_passed = (
        (args.skip_health or results["health"]) and
        (args.skip_formats or results["formats"]) and
        all(conv["success"] for conv in results["conversions"])
    )
    
    if all_passed:
        print_success("\nAll tests passed!")
        sys.exit(0)
    else:
        print_error("\nSome tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
