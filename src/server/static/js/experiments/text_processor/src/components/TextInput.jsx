import React, { useState, useEffect } from 'react';

const TextInput = ({ value, onChange, maxLength }) => {
  const [charCount, setCharCount] = useState(value.length);

  useEffect(() => {
    setCharCount(value.length);
  }, [value]);

  const handleChange = (e) => {
    onChange(e.target.value);
  };

  return (
    <div className="mb-4">
      <label htmlFor="text-input" className="block text-gray-700 text-sm font-medium mb-2">
        Text Input
      </label>
      <textarea 
        id="text-input" 
        className="w-full px-3 py-2 text-gray-700 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
        rows="5" 
        placeholder="Start typing here..." 
        maxLength={maxLength}
        value={value}
        onChange={handleChange}
      />
      <div className="mt-1 text-xs text-gray-500">
        {charCount} characters
      </div>
    </div>
  );
};

export default TextInput; 