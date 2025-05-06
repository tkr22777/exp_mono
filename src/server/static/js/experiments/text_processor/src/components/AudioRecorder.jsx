/**
 * Audio Recorder Component
 * 
 * This component provides an interface for recording audio from the user's microphone,
 * visualizing audio levels, and preparing the audio for processing.
 * 
 * TODO: Complete End-to-End Audio AI Integration
 * ---------------------------------------------
 * Next steps for implementation:
 * 
 * 1. Backend API Integration:
 *    - Create a new endpoint in the Flask server to handle audio file uploads
 *    - Implement server-side processing for audio transcription using a speech-to-text service
 *    - Add support for direct audio processing with multimodal AI models
 * 
 * 2. Processing Options:
 *    - Add options for users to choose between transcription or direct audio analysis
 *    - Implement progress indicators for long-running audio processing tasks
 *    - Provide feedback on processing status and results
 * 
 * 3. Testing:
 *    - Test with various audio formats and recording conditions
 *    - Validate transcription accuracy across different languages and accents
 *    - Ensure proper error handling for all edge cases (permission denied, unsupported browsers, etc.)
 * 
 * 4. Performance Optimizations:
 *    - Implement audio compression before sending to backend
 *    - Add options for adjusting recording quality/duration
 *    - Consider adding WebSocket support for real-time processing
 */

import React, { useState, useRef, useEffect } from 'react';

const AudioRecorder = ({ onAudioCaptured }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  const [permission, setPermission] = useState(false);
  const [error, setError] = useState(null);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioStreamRef = useRef(null);
  const timerRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const dataArrayRef = useRef(null);
  const animationFrameRef = useRef(null);

  // Request microphone permission on component mount
  useEffect(() => {
    const getMicrophonePermission = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        setPermission(true);
        audioStreamRef.current = stream;
        
        // Set up audio analysis
        audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
        analyserRef.current = audioContextRef.current.createAnalyser();
        const source = audioContextRef.current.createMediaStreamSource(stream);
        source.connect(analyserRef.current);
        analyserRef.current.fftSize = 256;
        const bufferLength = analyserRef.current.frequencyBinCount;
        dataArrayRef.current = new Uint8Array(bufferLength);
      } catch (err) {
        setError("Please allow microphone access to record audio.");
        console.error("Error accessing microphone:", err);
      }
    };

    getMicrophonePermission();

    // Clean up on unmount
    return () => {
      if (audioStreamRef.current) {
        audioStreamRef.current.getTracks().forEach(track => track.stop());
      }
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, []);

  // Analyze audio levels while recording
  const updateAudioLevel = () => {
    if (!analyserRef.current || !dataArrayRef.current) return;
    
    analyserRef.current.getByteFrequencyData(dataArrayRef.current);
    const average = dataArrayRef.current.reduce((acc, val) => acc + val, 0) / dataArrayRef.current.length;
    setAudioLevel(average);
    
    if (isRecording) {
      animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
    }
  };

  const startRecording = () => {
    if (!permission) {
      setError("Microphone permission is required");
      return;
    }

    audioChunksRef.current = [];
    
    const options = { mimeType: 'audio/webm' };
    try {
      mediaRecorderRef.current = new MediaRecorder(audioStreamRef.current, options);
    } catch (e) {
      console.error('MediaRecorder error:', e);
      setError("Recording is not supported in this browser");
      return;
    }

    mediaRecorderRef.current.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunksRef.current.push(event.data);
      }
    };

    mediaRecorderRef.current.onstop = () => {
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      const audioUrl = URL.createObjectURL(audioBlob);
      setAudioBlob(audioBlob);
      setAudioUrl(audioUrl);
      if (onAudioCaptured) {
        onAudioCaptured(audioBlob, audioUrl);
      }
    };

    // Start recording
    mediaRecorderRef.current.start();
    setIsRecording(true);
    setError(null);
    
    // Start the recording timer
    let seconds = 0;
    timerRef.current = setInterval(() => {
      seconds++;
      setRecordingTime(seconds);
    }, 1000);

    // Start audio level visualization
    updateAudioLevel();
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      // Stop the timer
      clearInterval(timerRef.current);
      
      // Stop the audio level visualization
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    }
  };

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = time % 60;
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  // TODO: Add backend processing functionality
  const processAudioWithAI = () => {
    if (!audioBlob) {
      setError("No audio to process");
      return;
    }
    
    console.log("TODO: Process audio with AI model");
    // This would be implemented once backend audio processing is set up
  };

  return (
    <div className="mb-6 p-4 bg-white border border-gray-200 rounded-lg shadow-sm">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">Audio Input</h2>
      
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-300 text-red-700 rounded-md text-sm">
          {error}
        </div>
      )}
      
      <div className="flex items-center space-x-4 mb-4">
        {!isRecording ? (
          <button
            onClick={startRecording}
            disabled={!permission}
            className={`flex items-center px-4 py-2 rounded-md ${
              permission ? 'bg-red-600 hover:bg-red-700 text-white' : 'bg-gray-300 text-gray-600 cursor-not-allowed'
            }`}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <circle cx="10" cy="10" r="6" />
            </svg>
            Record
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="flex items-center px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <rect x="6" y="6" width="8" height="8" />
            </svg>
            Stop
          </button>
        )}
        
        {audioUrl && (
          <audio controls className="h-10" src={audioUrl}>
            Your browser does not support the audio element.
          </audio>
        )}
        
        {audioBlob && (
          <button
            onClick={processAudioWithAI}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md"
          >
            Process with AI (TODO)
          </button>
        )}
      </div>
      
      {isRecording && (
        <div className="mb-4">
          <div className="flex items-center">
            <div className="animate-pulse mr-2">
              <div className="h-3 w-3 bg-red-500 rounded-full"></div>
            </div>
            <span className="text-sm font-medium">Recording: {formatTime(recordingTime)}</span>
          </div>
          
          <div className="mt-2 h-6 w-full bg-gray-200 rounded-full overflow-hidden">
            <div 
              className="h-full bg-red-600 transition-all duration-300 ease-in-out"
              style={{ width: `${Math.min(audioLevel / 2, 100)}%` }}
            ></div>
          </div>
        </div>
      )}
      
      <div className="text-xs text-gray-500 mt-2">
        {audioBlob 
          ? `Recorded audio: ${(audioBlob.size / 1024).toFixed(1)} KB` 
          : "No audio recorded yet"}
      </div>
    </div>
  );
};

export default AudioRecorder; 