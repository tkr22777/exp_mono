import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import ToolCard from './ToolCard';
import ResultDisplay from './ResultDisplay';

const MCPServerExplorer = () => {
    const [tools, setTools] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [results, setResults] = useState([]);
    const [socket, setSocket] = useState(null);
    const [processingTool, setProcessingTool] = useState(null);

    // Get configuration from window object
    const config = window.experimentConfig || {
        debounceDelayMs: 300,
        maxTextLength: 1000,
        availableTools: []
    };

    useEffect(() => {
        // Initialize Socket.IO connection
        const newSocket = io();
        setSocket(newSocket);

        // Set up Socket.IO event listeners
        newSocket.on('mcp_tools_list', (data) => {
            if (data.success) {
                setTools(data.tools);
                setLoading(false);
            } else {
                setError('Failed to load tools');
                setLoading(false);
            }
        });

        newSocket.on('mcp_tool_result', (data) => {
            setResults(prev => [data, ...prev]);
            setProcessingTool(null);
        });

        newSocket.on('mcp_processing_start', (data) => {
            setProcessingTool(data.tool_name);
        });

        newSocket.on('mcp_error', (data) => {
            setError(data.message);
            setProcessingTool(null);
        });

        // Request tools list
        newSocket.emit('mcp_get_tools');

        // Cleanup on unmount
        return () => newSocket.close();
    }, []);

    const callTool = async (toolName, args) => {
        setError(null);
        
        if (socket) {
            // Use Socket.IO for real-time updates
            socket.emit('mcp_call_tool', {
                tool_name: toolName,
                arguments: args
            });
        } else {
            // Fallback to HTTP API
            try {
                setProcessingTool(toolName);
                const response = await fetch('/experiments/mcp-server/api/call-tool', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        tool_name: toolName,
                        arguments: args
                    })
                });

                const data = await response.json();
                
                if (data.success) {
                    setResults(prev => [{
                        tool_name: toolName,
                        arguments: args,
                        result: data.result,
                        success: true,
                        timestamp: new Date().toISOString()
                    }, ...prev]);
                } else {
                    setError(data.error);
                }
            } catch (err) {
                setError(`Network error: ${err.message}`);
            } finally {
                setProcessingTool(null);
            }
        }
    };

    const clearResults = () => {
        setResults([]);
        setError(null);
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                <span className="ml-3 text-gray-600">Loading MCP tools...</span>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex justify-between items-center">
                    <div>
                        <h2 className="text-xl font-semibold text-gray-800">Available MCP Tools</h2>
                        <p className="text-gray-600 mt-1">
                            {tools.length} tools available • Click on a tool to test it
                        </p>
                    </div>
                    {results.length > 0 && (
                        <button
                            onClick={clearResults}
                            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
                        >
                            Clear Results
                        </button>
                    )}
                </div>
            </div>

            {/* Error Display */}
            {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div className="flex">
                        <div className="flex-shrink-0">
                            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                            </svg>
                        </div>
                        <div className="ml-3">
                            <h3 className="text-sm font-medium text-red-800">Error</h3>
                            <div className="mt-2 text-sm text-red-700">{error}</div>
                        </div>
                    </div>
                </div>
            )}

            {/* Tools Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {tools.map((tool) => (
                    <ToolCard
                        key={tool.name}
                        tool={tool}
                        onCall={callTool}
                        isProcessing={processingTool === tool.name}
                        config={config}
                    />
                ))}
            </div>

            {/* Results */}
            {results.length > 0 && (
                <div className="bg-white rounded-lg shadow-sm">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h3 className="text-lg font-medium text-gray-900">Recent Results</h3>
                        <p className="text-sm text-gray-600 mt-1">
                            Latest tool execution results
                        </p>
                    </div>
                    <div className="p-6 space-y-4">
                        {results.map((result, index) => (
                            <ResultDisplay key={index} result={result} />
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default MCPServerExplorer; 