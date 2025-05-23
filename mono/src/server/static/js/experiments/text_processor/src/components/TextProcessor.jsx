import React, { useState } from 'react';
import TextInput from './TextInput';

/**
 * TextProcessor Component
 * 
 * Two-input interface for text transformation:
 * 1. Transformation Command (for applying changes)
 * 2. Current Text State (editable by user, updated by AI responses)
 */

const TextProcessor = ({ config }) => {
  const [currentText, setCurrentText] = useState(config.defaultText || '');
  const [transformCommand, setTransformCommand] = useState('');
  const [sessionId] = useState(() => 'session_' + Math.random().toString(36).substr(2, 9));
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Process transformation command
  const processTransformation = async (command) => {
    if (!command.trim()) {
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
        body: JSON.stringify({ 
          text: command,
          session_id: sessionId 
        })
      });

      const data = await response.json();

      if (data.success) {
        const result = data.result.response || '';
        // Update current text with the transformation result
        setCurrentText(result.replace(/^['"]|['"]$/g, '')); // Remove quotes if present
        // Clear the transformation command after successful processing
        setTransformCommand('');
      } else {
        setError(data.error || 'An error occurred while processing transformation');
      }
    } catch (err) {
      setError(err.message || 'Failed to process transformation');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle text establishment (when current text is empty or being set initially)
  const establishTextState = async (text) => {
    if (!text.trim()) {
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
        body: JSON.stringify({ 
          text: text,
          session_id: sessionId 
        })
      });

      const data = await response.json();

      if (data.success) {
        const result = data.result.response || '';
        setCurrentText(result.replace(/^['"]|['"]$/g, '')); // Remove quotes if present
      } else {
        setError(data.error || 'An error occurred while establishing text state');
      }
    } catch (err) {
      setError(err.message || 'Failed to establish text state');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Enter key press in current text field (establish state)
  const handleCurrentTextKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      establishTextState(currentText);
    }
  };

  // Handle Enter key press in transform command field (apply transformation)
  const handleTransformKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      processTransformation(transformCommand);
    }
  };

  return (
    <div className="text-processor">
      <div className="bg-white shadow-md rounded-lg overflow-hidden mb-6">
        <div className="p-6">
          <h5 className="text-xl font-semibold text-gray-800 mb-2">Text Transformer</h5>
          <p className="text-gray-600 mb-6">
            Enter transformation commands to modify your text, or establish initial text state below.
          </p>

          {/* Transformation Command */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Transformation Command
            </label>
            <TextInput 
              value={transformCommand}
              onChange={setTransformCommand}
              onKeyPress={handleTransformKeyPress}
              maxLength={config.maxTextLength}
              placeholder="Enter transformation command (e.g., 'a blue car', 'make it red', 'add wings', 'make it plural')..."
            />
            <p className="text-xs text-gray-500 mt-1">
              Press Enter to process • Use this for initial text or transformations
            </p>
          </div>

          {/* Current Text State */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Current Text State
            </label>
            <TextInput 
              value={currentText}
              onChange={setCurrentText}
              onKeyPress={handleCurrentTextKeyPress}
              maxLength={config.maxTextLength}
              placeholder="Your current text will appear here... You can also manually edit this field and press Enter."
            />
            <p className="text-xs text-gray-500 mt-1">
              Auto-updated by transformations • You can manually edit and press Enter to establish new state
            </p>
          </div>

          {/* Status/Error Display */}
          {isLoading && (
            <div className="mb-4 p-3 bg-blue-50 text-blue-700 rounded-md">
              Processing...
            </div>
          )}

          {error && (
            <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-md">
              <strong>Error:</strong> {error}
            </div>
          )}

          {/* Instructions */}
          <div className="mt-6 p-4 bg-gray-50 rounded-md">
            <h6 className="text-sm font-semibold mb-2">How to Use:</h6>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>1. Enter text or commands in "Transformation Command" and press Enter</li>
              <li>2. Results appear in "Current Text State" below</li>
              <li>3. Continue with more transformations (e.g., "make it red", "add wings")</li>
              <li>4. You can manually edit the current text state anytime</li>
            </ul>
          </div>

          <div className="mt-4 flex justify-between items-center">
            <span className="text-xs text-gray-500">
              Two-step AI transformation: Intent Analysis → Execution
            </span>
            
            <a 
              href="/experiments/text-processor/audio"
              className="px-3 py-1 text-xs font-medium rounded bg-green-100 text-green-800 hover:bg-green-200"
            >
              Try Audio Processor
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TextProcessor; 