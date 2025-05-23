import React, { useState, useCallback } from 'react';
import AudioRecorder from './AudioRecorder';
import ProcessedResult from './ProcessedResult';
import WebSocketResult from './WebSocketResult';

/**
 * AudioProcessor Component
 * 
 * Dedicated component for audio input processing, separated from the main text processor.
 * This component handles audio recording, transcription, and AI processing.
 */

const AudioProcessor = ({ config }) => {
  const [transcribedText, setTranscribedText] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [audioBlob, setAudioBlob] = useState(null);
  const [transcribingAudio, setTranscribingAudio] = useState(false);
  const [showWebSocketResults, setShowWebSocketResults] = useState(true);

  // Process text through API
  const processText = useCallback(async (textToProcess) => {
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
  }, []);

  // Handle captured audio
  const handleAudioCaptured = (blob, url) => {
    setAudioBlob(blob);
    simulateTranscription(blob);
  };

  // Simulate audio transcription (would be replaced with actual transcription service)
  const simulateTranscription = (blob) => {
    setTranscribingAudio(true);
    
    // Simulate a delay for transcription process
    setTimeout(() => {
      // Mock transcription result
      const mockTranscription = "This is a simulated transcription of your audio recording. In a real implementation, this would be replaced with actual speech-to-text processing.";
      
      // Update the transcribed text
      setTranscribedText(mockTranscription);
      
      // Process the transcribed text
      processText(mockTranscription);
      
      setTranscribingAudio(false);
    }, 2000);
  };

  // Toggle between showing/hiding WebSocket results
  const toggleWebSocketResults = () => {
    setShowWebSocketResults(!showWebSocketResults);
  };

  // Clear all results
  const clearResults = () => {
    setTranscribedText('');
    setResponse('');
    setAudioBlob(null);
    setError(null);
  };

  return (
    <div className="audio-processor">
      <div className="bg-white shadow-md rounded-lg overflow-hidden mb-6">
        <div className="p-6">
          <h5 className="text-xl font-semibold text-gray-800 mb-2">Audio Processing</h5>
          <p className="text-gray-600 mb-4">Record audio and see it transcribed and processed with AI</p>

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

          {transcribedText && (
            <div className="mb-4">
              <h6 className="text-sm font-semibold mb-2">Transcribed Text:</h6>
              <div className="p-3 bg-gray-50 border border-gray-200 rounded-md">
                <p className="text-gray-800">{transcribedText}</p>
              </div>
            </div>
          )}

          <div className="mb-4">
            <div className="flex items-center justify-between">
              <h6 className="text-sm font-semibold mb-2">Processing Results:</h6>
              
              <div className="flex space-x-2">
                <button 
                  onClick={clearResults}
                  className="px-2 py-1 text-xs font-medium rounded bg-red-100 text-red-800 hover:bg-red-200"
                >
                  Clear All
                </button>
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
              inputText={transcribedText}
              audioBlob={audioBlob}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default AudioProcessor; 