import React, { useState } from 'react';
import { Terminal, Send, Server, Network } from 'lucide-react';

export const McpSandbox: React.FC = () => {
  const [transport, setTransport] = useState<'stdio' | 'streamable-http'>('stdio');
  const [selectedMethod, setSelectedMethod] = useState<string>('tools/list');
  const [activePayload, setActivePayload] = useState<string>(
    JSON.stringify({ jsonrpc: '2.0', id: 101, method: 'tools/list', params: {} }, null, 2)
  );

  const [responseLog, setResponseLog] = useState<string>(
    JSON.stringify({
      jsonrpc: '2.0',
      id: 101,
      result: {
        tools: [
          {
            name: 'execute_sql_query',
            description: 'Executes read-only PostgreSQL query on production DB',
            inputSchema: {
              type: 'object',
              properties: {
                sql: { type: 'string', description: 'SQL SELECT query' }
              },
              required: ['sql']
            }
          },
          {
            name: 'read_filesystem_resource',
            description: 'Reads dynamic system log or context file',
            inputSchema: {
              type: 'object',
              properties: {
                path: { type: 'string' }
              }
            }
          }
        ]
      }
    }, null, 2)
  );

  const handleSelectMethod = (method: string) => {
    setSelectedMethod(method);
    if (method === 'tools/list') {
      setActivePayload(JSON.stringify({ jsonrpc: '2.0', id: 102, method: 'tools/list', params: {} }, null, 2));
      setResponseLog(JSON.stringify({
        jsonrpc: '2.0',
        id: 102,
        result: {
          tools: [
            { name: 'execute_sql_query', description: 'PostgreSQL read execution' },
            { name: 'read_filesystem_resource', description: 'Local context reader' }
          ]
        }
      }, null, 2));
    } else if (method === 'tools/call') {
      setActivePayload(JSON.stringify({
        jsonrpc: '2.0',
        id: 103,
        method: 'tools/call',
        params: {
          name: 'execute_sql_query',
          arguments: { sql: 'SELECT count(*) FROM users;' }
        }
      }, null, 2));
      setResponseLog(JSON.stringify({
        jsonrpc: '2.0',
        id: 103,
        result: {
          content: [
            { type: 'text', text: '{"count": 1420}' }
          ],
          isError: false
        }
      }, null, 2));
    } else if (method === 'resources/read') {
      setActivePayload(JSON.stringify({
        jsonrpc: '2.0',
        id: 104,
        method: 'resources/read',
        params: { uri: 'config://app/database_status' }
      }, null, 2));
      setResponseLog(JSON.stringify({
        jsonrpc: '2.0',
        id: 104,
        result: {
          contents: [
            { uri: 'config://app/database_status', mimeType: 'text/plain', text: 'Pool Status: HEALTHY | Connections: 14/50' }
          ]
        }
      }, null, 2));
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-3xl p-6 md:p-8 shadow-sm my-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 pb-6 border-b border-slate-100">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-violet-50 text-violet-700 rounded-full text-xs font-bold uppercase tracking-wider mb-2">
            <Server className="w-3.5 h-3.5 text-violet-600" />
            Model Context Protocol (MCP) JSON-RPC Inspector
          </div>
          <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            stdio vs Streamable HTTP Message Frames
          </h3>
          <p className="text-sm text-slate-500 mt-1">
            Test Anthropic MCP tool schemas, resource readers, and JSON-RPC 2.0 transport frames.
          </p>
        </div>

        {/* Transport Selector */}
        <div className="flex bg-slate-100 p-1 rounded-2xl border border-slate-200 self-start">
          <button
            onClick={() => setTransport('stdio')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${
              transport === 'stdio'
                ? 'bg-violet-600 text-white shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            stdio (Subprocess IPC)
          </button>
          <button
            onClick={() => setTransport('streamable-http')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${
              transport === 'streamable-http'
                ? 'bg-violet-600 text-white shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Streamable HTTP (Remote)
          </button>
        </div>
      </div>

      {/* Method Buttons */}
      <div className="flex flex-wrap items-center gap-2 mb-6">
        <span className="text-xs font-bold text-slate-700 uppercase tracking-wider mr-2">JSON-RPC Method:</span>
        <button
          onClick={() => handleSelectMethod('tools/list')}
          className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
            selectedMethod === 'tools/list' ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
          }`}
        >
          tools/list
        </button>
        <button
          onClick={() => handleSelectMethod('tools/call')}
          className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
            selectedMethod === 'tools/call' ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
          }`}
        >
          tools/call
        </button>
        <button
          onClick={() => handleSelectMethod('resources/read')}
          className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
            selectedMethod === 'resources/read' ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
          }`}
        >
          resources/read
        </button>
      </div>

      {/* JSON-RPC Request & Response Code Explorer */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Request Frame */}
        <div className="bg-slate-950 rounded-2xl p-4 border border-slate-800">
          <div className="flex justify-between items-center mb-2 pb-2 border-b border-slate-800 text-slate-400 text-xs">
            <span className="font-mono text-violet-400 font-bold flex items-center gap-1.5">
              <Send className="w-3.5 h-3.5" /> Client JSON-RPC Request
            </span>
            <span className="text-[10px] uppercase font-mono bg-violet-950 text-violet-300 px-2 py-0.5 rounded">
              {transport === 'stdio' ? 'stdin pipe' : 'HTTP POST /mcp'}
            </span>
          </div>
          <pre className="p-3 bg-slate-900/80 rounded-xl font-mono text-xs text-blue-300 overflow-x-auto leading-relaxed border border-slate-800">
            {activePayload}
          </pre>
        </div>

        {/* Response Frame */}
        <div className="bg-slate-950 rounded-2xl p-4 border border-slate-800">
          <div className="flex justify-between items-center mb-2 pb-2 border-b border-slate-800 text-slate-400 text-xs">
            <span className="font-mono text-emerald-400 font-bold flex items-center gap-1.5">
              <Terminal className="w-3.5 h-3.5" /> MCP Server Response Frame
            </span>
            <span className="text-[10px] uppercase font-mono bg-emerald-950 text-emerald-300 px-2 py-0.5 rounded">
              {transport === 'stdio' ? 'stdout stream' : 'HTTP response / optional event stream'}
            </span>
          </div>
          <pre className="p-3 bg-slate-900/80 rounded-xl font-mono text-xs text-emerald-400 overflow-x-auto leading-relaxed border border-slate-800">
            {responseLog}
          </pre>
        </div>
      </div>
      <p className="mt-4 text-[11px] text-slate-500">Legacy HTTP+SSE is deprecated and should be retained only for backward compatibility. New remote MCP integrations should use Streamable HTTP.</p>
    </div>
  );
};
