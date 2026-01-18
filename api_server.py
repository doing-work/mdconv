"""Secure API server for mdconv with authentication and rate limiting."""

import os
import json
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from mdconv import Converter
from mdconv.utils.exceptions import InvalidFormatError, MDConvError

# Initialize FastAPI app
app = FastAPI(
    title="mdconv API",
    description="Secure REST API for converting markdown to various formats",
    version="0.2.0",
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS - restrict to allowed origins
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
# Remove empty strings and strip whitespace
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if "*" not in ALLOWED_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)

# Lazy converter initialization (singleton pattern)
_converter_instance: Optional[Converter] = None
_converter_error: Optional[Exception] = None


def get_converter() -> Converter:
    """Get or create the converter instance (lazy initialization)."""
    global _converter_instance, _converter_error
    if _converter_instance is None and _converter_error is None:
        try:
            _converter_instance = Converter()
        except Exception as e:
            _converter_error = e
            raise
    elif _converter_error is not None:
        raise _converter_error
    return _converter_instance


# API Key configuration
API_KEY = os.getenv("API_KEY", "")
_api_key_cache: Optional[str] = None


def get_api_key() -> Optional[str]:
    """Get API key from environment variable."""
    global _api_key_cache
    
    # Return cached key if available
    if _api_key_cache:
        return _api_key_cache
    
    # Get API key from environment variable
    if API_KEY:
        _api_key_cache = API_KEY
        return _api_key_cache
    
    return None


def verify_api_key(request: Request) -> bool:
    """Verify API key from request header."""
    api_key = get_api_key()
    
    # If no API key is configured, allow access (for development)
    if not api_key:
        return True
    
    # Get API key from header
    provided_key = request.headers.get("X-API-Key")
    if not provided_key:
        return False
    
    return provided_key == api_key


# Public endpoints (no authentication required)
PUBLIC_ENDPOINTS = ["/", "/health", "/docs", "/openapi.json", "/redoc", "/convert"]


@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    """Middleware to verify API key for protected endpoints."""
    # Skip authentication for public endpoints
    if request.url.path in PUBLIC_ENDPOINTS:
        return await call_next(request)
    
    # Verify API key for protected endpoints
    if not verify_api_key(request):
        return Response(
            content=json.dumps({"detail": "Invalid or missing API key. Provide X-API-Key header."}),
            status_code=status.HTTP_401_UNAUTHORIZED,
            media_type="application/json",
        )
    
    return await call_next(request)


class ConvertRequest(BaseModel):
    """Request model for conversion with validation."""
    content: str = Field(..., min_length=1, max_length=5000000)  # Max 5MB content
    output_format: str = Field(..., pattern="^(html|pdf|docx|pptx|epub|latex)$")
    options: dict = Field(default_factory=dict, max_length=20)  # Max 20 options
    
    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate content is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("Content cannot be empty or whitespace only")
        return v
    
    @field_validator("output_format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate output format is supported."""
        supported = ["html", "pdf", "docx", "pptx", "epub", "latex"]
        if v not in supported:
            raise ValueError(f"Unsupported format. Supported formats: {', '.join(supported)}")
        return v


@app.get("/")
async def root():
    """Root endpoint - public."""
    return {
        "name": "mdconv API",
        "version": "0.2.0",
        "status": "running",
        "authenticated": bool(get_api_key()),
    }


@app.get("/formats")
@limiter.limit("30/minute")  # Rate limit: 30 requests per minute
async def list_formats(request: Request):
    """List all supported output formats - requires API key."""
    return {"formats": get_converter().list_formats()}


@app.post("/convert")
@limiter.limit("10/minute")  # Rate limit: 10 conversions per minute per IP
async def convert(request: Request):
    """
    Convert markdown to another format - supports both file upload and JSON content.
    
    Accepts:
    - multipart/form-data: file (markdown file) OR content (markdown string), output_format, options (JSON string)
    - application/json: { "content": "...", "output_format": "...", "options": {...} }
    
    Requires API key.
    """
    try:
        content_type_header = request.headers.get("content-type", "").lower()
        markdown_content = None
        output_format = None
        conversion_options = {}
        
        # Check if it's multipart/form-data (file upload)
        if "multipart/form-data" in content_type_header:
            form = await request.form()
            
            # Get file if provided
            if "file" in form:
                file = form["file"]
                if hasattr(file, "file"):
                    # It's an UploadFile
                    content_bytes = await file.read()
                    if len(content_bytes) > 10 * 1024 * 1024:  # 10MB limit
                        raise HTTPException(
                            status_code=400,
                            detail="File size exceeds 10MB limit"
                        )
                    try:
                        markdown_content = content_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        raise HTTPException(
                            status_code=400,
                            detail="File must be valid UTF-8 encoded text"
                        )
                else:
                    # It's a string (content field)
                    markdown_content = str(file)
            
            # Get content if provided (alternative to file)
            if "content" in form and not markdown_content:
                markdown_content = form["content"]
            
            # Get output_format
            if "output_format" in form:
                output_format = form["output_format"]
            
            # Get options if provided
            if "options" in form:
                options_str = form["options"]
                try:
                    conversion_options = json.loads(options_str) if isinstance(options_str, str) else options_str
                except json.JSONDecodeError:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid options: must be valid JSON"
                    )
        else:
            # Try to parse as JSON
            try:
                body = await request.json()
                markdown_content = body.get("content")
                output_format = body.get("output_format")
                conversion_options = body.get("options", {})
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid request body. Expected JSON or multipart/form-data. Error: {str(e)}"
                )
        
        # Validate required fields
        if not markdown_content:
            raise HTTPException(
                status_code=400,
                detail="Either 'file' or 'content' must be provided"
            )
        
        if not output_format:
            raise HTTPException(
                status_code=400,
                detail="'output_format' is required"
            )
        
        if not markdown_content.strip():
            raise HTTPException(
                status_code=400,
                detail="Content cannot be empty or whitespace only"
            )
        
        # Validate output format
        supported_formats = ["html", "pdf", "docx", "pptx", "epub", "latex"]
        if output_format not in supported_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format. Supported formats: {', '.join(supported_formats)}"
            )
        
        # Validate content size
        if len(markdown_content) > 5000000:  # 5MB limit
            raise HTTPException(
                status_code=400,
                detail="Content exceeds 5MB limit"
            )
        
        # Perform conversion
        result = get_converter().convert_string(
            markdown_content=markdown_content,
            output_format=output_format,
            **conversion_options,
        )
        
        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Conversion returned no result"
            )
        
        # Determine content type based on format
        content_types = {
            "html": "text/html",
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "epub": "application/epub+zip",
            "latex": "text/x-latex",
        }
        
        content_type = content_types.get(output_format, "application/octet-stream")
        
        return Response(
            content=result,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="output.{output_format}"',
            },
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except InvalidFormatError as e:
        # Invalid format is a client error (400)
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except MDConvError as e:
        # Other mdconv errors - could be client or server error
        # For now, treat as server error (500)
        raise HTTPException(
            status_code=500,
            detail=f"Conversion error: {str(e)}"
        )
    except Exception as e:
        # Unexpected errors are server errors (500)
        raise HTTPException(
            status_code=500,
            detail=f"Conversion failed: {str(e)}"
        )


@app.post("/convert/json")
@limiter.limit("10/minute")  # Rate limit: 10 conversions per minute per IP
async def convert_json(request: Request, convert_request: ConvertRequest):
    """
    Convert markdown string to another format (JSON endpoint) - requires API key.
    
    This endpoint accepts JSON body for backward compatibility.
    For file uploads, use /convert with multipart/form-data.
    """
    try:
        result = get_converter().convert_string(
            markdown_content=convert_request.content,
            output_format=convert_request.output_format,
            **convert_request.options,
        )
        
        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Conversion returned no result"
            )
        
        # Determine content type based on format
        content_types = {
            "html": "text/html",
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "epub": "application/epub+zip",
            "latex": "text/x-latex",
        }
        
        content_type = content_types.get(convert_request.output_format, "application/octet-stream")
        
        return Response(
            content=result,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="output.{convert_request.output_format}"',
            },
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except InvalidFormatError as e:
        # Invalid format is a client error (400)
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except MDConvError as e:
        # Other mdconv errors - could be client or server error
        # For now, treat as server error (500)
        raise HTTPException(
            status_code=500,
            detail=f"Conversion error: {str(e)}"
        )
    except Exception as e:
        # Unexpected errors are server errors (500)
        raise HTTPException(
            status_code=500,
            detail=f"Conversion failed: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint - public."""
    return {
        "status": "healthy",
        "pandoc_available": get_converter().pandoc_wrapper.check_available(),
        "authenticated": bool(get_api_key()),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
