import React, { useState, useEffect, useCallback } from 'react';
import TextInput from './TextInput';
import ProcessedResult from './ProcessedResult';
import WebSocketResult from './WebSocketResult';
import AudioRecorder from './AudioRecorder';

/**
 * TextProcessor Component
 * 
 * Main component for processing text input, either from typing or audio recording.
 * 
 * TODO: Complete the integration with AudioRecorder component for end-to-end audio processing
 * ----------------------------------------------------------------------------------------
 * Next steps include:
 * - Implement backend API endpoint for handling audio files
 * - Add proper error handling for audio processing failures
 * - Extend the backend to support different AI models for processing audio input
 * - Improve the UX when switching between text and audio inputs
 */

const TextProcessor = ({ config }) => {
  const [text, setText] = useState(config.defaultText || '');
  const [processedText, setProcessedText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [audioBlob, setAudioBlob] = useState(null);
  const [transcribingAudio, setTranscribingAudio] = useState(false);
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

  // Handle captured audio
  const handleAudioCaptured = (blob, url) => {
    setAudioBlob(blob);
    // In a real implementation, you would send the audio to a speech-to-text service
    // For now, we'll just simulate the process with a message
    simulateTranscription(blob);
  };

  // Simulate audio transcription (would be replaced with actual transcription service)
  const simulateTranscription = (blob) => {
    setTranscribingAudio(true);
    
    // Simulate a delay for transcription process
    setTimeout(() => {
      // Mock transcription result
      const mockTranscription = "This is a simulated transcription of your audio recording. In a real implementation, this would be replaced with actual speech-to-text processing.";
      
      // Update the text input with the transcription
      setText(mockTranscription);
      
      // Process the transcribed text
      processText(mockTranscription);
      
      setTranscribingAudio(false);
    }, 2000);
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
          <p className="text-gray-600 mb-4">Enter text below or use audio input and see it processed in real-time</p>

          <TextInput 
            value={text}
            onChange={handleTextChange}
            maxLength={config.maxTextLength}
            disabled={transcribingAudio}
          />

          <AudioRecorder 
            onAudioCaptured={handleAudioCaptured}
          />

          {transcribingAudio && (
            <div className="my-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
              <div className="flex items-center">
                <svg className="animate-spin h-5 w-5 mr-2 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Transcribing audio... This is a simulation and would be replaced with actual speech-to-text conversion.</span>
              </div>
            </div>
          )}

          <div className="mb-4">
            <div className="flex items-center justify-between">
              <h6 className="text-sm font-semibold mb-2">Processing Results:</h6>
              
              <div className="flex space-x-2">
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
              processedText={processedText}
              isLoading={isLoading}
              error={error}
            />
          </div>

          {/* WebSocket Result */}
          {showWebSocketResults && (
            <WebSocketResult 
              inputText={text}
              audioBlob={audioBlob}
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