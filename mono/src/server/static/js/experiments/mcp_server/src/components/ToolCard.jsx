import React, { useState } from 'react';

const ToolCard = ({ tool, onCall, isProcessing, config }) => {
    const [inputs, setInputs] = useState({});
    const [showAdvanced, setShowAdvanced] = useState(false);

    const handleInputChange = (key, value) => {
        setInputs(prev => ({
            ...prev,
            [key]: value
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onCall(tool.name, inputs);
    };

    const getToolIcon = (toolName) => {
        switch (toolName) {
            case 'calculate':
                return (
                    <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                );
            case 'text_stats':
                return (
                    <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                );
            case 'system_info':
                return (
                    <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                );
            case 'format_text':
                return (
                    <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h7" />
                    </svg>
                );
            default:
                return (
                    <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                );
        }
    };

    const renderInputFields = () => {
        if (tool.name === 'calculate') {
            return (
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Mathematical Expression
                    </label>
                    <input
                        type="text"
                        placeholder="e.g., 2 + 3 * 4"
                        value={inputs.expression || ''}
                        onChange={(e) => handleInputChange('expression', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>
            );
        } else if (tool.name === 'text_stats') {
            return (
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Text to Analyze
                    </label>
                    <textarea
                        placeholder="Enter text to analyze..."
                        value={inputs.text || ''}
                        onChange={(e) => handleInputChange('text', e.target.value)}
                        rows={3}
                        maxLength={config.maxTextLength}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                        {(inputs.text || '').length}/{config.maxTextLength} characters
                    </p>
                </div>
            );
        } else if (tool.name === 'format_text') {
            return (
                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Text to Format
                        </label>
                        <input
                            type="text"
                            placeholder="Enter text to format..."
                            value={inputs.text || ''}
                            onChange={(e) => handleInputChange('text', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Format Type
                        </label>
                        <select
                            value={inputs.format_type || 'title'}
                            onChange={(e) => handleInputChange('format_type', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="upper">UPPERCASE</option>
                            <option value="lower">lowercase</option>
                            <option value="title">Title Case</option>
                            <option value="capitalize">Capitalize</option>
                            <option value="swapcase">sWAPcASE</option>
                            <option value="reverse">esreveR</option>
                            <option value="strip">Strip Whitespace</option>
                        </select>
                    </div>
                </div>
            );
        } else if (tool.name === 'system_info') {
            return (
                <div className="text-center py-4">
                    <p className="text-gray-600">No input required for system information</p>
                </div>
            );
        }
        
        return null;
    };

    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                    <div className="flex-shrink-0 p-2 bg-blue-100 rounded-lg text-blue-600">
                        {getToolIcon(tool.name)}
                    </div>
                    <div className="ml-3">
                        <h3 className="text-lg font-medium text-gray-900">{tool.name}</h3>
                        <p className="text-sm text-gray-600">{tool.description}</p>
                    </div>
                </div>
                {showAdvanced && (
                    <button
                        onClick={() => setShowAdvanced(false)}
                        className="text-gray-400 hover:text-gray-600"
                    >
                        <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                )}
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
                {renderInputFields()}

                <div className="flex items-center justify-between pt-4">
                    <button
                        type="button"
                        onClick={() => setShowAdvanced(!showAdvanced)}
                        className="text-sm text-gray-500 hover:text-gray-700"
                    >
                        {showAdvanced ? 'Hide' : 'Show'} Details
                    </button>
                    
                    <button
                        type="submit"
                        disabled={isProcessing}
                        className={`px-4 py-2 rounded-md font-medium transition-colors ${
                            isProcessing
                                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                : 'bg-blue-600 text-white hover:bg-blue-700'
                        }`}
                    >
                        {isProcessing ? (
                            <div className="flex items-center">
                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                Processing...
                            </div>
                        ) : (
                            'Run Tool'
                        )}
                    </button>
                </div>
            </form>

            {showAdvanced && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Tool Schema</h4>
                    <pre className="text-xs bg-gray-50 p-3 rounded-md overflow-x-auto">
                        {JSON.stringify(tool.inputSchema, null, 2)}
                    </pre>
                </div>
            )}
        </div>
    );
};

export default ToolCard; 