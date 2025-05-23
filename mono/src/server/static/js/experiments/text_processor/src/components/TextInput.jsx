import React, { useState, useEffect } from 'react';

const TextInput = ({ value, onChange, onKeyPress, maxLength, disabled, placeholder }) => {
  const [charCount, setCharCount] = useState(value.length);

  useEffect(() => {
    setCharCount(value.length);
  }, [value]);

  const handleChange = (e) => {
    onChange(e.target.value);
  };

  const handleKeyPress = (e) => {
    if (onKeyPress) {
      onKeyPress(e);
    }
  };

  return (
    <div className="mb-4">
      <label htmlFor="text-input" className="block text-gray-700 text-sm font-medium mb-2">
        Text Input
      </label>
      <textarea 
        id="text-input" 
        className={`w-full px-3 py-2 text-gray-700 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
          disabled ? 'bg-gray-100 cursor-not-allowed' : ''
        }`}
        rows="5" 
        placeholder={placeholder || "Start typing here or use the audio recorder below..."} 
        maxLength={maxLength}
        value={value}
        onChange={handleChange}
        onKeyPress={handleKeyPress}
        disabled={disabled}
      />
      <div className="mt-1 text-xs text-gray-500 flex justify-between">
        <span>
          {charCount} characters
        </span>
        {disabled && <span className="text-blue-600">Input disabled during transcription...</span>}
      </div>
    </div>
  );
};

export default TextInput; 