import React, { useState, useEffect, useRef } from 'react';
import { io } from 'socket.io-client';

/**
 * WebSocketResult Component - Displays calculator results using Socket.IO
 * Simplified to only show direct API responses
 */
const WebSocketResult = ({ inputText, audioBlob }) => {
  const [connected, setConnected] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [response, setResponse] = useState('');
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
      setResponse('');
    });

    socket.on('processing_update', (data) => {
      setResponse(prev => prev + data.chunk);
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
    
    // Send to server for processing
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
    <div className="mt-4 p-4 bg-gray-50 rounded-md">
      <div className="mb-2">
        <span className="text-sm font-semibold">Socket.IO Result</span>
        {!connected && <span className="ml-2 text-sm text-red-500">(Disconnected)</span>}
      </div>
      
      {error && (
        <div className="mb-4 p-2 bg-red-50 text-red-700 text-sm">
          {error}
        </div>
      )}
      
      <div className="bg-white border border-gray-200 rounded-md p-3 min-h-[100px] font-mono">
        {processing ? (
          <div className="text-gray-500">
            Processing...
          </div>
        ) : response ? (
          <div className="whitespace-pre-wrap text-green-600">
            {response}
          </div>
        ) : (
          <div className="text-gray-400 italic">
            Enter a number to start calculating...
          </div>
        )}
      </div>
    </div>
  );
};

export default WebSocketResult; 