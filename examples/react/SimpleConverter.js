/**
 * Simplest possible React component - just copy and paste
 * 
 * Usage:
 * 1. Start API server: python api_server.py
 * 2. Copy this code into your React component
 */

import React, { useState } from 'react';

export const SimpleConverter = () => {
  const [markdown, setMarkdown] = useState('# Hello World\n\nThis is markdown.');
  const [format, setFormat] = useState('html');
  const [loading, setLoading] = useState(false);

  const handleConvert = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/convert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: markdown,
          output_format: format,
          options: { standalone: format === 'html' },
        }),
      });

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `output.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      alert('Conversion failed: ' + error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Markdown Converter</h1>
      
      <select value={format} onChange={(e) => setFormat(e.target.value)}>
        <option value="html">HTML</option>
        <option value="pdf">PDF</option>
        <option value="docx">DOCX</option>
        <option value="pptx">PPTX</option>
      </select>

      <textarea
        value={markdown}
        onChange={(e) => setMarkdown(e.target.value)}
        rows={10}
        style={{ width: '100%', margin: '10px 0' }}
      />

      <button onClick={handleConvert} disabled={loading}>
        {loading ? 'Converting...' : 'Convert'}
      </button>
    </div>
  );
};


