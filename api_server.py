"""Simple API server for mdconv - minimal setup."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

from mdconv import Converter

app = FastAPI(
    title="mdconv API",
    description="Simple REST API for converting markdown to various formats",
    version="0.1.0",
)

# Enable CORS for all origins (configure as needed for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize converter (singleton)
converter = Converter()


class ConvertRequest(BaseModel):
    """Request model for conversion."""
    content: str
    output_format: str
    options: dict = {}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "mdconv API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/formats")
async def list_formats():
    """List all supported output formats."""
    return {"formats": converter.list_formats()}


@app.post("/convert")
async def convert(request: ConvertRequest):
    """Convert markdown string to another format."""
    try:
        result = converter.convert_string(
            markdown_content=request.content,
            output_format=request.output_format,
            **request.options,
        )
        
        if result is None:
            return {"error": "Conversion returned no result"}, 500
        
        # Determine content type based on format
        content_types = {
            "html": "text/html",
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "epub": "application/epub+zip",
            "latex": "text/x-latex",
        }
        
        content_type = content_types.get(request.output_format, "application/octet-stream")
        
        return Response(
            content=result,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="output.{request.output_format}"',
            },
        )
    except Exception as e:
        return Response(
            content=f'{{"error": "{str(e)}"}}',
            media_type="application/json",
            status_code=400,
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "pandoc_available": converter.pandoc_wrapper.check_available(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


