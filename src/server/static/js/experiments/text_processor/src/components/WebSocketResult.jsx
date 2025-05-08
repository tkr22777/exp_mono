import React, { useState, useEffect, useRef } from 'react';
import { io } from 'socket.io-client';

/**
 * WebSocketResult Component - Displays streaming results using Socket.IO
 */
const WebSocketResult = ({ inputText, audioBlob }) => {
  const [connected, setConnected] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const socketRef = useRef(null);
  const processingRef = useRef(false);
  const latestInputRef = useRef('');
  const processingTimeoutRef = useRef(null);

  // Connect to Socket.IO
  useEffect(() => {
    setError(null);

    const socket = io(window.location.origin, {
      path: '/socket.io',
      transports: ['websocket', 'polling'],
      autoConnect: true,
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5
    });
    
    socketRef.current = socket;
    socket.emit('join', { namespace: '/experiments/text-processor/ws' });

    socket.on('connect', () => {
      setConnected(true);
      setError(null);
    });

    socket.on('disconnect', (reason) => {
      setConnected(false);
      if (reason === 'io server disconnect') {
        socket.connect();
      }
    });

    socket.on('connect_error', (err) => {
      setError('Connection error: ' + (err.message || 'Unknown error'));
      setConnected(false);
    });

    socket.on('processing_start', () => {
      setProcessing(true);
      setResults([]);
    });

    socket.on('processing_update', (data) => {
      setResults(prevResults => [...prevResults, data.chunk]);
    });

    socket.on('processing_complete', () => {
      setProcessing(false);
      processingRef.current = false;
      
      if (latestInputRef.current !== inputText && inputText) {
        processLatestInput();
      }
    });

    socket.on('error', (data) => {
      setError(data.message || 'Processing error');
      setProcessing(false);
      processingRef.current = false;
    });

    return () => {
      clearTimeout(processingTimeoutRef.current);
      socket.disconnect();
      socketRef.current = null;
    };
  }, []);

  // Process text with debounce
  const processLatestInput = () => {
    if (!connected || !socketRef.current || !inputText || processingRef.current) return;
    
    processingRef.current = true;
    latestInputRef.current = inputText;
    socketRef.current.emit('process_text', { text: inputText });
  };

  // Handle input text changes
  useEffect(() => {
    if (!connected || !socketRef.current || !inputText) return;
    
    latestInputRef.current = inputText;
    clearTimeout(processingTimeoutRef.current);
    
    if (processingRef.current) return;
    
    processingTimeoutRef.current = setTimeout(() => {
      processLatestInput();
    }, 300);
    
    return () => clearTimeout(processingTimeoutRef.current);
  }, [connected, inputText]);

  // Handle audio blob changes
  useEffect(() => {
    if (!connected || !audioBlob || !socketRef.current || processingRef.current) return;

    const processAudio = async () => {
      try {
        processingRef.current = true;
        
        const reader = new FileReader();
        reader.readAsDataURL(audioBlob);
        
        reader.onloadend = () => {
          const base64data = reader.result.split(',')[1];
          
          socketRef.current.emit('process_audio', {
            audio_data: base64data,
            format: audioBlob.type
          });
        };
      } catch (err) {
        setError('Failed to process audio');
        processingRef.current = false;
      }
    };
    
    processAudio();
  }, [connected, audioBlob]);

  return (
    <div className="mt-4 p-4 bg-gray-50 rounded-md border border-gray-200">
      <div className="flex items-center justify-between mb-2">
        <h6 className="text-sm font-semibold">Real-time Results:</h6>
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
              {connected ? (processing ? 'Processing...' : 'Waiting for input...') : 'Connecting...'}
            </div>
          )}
        </div>
      </div>
      
      <div className="mt-2 text-xs text-gray-500">
        <span>Real-time processing with Socket.IO</span>
      </div>
    </div>
  );
};

export default WebSocketResult; 