import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Wrench, Play, Terminal, Info, AlertTriangle } from "lucide-react";

interface ToolParameter {
    name: string;
    type: string;
    description?: string;
    required: boolean;
}

interface Tool {
    name: string;
    description: string;
    parameters: ToolParameter[];
}

export function Tools() {
    const [tools, setTools] = useState<Tool[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchTools();
    }, []);

    const fetchTools = async () => {
        try {
            setLoading(true);
            const response = await fetch('http://localhost:10793/api/v1/tools/');
            if (!response.ok) throw new Error('Failed to fetch tools');
            const data = await response.json();
            setTools(data);
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Tools Hub</h2>
                    <p className="text-slate-400">Real-time MCP tool orchestration</p>
                </div>
                <Button variant="outline" onClick={fetchTools} disabled={loading} className="border-slate-800 bg-slate-900/50 hover:bg-slate-800 text-slate-200">
                    <Wrench className="mr-2 h-4 w-4" />
                    Refresh Inventory
                </Button>
            </div>

            {error && (
                <Card className="border-red-900/50 bg-red-950/20">
                    <CardContent className="pt-6 flex items-center gap-3 text-red-400">
                        <AlertTriangle className="h-5 w-5" />
                        <p>{error}</p>
                    </CardContent>
                </Card>
            )}

            <div className="grid gap-6">
                {loading ? (
                    <div className="py-12 flex flex-col items-center justify-center text-slate-500">
                        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
                        <p>Syncing tool registry...</p>
                    </div>
                ) : tools.map((tool) => (
                    <Card key={tool.name} className="border-slate-800 bg-slate-950/50 hover:border-slate-700 transition-colors">
                        <CardHeader className="flex flex-row items-start justify-between">
                            <div className="space-y-1">
                                <div className="flex items-center gap-3">
                                    <CardTitle className="text-lg text-white group flex items-center gap-2">
                                        <Terminal className="h-4 w-4 text-blue-500" />
                                        {tool.name}
                                    </CardTitle>
                                    <Badge variant="secondary" className="bg-slate-800 text-slate-400 text-[10px] uppercase font-bold tracking-wider">
                                        FastMCP 2.14.3
                                    </Badge>
                                </div>
                                <CardDescription className="text-slate-400 max-w-2xl">
                                    {tool.description}
                                </CardDescription>
                            </div>
                            <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white border-0">
                                <Play className="mr-2 h-3.5 w-3.5" />
                                Execute
                            </Button>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                <h4 className="text-xs font-bold uppercase tracking-widest text-slate-500 flex items-center gap-2">
                                    <Info className="h-3 w-3" />
                                    Parameters
                                </h4>
                                <div className="grid gap-2">
                                    {tool.parameters.length > 0 ? tool.parameters.map((param) => (
                                        <div key={param.name} className="flex items-center justify-between p-2 rounded bg-slate-900/50 border border-slate-800/50 group hover:border-slate-700 transition-colors">
                                            <div className="flex items-baseline gap-3">
                                                <span className="text-sm font-mono text-emerald-400">{param.name}</span>
                                                <span className="text-[10px] font-bold text-slate-600 uppercase tracking-tighter">{param.type}</span>
                                                <span className="text-xs text-slate-500 italic">{param.description}</span>
                                            </div>
                                            {param.required && (
                                                <Badge className="bg-red-500/10 text-red-500 border-red-500/20 text-[10px]">REQUIRED</Badge>
                                            )}
                                        </div>
                                    )) : (
                                        <p className="text-xs text-slate-600 italic">No parameters required</p>
                                    )}
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    );
}
