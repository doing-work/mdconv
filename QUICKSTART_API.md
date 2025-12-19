# Quick Start: Web API Integration

The simplest way to integrate mdconv into your React/website.

## 3-Step Setup

### Step 1: Install Dependencies
```bash
pip install fastapi uvicorn
```

### Step 2: Start the Server
```bash
python api_server.py
```

Server runs at: `http://localhost:8000`

### Step 3: Use in Your React App

Copy this code into your React component:

```javascript
const handleConvert = async () => {
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
  const a = document.createElement('a');
  a.href = url;
  a.download = 'output.html';
  a.click();
};
```

## Complete Example

See `examples/react/SimpleConverter.js` for a complete working component.

## API Endpoints

- `POST /convert` - Convert markdown to any format
- `GET /formats` - List supported formats
- `GET /health` - Health check

## Test the API

```bash
python test_api.py
```

## Full Documentation

- `API_README.md` - Complete API documentation
- `examples/react/` - React integration examples

That's it! No Docker, no complex setup, just start the server and use fetch().


