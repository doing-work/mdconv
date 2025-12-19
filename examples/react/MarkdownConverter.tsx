import React, { useState, useEffect } from 'react';

/**
 * Simple Markdown Converter Component
 * 
 * Usage:
 * 1. Start the API server: python api_server.py
 * 2. Use this component in your React app
 */

const API_URL = process.env.REACT_APP_MDCONV_API_URL || 'http://localhost:8000';

export const MarkdownConverter: React.FC = () => {
  const [markdown, setMarkdown] = useState('# Hello World\n\nThis is a **markdown** document.');
  const [outputFormat, setOutputFormat] = useState('html');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formats, setFormats] = useState<string[]>([]);

  useEffect(() => {
    // Fetch available formats
    fetch(`${API_URL}/formats`)
      .then((res) => res.json())
      .then((data) => setFormats(data.formats || []))
      .catch((err) => console.error('Failed to fetch formats:', err));
  }, []);

  const handleConvert = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/convert`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: markdown,
          output_format: outputFormat,
          options: {
            standalone: outputFormat === 'html',
            toc: true,
          },
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Conversion failed');
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `output.${outputFormat}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Conversion failed');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      // Read file as text
      const fileContent = await file.text();
      setMarkdown(fileContent);
    } catch (err) {
      setError('Failed to read file');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '900px', margin: '0 auto' }}>
      <h1>Markdown Converter</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
          Output Format:
        </label>
        <select
          value={outputFormat}
          onChange={(e) => setOutputFormat(e.target.value)}
          style={{
            padding: '8px',
            fontSize: '16px',
            borderRadius: '4px',
            border: '1px solid #ccc',
            minWidth: '150px',
          }}
        >
          {formats.length > 0 ? (
            formats.map((fmt) => (
              <option key={fmt} value={fmt}>
                {fmt.toUpperCase()}
              </option>
            ))
          ) : (
            <>
              <option value="html">HTML</option>
              <option value="pdf">PDF</option>
              <option value="docx">DOCX</option>
              <option value="pptx">PPTX</option>
            </>
          )}
        </select>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
          Markdown Content:
        </label>
        <textarea
          value={markdown}
          onChange={(e) => setMarkdown(e.target.value)}
          rows={15}
          style={{
            width: '100%',
            padding: '10px',
            fontSize: '14px',
            fontFamily: 'monospace',
            border: '1px solid #ccc',
            borderRadius: '4px',
            resize: 'vertical',
          }}
          placeholder="Enter your markdown here..."
        />
      </div>

      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
          Or Upload Markdown File:
        </label>
        <input
          type="file"
          onChange={handleFileUpload}
          accept=".md,.markdown,.txt"
          style={{ padding: '5px' }}
        />
      </div>

      <button
        onClick={handleConvert}
        disabled={loading || !markdown.trim()}
        style={{
          padding: '12px 24px',
          fontSize: '16px',
          backgroundColor: loading ? '#ccc' : '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: loading ? 'not-allowed' : 'pointer',
          fontWeight: 'bold',
        }}
      >
        {loading ? 'Converting...' : 'Convert & Download'}
      </button>

      {error && (
        <div
          style={{
            marginTop: '20px',
            padding: '10px',
            backgroundColor: '#fee',
            color: '#c33',
            borderRadius: '4px',
            border: '1px solid #fcc',
          }}
        >
          <strong>Error:</strong> {error}
        </div>
      )}

      <div style={{ marginTop: '30px', fontSize: '12px', color: '#666' }}>
        <p>
          <strong>API URL:</strong> {API_URL}
        </p>
        <p>
          Make sure the API server is running: <code>python api_server.py</code>
        </p>
      </div>
    </div>
  );
};

export default MarkdownConverter;


