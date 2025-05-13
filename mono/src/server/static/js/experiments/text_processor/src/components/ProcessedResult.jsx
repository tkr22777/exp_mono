import React from 'react';

const ProcessedResult = ({ response, isLoading, error }) => {
  if (error) {
    return (
      <div className="mt-4 p-2 bg-red-50 text-red-700">
        <strong>Error:</strong> {error}
      </div>
    );
  }

  if (!response && !isLoading) {
    return null;
  }

  return (
    <div className="mt-4 p-4 bg-gray-50 rounded-md">
      <div className="mb-2">
        <span className="text-sm font-semibold">HTTP Response</span>
      </div>
      
      {isLoading ? (
        <div className="p-2 text-gray-500">
          Processing...
        </div>
      ) : (
        <div className="bg-white border border-gray-200 p-3 rounded-md">
          <div className="mb-2">
            <strong>You: </strong>
            <span>[Input text]</span>
          </div>
          
          <div>
            <strong>AI: </strong>
            <span className="whitespace-pre-wrap">{response}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProcessedResult; 