import React from 'react';
import { createRoot } from 'react-dom/client';
import TextProcessor from './components/TextProcessor';

// Get configuration from global variable set in the HTML
const experimentConfig = window.experimentConfig || {
  debounceDelayMs: 300,
  defaultText: '',
  maxTextLength: 5000
};

// Mount React app
const container = document.getElementById('react-text-processor');
const root = createRoot(container);
root.render(<TextProcessor config={experimentConfig} />); 