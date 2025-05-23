import React, { useState } from 'react';
import TextInput from './TextInput';
import ProcessedResult from './ProcessedResult';

/**
 * TextProcessor Component
 * 
 * Main component for processing text input from typing.
 * Processes text only when Enter is pressed, not in real-time.
 * WebSocket functionality has been moved to the AudioProcessor component.
 */

const TextProcessor = ({ config }) => {
  const [text, setText] = useState(config.defaultText || '');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Process text through API when Enter is pressed
  const processText = async (textToProcess) => {
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
  };

  // Handle text input change (only update text, don't process)
  const handleTextChange = (newText) => {
    setText(newText);
  };

  // Handle Enter key press to trigger processing
  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      processText(text);
    }
  };

  return (
    <div className="text-processor">
      <div className="bg-white shadow-md rounded-lg overflow-hidden mb-6">
        <div className="p-6">
          <h5 className="text-xl font-semibold text-gray-800 mb-2">Text Transformer</h5>
          <p className="text-gray-600 mb-4">Enter text and press Enter to transform it. First input establishes the text state, subsequent inputs apply modifications.</p>

          <div className="mb-4">
            <TextInput 
              value={text}
              onChange={handleTextChange}
              onKeyPress={handleKeyPress}
              maxLength={config.maxTextLength}
              placeholder="Type your text and press Enter to process..."
            />
            <p className="text-xs text-gray-500 mt-1">
              Press Enter to process • Example: "a bright blue cow" → "make it red"
            </p>
          </div>

          <div className="mb-4">
            <div className="flex items-center justify-between">
              <h6 className="text-sm font-semibold mb-2">Transformation Result:</h6>
              
              <div className="flex space-x-2">
                <a 
                  href="/experiments/text-processor/audio"
                  className="px-2 py-1 text-xs font-medium rounded bg-green-100 text-green-800 hover:bg-green-200"
                >
                  Try Audio Processor
                </a>
              </div>
            </div>
          </div>

          {/* Processing Result */}
          <ProcessedResult 
            response={response}
            isLoading={isLoading}
            error={error}
          />

          <div className="mt-4">
            <span className="text-xs text-gray-500">
              Text transformation powered by AI • Real-time WebSocket processing available in Audio Processor
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TextProcessor; 