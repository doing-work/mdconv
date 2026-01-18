#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for containerized mdconv FastAPI with different conversions.

Tests all supported output formats (html, pdf, docx, pptx, epub, latex)
against the containerized API.
"""

import sys
import argparse
import time
from pathlib import Path
from typing import Optional, Dict, List

# Fix Windows console encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import requests
except ImportError:
    print("Error: 'requests' library is required. Install it with: uv pip install requests")
    sys.exit(1)

# Default API URL (can be overridden)
API_BASE_URL = "http://localhost:8000"

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


def test_health(api_url: str, api_key: Optional[str] = None) -> bool:
    """Test the health endpoint."""
    print_header("Testing Health Endpoint")
    
    try:
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key
            
        response = requests.get(f"{api_url}/health", headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print_success(f"Health check passed: {data.get('status', 'unknown')}")
        print(f"  Pandoc available: {data.get('pandoc_available', 'unknown')}")
        print(f"  Authenticated: {data.get('authenticated', 'unknown')}")
        return True
    except requests.exceptions.RequestException as e:
        print_error(f"Health check failed: {e}")
        return False


def test_formats(api_url: str, api_key: Optional[str] = None) -> bool:
    """Test the formats endpoint."""
    print_header("Testing Formats Endpoint")
    
    try:
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key
            
        response = requests.get(f"{api_url}/formats", headers=headers, timeout=10)
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


def test_conversion(
    api_url: str,
    markdown_content: str,
    output_format: str,
    output_file: Optional[str] = None,
    api_key: Optional[str] = None,
    use_json_endpoint: bool = False
) -> Dict:
    """Test conversion to a specific format."""
    print_header(f"Testing {output_format.upper()} Conversion")
    
    try:
        headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            headers["X-API-Key"] = api_key
        
        # Choose endpoint
        endpoint = "/convert/json" if use_json_endpoint else "/convert"
        
        # Prepare request data
        data = {
            "content": markdown_content,
            "output_format": output_format,
            "options": {}
        }
        
        print_info(f"Sending conversion request to {endpoint}...")
        print_info(f"Content length: {len(markdown_content)} characters")
        
        # Send request
        start_time = time.time()
        response = requests.post(
            f"{api_url}{endpoint}",
            json=data,
            headers=headers,
            timeout=120  # 2 minutes timeout for conversions
        )
        elapsed_time = time.time() - start_time
        
        # Check response
        if response.status_code == 200:
            # Save the converted file
            if output_file is None:
                output_file = f"output_test.{output_format}"
            
            # Create output directory if it doesn't exist
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            file_size = Path(output_file).stat().st_size
            content_type = response.headers.get('Content-Type', 'unknown')
            
            print_success(f"Conversion successful!")
            print(f"  Output file: {output_file}")
            print(f"  File size: {file_size:,} bytes")
            print(f"  Content-Type: {content_type}")
            print(f"  Conversion time: {elapsed_time:.2f}s")
            
            return {
                "success": True,
                "output_file": output_file,
                "file_size": file_size,
                "elapsed_time": elapsed_time
            }
        else:
            error_msg = "Unknown error"
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', error_data.get('error', 'Unknown error'))
            except:
                error_msg = response.text[:200]
            
            print_error(f"Conversion failed with status {response.status_code}")
            print(f"  Error: {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "status_code": response.status_code
            }
            
    except requests.exceptions.Timeout:
        print_error("Request timed out. The conversion might be taking too long.")
        return {"success": False, "error": "Timeout"}
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def test_all_formats(
    api_url: str,
    markdown_content: str,
    formats: List[str],
    api_key: Optional[str] = None,
    output_dir: str = "output"
) -> Dict:
    """Test all specified formats."""
    print_header("Testing All Formats")
    
    results = {}
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    for fmt in formats:
        output_file = f"{output_dir}/test_output.{fmt}"
        result = test_conversion(
            api_url=api_url,
            markdown_content=markdown_content,
            output_format=fmt,
            output_file=output_file,
            api_key=api_key
        )
        results[fmt] = result
        
        # Small delay between requests
        if fmt != formats[-1]:
            time.sleep(1)
    
    return results


def main():
    """Main test function."""
    parser = argparse.ArgumentParser(
        description="Test containerized mdconv FastAPI with different conversions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test all formats with default sample file
  python test_docker_conversions.py --all-formats
  
  # Test specific format
  python test_docker_conversions.py --format html
  
  # Test with custom markdown file
  python test_docker_conversions.py --file mydoc.md --format pdf
  
  # Test with API key
  python test_docker_conversions.py --api-key mykey --all-formats
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
        help="Output format to test (default: html, or all if --all-formats is used)"
    )
    parser.add_argument(
        "--all-formats",
        action="store_true",
        help="Test all supported formats"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Output directory for converted files (default: output)"
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
        default=API_BASE_URL,
        help=f"API base URL (default: {API_BASE_URL})"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="API key for authentication (optional)"
    )
    parser.add_argument(
        "--use-json-endpoint",
        action="store_true",
        help="Use /convert/json endpoint instead of /convert"
    )
    
    args = parser.parse_args()
    
    print_header("mdconv Docker API Conversion Test")
    print(f"API URL: {args.api_url}")
    print(f"Input file: {args.file}")
    if args.api_key:
        print(f"API Key: {'*' * len(args.api_key)}")
    print()
    
    # Read markdown file
    file_path = Path(args.file)
    if not file_path.exists():
        print_error(f"File not found: {file_path}")
        sys.exit(1)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    except Exception as e:
        print_error(f"Failed to read file: {e}")
        sys.exit(1)
    
    results = {
        "health": False,
        "formats": False,
        "conversions": {}
    }
    
    # Test health endpoint
    if not args.skip_health:
        results["health"] = test_health(args.api_url, args.api_key)
    
    # Test formats endpoint
    if not args.skip_formats:
        results["formats"] = test_formats(args.api_url, args.api_key)
    
    # Determine formats to test
    if args.all_formats:
        formats_to_test = ["html", "pdf", "docx", "pptx", "epub", "latex"]
    elif args.format:
        formats_to_test = [args.format]
    else:
        formats_to_test = ["html"]  # Default
    
    # Test conversions
    for fmt in formats_to_test:
        output_file = f"{args.output_dir}/test_output.{fmt}"
        result = test_conversion(
            api_url=args.api_url,
            markdown_content=markdown_content,
            output_format=fmt,
            output_file=output_file,
            api_key=args.api_key,
            use_json_endpoint=args.use_json_endpoint
        )
        results["conversions"][fmt] = result
        
        # Small delay between requests
        if fmt != formats_to_test[-1]:
            time.sleep(1)
    
    # Summary
    print_header("Test Summary")
    
    if not args.skip_health:
        status = "✓ PASS" if results["health"] else "✗ FAIL"
        print(f"Health Check: {status}")
    
    if not args.skip_formats:
        status = "✓ PASS" if results["formats"] else "✗ FAIL"
        print(f"Formats Endpoint: {status}")
    
    print(f"\nConversions:")
    for fmt, result in results["conversions"].items():
        status = "✓ PASS" if result.get("success") else "✗ FAIL"
        print(f"  {status} {fmt}: ", end="")
        if result.get("success"):
            print(f"{result.get('output_file')} ({result.get('file_size', 0):,} bytes, {result.get('elapsed_time', 0):.2f}s)")
        else:
            print(f"Failed - {result.get('error', 'Unknown error')}")
    
    # Overall status
    all_passed = (
        (args.skip_health or results["health"]) and
        (args.skip_formats or results["formats"]) and
        all(conv.get("success") for conv in results["conversions"].values())
    )
    
    if all_passed:
        print_success("\nAll tests passed!")
        sys.exit(0)
    else:
        print_error("\nSome tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
