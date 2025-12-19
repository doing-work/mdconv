# mdconv API Server

Simple REST API for converting markdown to various formats.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install fastapi uvicorn
   ```

2. **Start the server:**
   ```bash
   python api_server.py
   ```

3. **Server runs at:** `http://localhost:8000`

## API Endpoints

### `GET /`
Root endpoint - returns API info.

### `GET /formats`
List all supported output formats.

**Response:**
```json
{
  "formats": ["html", "pdf", "docx", "pptx", "epub", "latex"]
}
```

### `POST /convert`
Convert markdown string to another format.

**Request:**
```json
{
  "content": "# Hello World\n\nThis is markdown.",
  "output_format": "html",
  "options": {
    "standalone": true,
    "toc": true
  }
}
```

**Response:** Binary file (downloads automatically)

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "pandoc_available": true
}
```

## Usage Examples

### JavaScript/React

```javascript
// Convert markdown to HTML
const response = await fetch('http://localhost:8000/convert', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    content: '# Hello World',
    output_format: 'html',
    options: { standalone: true },
  }),
});

const blob = await response.blob();
const url = URL.createObjectURL(blob);
window.open(url); // Opens in new tab
```

### Python

```python
import requests

response = requests.post(
    'http://localhost:8000/convert',
    json={
        'content': '# Hello World',
        'output_format': 'html',
        'options': {'standalone': True},
    },
)

with open('output.html', 'wb') as f:
    f.write(response.content)
```

### cURL

```bash
curl -X POST http://localhost:8000/convert \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# Hello World",
    "output_format": "html",
    "options": {"standalone": true}
  }' \
  --output output.html
```

## Format-Specific Options

### HTML
```json
{
  "standalone": true,
  "toc": true,
  "css": ["style.css"],
  "mathjax": true
}
```

### PDF
```json
{
  "pdf_engine": "xhtml2pdf",
  "toc": true,
  "geometry": "margin=1in",
  "fontsize": "12pt"
}
```

### PPTX
```json
{
  "slide_level": 2,
  "theme": "modern",
  "theme_color": "#3498db",
  "font_family": "Arial"
}
```

### DOCX
```json
{
  "reference_doc": "template.docx",
  "toc": true
}
```

## CORS Configuration

For production, update CORS settings in `api_server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Deployment

### Local Development
```bash
python api_server.py
```

### Production (with uvicorn)
```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install fastapi uvicorn
COPY . .
RUN pip install -e .
EXPOSE 8000
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Error Handling

The API returns errors in JSON format:

```json
{
  "error": "Invalid format 'xyz'. Available formats: html, pdf, docx..."
}
```

Check the response status code:
- `200` - Success
- `400` - Bad request (invalid format, missing parameters)
- `500` - Server error (conversion failed)


