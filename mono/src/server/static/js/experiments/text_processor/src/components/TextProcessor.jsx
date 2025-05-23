import React, { useState, useEffect, useCallback } from 'react';
import TextInput from './TextInput';
import ProcessedResult from './ProcessedResult';
import WebSocketResult from './WebSocketResult';

/**
 * TextProcessor Component
 * 
 * Main component for processing text input from typing.
 * Audio processing functionality has been moved to a separate AudioProcessor component.
 */

const TextProcessor = ({ config }) => {
  const [text, setText] = useState(config.defaultText || '');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showWebSocketResults, setShowWebSocketResults] = useState(true);

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
        setResponse('');
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
          setResponse(data.result.response || '');
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

  // Toggle between showing/hiding WebSocket results
  const toggleWebSocketResults = () => {
    setShowWebSocketResults(!showWebSocketResults);
  };

  // Process default text on initial load if provided
  useEffect(() => {
    if (config.defaultText) {
      processText(config.defaultText);
    }
  }, [config.defaultText, processText]);

  return (
    <div className="text-processor">
      <div className="bg-white shadow-md rounded-lg overflow-hidden mb-6">
        <div className="p-6">
          <h5 className="text-xl font-semibold text-gray-800 mb-2">Process Text</h5>
          <p className="text-gray-600 mb-4">Enter text below and see it processed in real-time</p>

          <TextInput 
            value={text}
            onChange={handleTextChange}
            maxLength={config.maxTextLength}
          />

          <div className="mb-4">
            <div className="flex items-center justify-between">
              <h6 className="text-sm font-semibold mb-2">Processing Results:</h6>
              
              <div className="flex space-x-2">
                <a 
                  href="/experiments/text-processor/audio"
                  className="px-2 py-1 text-xs font-medium rounded bg-green-100 text-green-800 hover:bg-green-200"
                >
                  Try Audio Processor
                </a>
                <button 
                  onClick={toggleWebSocketResults}
                  className={`px-2 py-1 text-xs font-medium rounded 
                    ${showWebSocketResults ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'}`}
                >
                  {showWebSocketResults ? 'Hide WebSocket Results' : 'Show WebSocket Results'}
                </button>
              </div>
            </div>
          </div>

          {/* Traditional HTTP Result */}
          <div className="mb-4">
            <h6 className="text-sm font-semibold mb-2">HTTP Result:</h6>
            <ProcessedResult 
              response={response}
              isLoading={isLoading}
              error={error}
            />
          </div>

          {/* WebSocket Result */}
          {showWebSocketResults && (
            <WebSocketResult 
              inputText={text}
            />
          )}

          <div className="mt-4">
            <span className="text-xs text-gray-500">Processing delay: {config.debounceDelayMs}ms</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TextProcessor; 