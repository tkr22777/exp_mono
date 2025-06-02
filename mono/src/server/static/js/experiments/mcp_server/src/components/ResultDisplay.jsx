import React, { useState } from 'react';

const ResultDisplay = ({ result }) => {
    const [expanded, setExpanded] = useState(false);

    const formatTimestamp = (timestamp) => {
        if (!timestamp) return 'Just now';
        return new Date(timestamp).toLocaleTimeString();
    };

    const getStatusIcon = (success) => {
        if (success) {
            return (
                <svg className="h-5 w-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            );
        } else {
            return (
                <svg className="h-5 w-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            );
        }
    };

    const renderResult = () => {
        if (typeof result.result === 'object') {
            return (
                <div className="space-y-2">
                    {Object.entries(result.result).map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                            <span className="font-medium text-gray-700">{key}:</span>
                            <span className="text-gray-900">
                                {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                            </span>
                        </div>
                    ))}
                </div>
            );
        } else {
            return (
                <div className="text-gray-900">
                    {String(result.result)}
                </div>
            );
        }
    };

    const renderArguments = () => {
        if (!result.arguments || Object.keys(result.arguments).length === 0) {
            return <span className="text-gray-500 italic">No arguments</span>;
        }

        return (
            <div className="space-y-1">
                {Object.entries(result.arguments).map(([key, value]) => (
                    <div key={key} className="text-sm">
                        <span className="font-medium text-gray-600">{key}:</span>{' '}
                        <span className="text-gray-800">{String(value)}</span>
                    </div>
                ))}
            </div>
        );
    };

    return (
        <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
            <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                    {getStatusIcon(result.success)}
                    <div>
                        <h4 className="font-medium text-gray-900">{result.tool_name}</h4>
                        <p className="text-sm text-gray-500">
                            {formatTimestamp(result.timestamp)}
                        </p>
                    </div>
                </div>
                <button
                    onClick={() => setExpanded(!expanded)}
                    className="text-gray-400 hover:text-gray-600"
                >
                    <svg 
                        className={`h-5 w-5 transform transition-transform ${expanded ? 'rotate-180' : ''}`} 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                    >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                </button>
            </div>

            {expanded && (
                <div className="mt-4 space-y-4">
                    {/* Arguments */}
                    <div>
                        <h5 className="text-sm font-medium text-gray-700 mb-2">Arguments:</h5>
                        <div className="bg-white p-3 rounded border">
                            {renderArguments()}
                        </div>
                    </div>

                    {/* Result */}
                    <div>
                        <h5 className="text-sm font-medium text-gray-700 mb-2">Result:</h5>
                        <div className="bg-white p-3 rounded border">
                            {renderResult()}
                        </div>
                    </div>

                    {/* Raw JSON (for debugging) */}
                    <details className="text-xs">
                        <summary className="cursor-pointer text-gray-500 hover:text-gray-700">
                            Show raw JSON
                        </summary>
                        <pre className="mt-2 bg-gray-100 p-2 rounded overflow-x-auto text-xs">
                            {JSON.stringify(result, null, 2)}
                        </pre>
                    </details>
                </div>
            )}
        </div>
    );
};

export default ResultDisplay; 