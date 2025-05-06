import React, { useState, useEffect, useCallback } from 'react';
import TextInput from './TextInput';
import ProcessedResult from './ProcessedResult';

const TextProcessor = ({ config }) => {
  const [text, setText] = useState(config.defaultText || '');
  const [processedText, setProcessedText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Debounce function to limit API calls
  const debounce = (func, wait) => {
    let timeout;
    return (...args) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  };

  // Process text through API - wrapped in useCallback to prevent recreation on each render
  const processText = useCallback(
    debounce(async (textToProcess) => {
      if (!textToProcess.trim()) {
        setProcessedText('');
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch('/experiments/text-processor/api/process', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ text: textToProcess })
        });

        const data = await response.json();

        if (data.success) {
          setProcessedText(data.result.processed_text);
        } else {
          setError(data.error || 'An error occurred while processing text');
        }
      } catch (err) {
        setError(err.message || 'Failed to process text');
      } finally {
        setIsLoading(false);
      }
    }, config.debounceDelayMs),
    [config.debounceDelayMs]
  );

  // Handle text input change
  const handleTextChange = (newText) => {
    setText(newText);
    processText(newText);
  };

  // Process default text on initial load if provided
  useEffect(() => {
    if (config.defaultText) {
      processText(config.defaultText);
    }
  }, [config.defaultText, processText]);

  return (
    <div className="text-processor">
      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <div className="p-6">
          <h5 className="text-xl font-semibold text-gray-800 mb-2">Process Text</h5>
          <p className="text-gray-600 mb-4">Enter text below and see it processed in real-time</p>

          <TextInput 
            value={text}
            onChange={handleTextChange}
            maxLength={config.maxTextLength}
          />

          <ProcessedResult 
            processedText={processedText}
            isLoading={isLoading}
            error={error}
          />

          <div className="mt-4">
            <span className="text-xs text-gray-500">Processing delay: {config.debounceDelayMs}ms</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TextProcessor; 