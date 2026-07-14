import { useState, useEffect } from "react";
import { API_BASE } from "../lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Repeat, Play, Info, AlertCircle, CheckCircle2 } from "lucide-react";

interface Loop {
    id: string;
    name: string;
    description: string;
    tools: string[];
    status: string;
}

export function Loops() {
    const [loops, setLoops] = useState<Loop[]>([]);
    const [activeLoop, setActiveLoop] = useState<string | null>(null);

    useEffect(() => {
        fetch(API_BASE + "/api/v1/intelligence/loops")
            .then((r) => (r.ok ? r.json() : { loops: [] }))
            .then((d) => setLoops(d?.loops ?? []))
            .catch(() => setLoops([]));
    }, []);

    const runLoop = (id: string) => {
        setActiveLoop(id);
        // Simulation of running a loop
        setTimeout(() => setActiveLoop(null), 3000);
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold bg-gradient-to-r from-orange-400 to-red-500 bg-clip-text text-transparent">
                        Agentic Loops
                    </h2>
                    <p className="text-slate-400">Meta-Actions · Autonomous Workflows · Sampling Sessions</p>
                </div>
                <div className="flex items-center gap-2">
                    <div className="flex -space-x-2">
                        {[1, 2, 3].map(i => (
                            <div key={i} className="h-8 w-8 rounded-full border-2 border-slate-950 bg-slate-800 flex items-center justify-center">
                                <span className="text-[10px] font-bold text-slate-400">A{i}</span>
                            </div>
                        ))}
                    </div>
                    <span className="text-xs text-slate-500 font-mono ml-2">3 Agents Sampling</span>
                </div>
            </div>

            <div className="grid gap-6">
                {loops.map((loop) => (
                    <Card key={loop.id} className={`border-slate-800 bg-slate-950/40 backdrop-blur-xl transition-all ${activeLoop === loop.id ? 'ring-2 ring-orange-500/50 border-orange-500/30' : ''}`}>
                        <CardHeader className="flex flex-row items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className={`p-2 rounded-lg ${activeLoop === loop.id ? 'bg-orange-500/20 text-orange-400 animate-spin-slow' : 'bg-slate-800 text-slate-400'}`}>
                                    <Repeat className="h-5 w-5" />
                                </div>
                                <div>
                                    <CardTitle className="text-lg text-white">{loop.name}</CardTitle>
                                    <p className="text-xs text-slate-500">{loop.description}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                <Badge variant="outline" className={`${loop.status === 'active' ? 'border-emerald-500/20 text-emerald-400' :
                                        loop.status === 'ready' ? 'border-blue-500/20 text-blue-400' : 'border-slate-700 text-slate-500'
                                    }`}>
                                    {loop.status.toUpperCase()}
                                </Badge>
                                <button
                                    onClick={() => runLoop(loop.id)}
                                    disabled={activeLoop !== null}
                                    className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${activeLoop === loop.id ? 'bg-orange-500 text-white shadow-lg shadow-orange-500/20' :
                                            'bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-50'
                                        }`}
                                >
                                    <Play className={`h-3 w-3 ${activeLoop === loop.id ? 'fill-current' : ''}`} />
                                    {activeLoop === loop.id ? "RUNNING..." : "EXECUTE LOOP"}
                                </button>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                <div>
                                    <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2 flex items-center gap-1">
                                        <Info className="h-3 w-3" /> Tool Chain
                                    </div>
                                    <div className="flex flex-wrap gap-2">
                                        {loop.tools.map((tool, idx) => (
                                            <div key={tool} className="flex items-center">
                                                <Badge variant="secondary" className="bg-slate-900 border-slate-800 text-slate-300 font-mono text-[10px]">
                                                    {tool}
                                                </Badge>
                                                {idx < loop.tools.length - 1 && (
                                                    <div className="mx-2 h-px w-4 bg-slate-800" />
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900/50 border border-slate-800/50">
                                    <div className="flex items-center gap-3">
                                        {loop.status === 'active' ? (
                                            <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                                        ) : (
                                            <AlertCircle className="h-4 w-4 text-amber-500" />
                                        )}
                                        <span className="text-xs text-slate-400">
                                            {loop.status === 'active' ? "Stability Index: 0.98" : "Requires Agent Approval"}
                                        </span>
                                    </div>
                                    <span className="text-[10px] font-mono text-slate-600 uppercase">BlackFang Compatible</span>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl border-dashed">
                <CardContent className="py-8 flex flex-col items-center justify-center text-center opacity-60">
                    <div className="h-12 w-12 rounded-full bg-slate-800 flex items-center justify-center mb-4">
                        <Repeat className="h-6 w-6 text-slate-400" />
                    </div>
                    <h3 className="text-sm font-bold text-white mb-1">Define New Loop</h3>
                    <p className="text-xs text-slate-500">Register custom agentic behaviors via the Portmanteau Engine.</p>
                </CardContent>
            </Card>
        </div>
    );
}
