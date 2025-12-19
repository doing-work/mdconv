# React Integration Examples

Simple examples for integrating mdconv API into React applications.

## Quick Start

1. **Start the API server:**
   ```bash
   python api_server.py
   ```

2. **Use the component in your React app:**

### Option 1: Simple Component (JavaScript)
Copy `SimpleConverter.js` into your React app - no dependencies needed!

### Option 2: Full-Featured Component (TypeScript)
Use `MarkdownConverter.tsx` for a more complete solution with error handling.

## Usage Example

```jsx
import { SimpleConverter } from './SimpleConverter';

function App() {
  return (
    <div>
      <SimpleConverter />
    </div>
  );
}
```

## API Configuration

Set the API URL via environment variable:
```bash
REACT_APP_MDCONV_API_URL=http://localhost:8000 npm start
```

Or modify the `API_URL` constant in the component.

## API Endpoints

- `POST /convert` - Convert markdown string to another format
- `GET /formats` - List all supported formats
- `GET /health` - Health check

## Example Request

```javascript
const response = await fetch('http://localhost:8000/convert', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    content: '# Hello World',
    output_format: 'html',
    options: { standalone: true, toc: true },
  }),
});

const blob = await response.blob();
// Download or display the blob
```


