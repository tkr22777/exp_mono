import React from 'react';

const ProcessedResult = ({ processedText, isLoading, error }) => {
  if (error) {
    return (
      <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
        <strong>Error:</strong> {error}
      </div>
    );
  }

  if (!processedText && !isLoading) {
    return null;
  }

  return (
    <div className="mt-4 p-4 bg-gray-50 rounded-md">
      <h6 className="text-sm font-semibold mb-2">Processed Result:</h6>
      
      {isLoading ? (
        <div className="flex items-center">
          <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full mr-2"></div>
          <span>Processing...</span>
        </div>
      ) : (
        <div className="p-3 bg-white border border-gray-200 rounded-md">
          {processedText}
        </div>
      )}
    </div>
  );
};

export default ProcessedResult; 