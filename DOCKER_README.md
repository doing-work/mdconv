# Docker Setup for mdconv FastAPI

This directory contains Docker configuration for running the mdconv FastAPI server in a containerized environment.

## Quick Start

### Using Docker Compose (Recommended)

1. **Build and start the container:**
   ```bash
   docker-compose up --build
   ```

2. **Run in detached mode:**
   ```bash
   docker-compose up -d
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Stop the container:**
   ```bash
   docker-compose down
   ```

### Using Docker Directly

1. **Build the image:**
   ```bash
   docker build -t mdconv-api .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 mdconv-api
   ```

3. **Run with environment variables:**
   ```bash
   docker run -p 8000:8000 \
     -e API_KEY=your-api-key \
     -e ALLOWED_ORIGINS=http://localhost:3000 \
     mdconv-api
   ```

## Testing

### Test All Conversions

Run the comprehensive test script to test all supported formats:

```bash
# Test all formats
python test_docker_conversions.py --all-formats

# Test specific format
python test_docker_conversions.py --format pdf

# Test with custom file
python test_docker_conversions.py --file mydoc.md --all-formats

# Test with API key
python test_docker_conversions.py --api-key mykey --all-formats
```

### Manual Testing

1. **Health check:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **List formats:**
   ```bash
   curl http://localhost:8000/formats
   ```

3. **Convert markdown to HTML:**
   ```bash
   curl -X POST http://localhost:8000/convert \
     -H "Content-Type: application/json" \
     -d '{"content": "# Hello World", "output_format": "html"}' \
     -o output.html
   ```

4. **Convert with file upload:**
   ```bash
   curl -X POST http://localhost:8000/convert \
     -F "file=@test_sample.md" \
     -F "output_format=pdf" \
     -o output.pdf
   ```

## Environment Variables

- `API_KEY`: Optional API key for authentication (default: no authentication)
- `ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins (default: `*`)
- `PYTHONUNBUFFERED`: Set to `1` for real-time logging (default: `1`)

## Supported Formats

The containerized API supports the following output formats:

- **html** - HTML5 output
- **pdf** - PDF documents (requires xhtml2pdf)
- **docx** - Microsoft Word documents
- **pptx** - PowerPoint presentations
- **epub** - EPUB e-books
- **latex** - LaTeX source

## Output Files

Converted files are saved to the `output/` directory (mounted as a volume in docker-compose).

## Troubleshooting

### Container won't start

1. Check if port 8000 is already in use:
   ```bash
   netstat -an | grep 8000  # Linux/Mac
   netstat -an | findstr 8000  # Windows
   ```

2. Check container logs:
   ```bash
   docker-compose logs
   ```

### Conversion fails

1. Check if pandoc is available:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check container logs for errors:
   ```bash
   docker-compose logs api
   ```

### PDF conversion issues

PDF conversion requires xhtml2pdf, which is included in the requirements. If PDF conversion fails, check the container logs for specific error messages.

## Development

To modify the API and test changes:

1. Make your changes to the code
2. Rebuild the container:
   ```bash
   docker-compose build
   docker-compose up
   ```

Or use volume mounting for live development (modify docker-compose.yml):

```yaml
volumes:
  - .:/app
```

## Production Considerations

For production deployment:

1. Set a strong `API_KEY` environment variable
2. Configure `ALLOWED_ORIGINS` to restrict CORS
3. Use a reverse proxy (nginx, traefik) for SSL/TLS
4. Consider using Docker secrets for sensitive data
5. Set up proper logging and monitoring
6. Use a production WSGI server like gunicorn with uvicorn workers

Example production docker-compose:

```yaml
services:
  api:
    build: .
    environment:
      - API_KEY=${API_KEY}
      - ALLOWED_ORIGINS=${ALLOWED_ORIGINS}
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```
