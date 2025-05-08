import React, { useState, useEffect, useRef } from 'react';

/**
 * WebSocketResult Component
 * 
 * This component establishes a WebSocket connection to the server
 * and displays processing results streamed in real-time.
 */
const WebSocketResult = ({ inputText, audioBlob }) => {
  const [connected, setConnected] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  // Connect to WebSocket and handle connection lifecycle
  useEffect(() => {
    const connectWebSocket = () => {
      // Clear any existing error state when attempting to connect
      setError(null);

      // Determine the WebSocket URL (secure or not)
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      const wsUrl = `${protocol}//${host}/experiments/text-processor/ws`;

      try {
        // Create a new WebSocket connection
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        // Setup event handlers
        ws.onopen = () => {
          console.log('WebSocket connection established');
          setConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'processing_start') {
              setProcessing(true);
              // Clear previous results when a new processing starts
              setResults([]);
            } 
            else if (data.type === 'processing_update') {
              // Add the new chunk to results
              setResults(prevResults => [...prevResults, data.chunk]);
            } 
            else if (data.type === 'processing_complete') {
              setProcessing(false);
            } 
            else if (data.type === 'error') {
              setError(data.message || 'An error occurred during processing');
              setProcessing(false);
            }
          } catch (e) {
            console.error('Error parsing WebSocket message:', e);
            setError('Failed to parse server message');
          }
        };

        ws.onclose = (event) => {
          setConnected(false);
          
          // WebSocket closed unexpectedly - attempt to reconnect
          if (!event.wasClean) {
            setError('WebSocket connection lost, attempting to reconnect...');
            
            // Try to reconnect after a delay
            reconnectTimeoutRef.current = setTimeout(connectWebSocket, 3000);
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          setError('WebSocket connection error');
          ws.close();
        };

      } catch (err) {
        console.error('Failed to establish WebSocket connection:', err);
        setError('Failed to connect to the server via WebSocket');
        
        // Try to reconnect after a delay
        reconnectTimeoutRef.current = setTimeout(connectWebSocket, 3000);
      }
    };

    // Initialize connection
    connectWebSocket();

    // Cleanup function
    return () => {
      // Close WebSocket connection
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      
      // Clear any pending reconnect timeouts
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
    };
  }, []);

  // Send text for processing when inputText changes
  useEffect(() => {
    if (connected && inputText && wsRef.current) {
      // Only send if the connection is established
      const message = {
        type: 'process_text',
        text: inputText
      };
      wsRef.current.send(JSON.stringify(message));
    }
  }, [connected, inputText]);

  // Send audio for processing when audioBlob changes
  useEffect(() => {
    const processAudio = async () => {
      if (connected && audioBlob && wsRef.current) {
        try {
          // Convert blob to base64 for sending via WebSocket
          const reader = new FileReader();
          reader.readAsDataURL(audioBlob);
          
          reader.onloadend = () => {
            // Extract the base64 data (remove the data URL prefix)
            const base64data = reader.result.split(',')[1];
            
            const message = {
              type: 'process_audio',
              audio_data: base64data,
              format: audioBlob.type
            };
            
            wsRef.current.send(JSON.stringify(message));
          };
        } catch (err) {
          console.error('Error processing audio for WebSocket:', err);
          setError('Failed to process audio for streaming');
        }
      }
    };
    
    processAudio();
  }, [connected, audioBlob]);

  return (
    <div className="mt-4 p-4 bg-gray-50 rounded-md border border-gray-200">
      <div className="flex items-center justify-between mb-2">
        <h6 className="text-sm font-semibold">WebSocket Stream Results:</h6>
        <div className="flex items-center">
          {connected ? (
            <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
              <span className="h-2 w-2 mr-1 rounded-full bg-green-500"></span>
              Connected
            </span>
          ) : (
            <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800">
              <span className="h-2 w-2 mr-1 rounded-full bg-red-500"></span>
              Disconnected
            </span>
          )}
        </div>
      </div>
      
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">
          {error}
        </div>
      )}
      
      <div className="p-3 bg-white border border-gray-200 rounded-md min-h-[100px] relative">
        {processing && (
          <div className="absolute left-3 top-3">
            <div className="flex items-center text-blue-500">
              <div className="animate-pulse h-2 w-2 bg-blue-500 rounded-full mr-1"></div>
              <div className="animate-pulse h-2 w-2 bg-blue-500 rounded-full mr-1 [animation-delay:0.2s]"></div>
              <div className="animate-pulse h-2 w-2 bg-blue-500 rounded-full [animation-delay:0.4s]"></div>
            </div>
          </div>
        )}
        
        <div className={`${processing ? 'mt-6' : ''}`}>
          {results.length > 0 ? (
            <div>
              {results.map((chunk, index) => (
                <span key={index} className={index === results.length - 1 && processing ? 'animate-pulse' : ''}>
                  {chunk}
                </span>
              ))}
            </div>
          ) : (
            <div className="text-gray-400 italic">
              {connected ? (processing ? 'Processing...' : 'Waiting for input...') : 'Connecting to server...'}
            </div>
          )}
        </div>
      </div>
      
      <div className="mt-2 text-xs text-gray-500">
        <span>WebSocket processing provides real-time streaming results</span>
      </div>
    </div>
  );
};

export default WebSocketResult; 