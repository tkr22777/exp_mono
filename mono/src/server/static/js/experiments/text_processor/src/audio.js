import React from 'react';
import ReactDOM from 'react-dom/client';
import AudioProcessor from './components/AudioProcessor';

// Get the React root element
const container = document.getElementById('react-audio-processor');
const root = ReactDOM.createRoot(container);

// Get the experiment configuration
const config = window.experimentConfig || {};

// Render the AudioProcessor component
root.render(
  <React.StrictMode>
    <AudioProcessor config={config} />
  </React.StrictMode>
); 