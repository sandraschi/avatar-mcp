import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Wrench, Play, Terminal, Info, AlertTriangle, ChevronDown, ChevronUp } from "lucide-react";

interface ToolParameter {
    name: string;
    type?: string;
    description?: string;
    required?: boolean;
}

interface Tool {
    name: string;
    description: string;
    parameters?: Record<string, unknown> | ToolParameter[];
}

function normalizeParams(tool: Tool): ToolParameter[] {
    const p = tool.parameters;
    if (!p) return [];
    if (Array.isArray(p)) return p as ToolParameter[];
    const schema = p as { properties?: Record<string, { type?: string; description?: string }>; required?: string[] };
    if (!schema.properties) return [];
    return Object.entries(schema.properties).map(([name, info]) => ({
        name,
        type: info?.type ?? "string",
        description: info?.description,
        required: Array.isArray(schema.required) && schema.required.includes(name),
    }));
}

export function Tools() {
    const [tools, setTools] = useState<Tool[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [executing, setExecuting] = useState<string | null>(null);
    const [result, setResult] = useState<{ tool: string; status: string; data: unknown } | null>(null);
    const [expandRun, setExpandRun] = useState<string | null>(null);
    const [argsJson, setArgsJson] = useState<Record<string, string>>({});

    useEffect(() => {
        fetchTools();
    }, []);

    const fetchTools = async () => {
        try {
            setLoading(true);
            const response = await fetch('/api/v1/tools');
            if (!response.ok) throw new Error('Failed to fetch tools');
            const data = await response.json();
            setTools(Array.isArray(data) ? data : []);
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        } finally {
            setLoading(false);
        }
    };

    const runTool = async (toolName: string) => {
        const raw = argsJson[toolName] ?? '{}';
        let args: Record<string, unknown>;
        try {
            args = JSON.parse(raw);
        } catch {
            setResult({ tool: toolName, status: 'error', data: 'Invalid JSON for arguments' });
            return;
        }
        setExecuting(toolName);
        setResult(null);
        try {
            const response = await fetch('/api/v1/tools/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tool_name: toolName, arguments: args }),
            });
            const data = await response.json().catch(() => ({}));
            setResult({
                tool: toolName,
                status: response.ok ? (data.status ?? 'success') : 'error',
                data: data.result ?? data.detail ?? data,
            });
        } catch (err) {
            setResult({ tool: toolName, status: 'error', data: String(err) });
        } finally {
            setExecuting(null);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Tools Hub</h2>
                    <p className="text-slate-400">List and run MCP tools via the backend bridge</p>
                </div>
                <Button variant="outline" onClick={fetchTools} disabled={loading} className="border-slate-800 bg-slate-900/50 hover:bg-slate-800 text-slate-200">
                    <Wrench className="mr-2 h-4 w-4" />
                    Refresh
                </Button>
            </div>

            {error && (
                <Card className="border-red-900/50 bg-red-950/20">
                    <CardContent className="pt-6 flex items-center gap-3 text-red-400">
                        <AlertTriangle className="h-5 w-5" />
                        <p>{error}. Ensure backend is running (web_sota/start.ps1).</p>
                    </CardContent>
                </Card>
            )}

            {result && (
                <Card className="border-slate-700 bg-slate-900/50">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm text-slate-300">Last run: {result.tool}</CardTitle>
                        <Badge className={result.status === 'success' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}>{result.status}</Badge>
                    </CardHeader>
                    <CardContent>
                        <pre className="text-xs text-slate-400 overflow-auto max-h-48 rounded bg-slate-950 p-3">{typeof result.data === 'string' ? result.data : JSON.stringify(result.data, null, 2)}</pre>
                    </CardContent>
                </Card>
            )}

            <div className="grid gap-6">
                {loading ? (
                    <div className="py-12 flex flex-col items-center justify-center text-slate-500">
                        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mb-4" />
                        <p>Loading tools from MCP server...</p>
                    </div>
                ) : tools.map((tool) => {
                    const params = normalizeParams(tool);
                    const isExpanded = expandRun === tool.name;
                    return (
                        <Card key={tool.name} className="border-slate-800 bg-slate-950/50 hover:border-slate-700 transition-colors">
                            <CardHeader className="flex flex-row items-start justify-between">
                                <div className="space-y-1">
                                    <div className="flex items-center gap-3">
                                        <CardTitle className="text-lg text-white flex items-center gap-2">
                                            <Terminal className="h-4 w-4 text-blue-500" />
                                            {tool.name}
                                        </CardTitle>
                                        <Badge variant="secondary" className="bg-slate-800 text-slate-400 text-[10px] uppercase font-bold tracking-wider">FastMCP 3</Badge>
                                    </div>
                                    <CardDescription className="text-slate-400 max-w-2xl">{tool.description}</CardDescription>
                                </div>
                                <Button
                                    size="sm"
                                    className="bg-blue-600 hover:bg-blue-700 text-white border-0"
                                    onClick={() => setExpandRun(isExpanded ? null : tool.name)}
                                    disabled={executing !== null}
                                >
                                    {isExpanded ? <ChevronUp className="h-3.5 w-3.5 mr-1" /> : <ChevronDown className="h-3.5 w-3.5 mr-1" />}
                                    Run
                                </Button>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    <h4 className="text-xs font-bold uppercase tracking-widest text-slate-500 flex items-center gap-2"><Info className="h-3 w-3" /> Parameters</h4>
                                    <div className="grid gap-2">
                                        {params.length > 0 ? params.map((param) => (
                                            <div key={param.name} className="flex items-center justify-between p-2 rounded bg-slate-900/50 border border-slate-800/50">
                                                <div className="flex items-baseline gap-3">
                                                    <span className="text-sm font-mono text-emerald-400">{param.name}</span>
                                                    <span className="text-[10px] font-bold text-slate-600 uppercase">{param.type ?? 'any'}</span>
                                                    {param.description && <span className="text-xs text-slate-500 italic">{param.description}</span>}
                                                </div>
                                                {param.required && <Badge className="bg-red-500/10 text-red-500 border-red-500/20 text-[10px]">REQUIRED</Badge>}
                                            </div>
                                        )) : <p className="text-xs text-slate-600 italic">No parameters or optional only</p>}
                                    </div>
                                </div>
                                {isExpanded && (
                                    <div className="mt-4 pt-4 border-t border-slate-800">
                                        <label className="text-xs font-bold uppercase text-slate-500 block mb-2">Arguments (JSON)</label>
                                        <textarea
                                            className="w-full h-24 rounded bg-slate-950 border border-slate-700 text-slate-200 text-sm font-mono p-2"
                                            placeholder='{"operation": "list"}'
                                            value={argsJson[tool.name] ?? '{}'}
                                            onChange={(e) => setArgsJson((s) => ({ ...s, [tool.name]: e.target.value }))}
                                        />
                                        <Button className="mt-2 bg-emerald-600 hover:bg-emerald-700 text-white" onClick={() => runTool(tool.name)} disabled={executing !== null}>
                                            {executing === tool.name ? 'Running…' : <><Play className="h-3.5 w-3.5 mr-2" /> Execute</>}
                                        </Button>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    );
                })}
            </div>
        </div>
    );
}
