import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Cpu, Zap, Network, Bot, ShieldCheck } from "lucide-react";

interface TrifectaData {
    openfang: {
        status: string;
        telemetry: string;
        latency_ms: number;
    };
    avatarmcp_connectors: {
        status: string;
        active_portmanteaus: number;
        api_proxy: string;
    };
    blackfang_agents: {
        status: string;
        connected_agents: number;
        current_loop: string;
    };
}

export function Intelligence() {
    const [data, setData] = useState<TrifectaData | null>(null);

    useEffect(() => {
        fetch("http://127.0.0.1:10793/api/v1/intelligence/trifecta")
            .then(r => r.json())
            .then(setData)
            .catch(() => { });
    }, []);

    if (!data) return <div className="p-8 text-slate-500 font-mono">Loading Intelligence Matrix...</div>;

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-400 via-indigo-500 to-purple-600 bg-clip-text text-transparent">
                        Intelligence Hub
                    </h2>
                    <p className="text-slate-400">The Trifecta: OpenFang · Avatar-MCP · BlackFang</p>
                </div>
                <Badge variant="outline" className="border-indigo-500/20 text-indigo-400 px-4 py-1">
                    SOTA Synchronized
                </Badge>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* OpenFang */}
                <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl hover:border-blue-500/30 transition-all">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-blue-400">OpenFang (Robotics)</CardTitle>
                        <Cpu className="h-4 w-4 text-blue-400" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white capitalize">{data.openfang.status}</div>
                        <p className="text-xs text-slate-500 mt-1">Telemetry: {data.openfang.telemetry}</p>
                        <div className="mt-4 flex items-center gap-2">
                            <div className="h-1.5 flex-1 bg-slate-800 rounded-full overflow-hidden">
                                <div className="h-full bg-blue-500 w-[85%]" />
                            </div>
                            <span className="text-[10px] font-mono text-blue-400">{data.openfang.latency_ms}ms</span>
                        </div>
                    </CardContent>
                </Card>

                {/* Avatar-MCP */}
                <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl hover:border-emerald-500/30 transition-all">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-emerald-400">Avatar-MCP (Connectors)</CardTitle>
                        <Network className="h-4 w-4 text-emerald-400" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">{data.avatarmcp_connectors.active_portmanteaus} Portmanteaus</div>
                        <p className="text-xs text-slate-500 mt-1">API Proxy: {data.avatarmcp_connectors.api_proxy}</p>
                        <div className="mt-4 flex items-center gap-2 text-xs font-mono">
                            <ShieldCheck className="h-3 w-3 text-emerald-500" />
                            <span className="text-emerald-500">Secure Bridge Active</span>
                        </div>
                    </CardContent>
                </Card>

                {/* BlackFang */}
                <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl hover:border-purple-500/30 transition-all">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-purple-400">BlackFang (Agents)</CardTitle>
                        <Bot className="h-4 w-4 text-purple-400" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">{data.blackfang_agents.connected_agents} Agents</div>
                        <p className="text-xs text-slate-500 mt-1">Running: {data.blackfang_agents.current_loop}</p>
                        <div className="mt-4">
                            <Badge className="bg-purple-500/10 text-purple-400 border-purple-500/20 text-[10px]">
                                Agentic Sampling Enabled
                            </Badge>
                        </div>
                    </CardContent>
                </Card>
            </div>

            <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl border-l-4 border-l-cyan-500">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                        <Zap className="h-4 w-4 text-cyan-400" />
                        Intelligence Matrix
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="flex items-center justify-between p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/10">
                        <span className="text-xs text-emerald-400 font-bold">ARTIFACT PIPELINE</span>
                        <div className="flex items-center gap-2">
                            <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                            <span className="text-[10px] text-emerald-500 font-mono">HAWK-MODE ACTIVE</span>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="p-3 rounded-lg bg-slate-900/50 border border-slate-800">
                            <div className="text-[10px] text-slate-500 uppercase font-bold tracking-tighter">Landfalls Detected</div>
                            <div className="text-xl font-bold text-white font-mono mt-1">4 ACTIVE</div>
                        </div>
                        <div className="p-3 rounded-lg bg-slate-900/50 border border-slate-800">
                            <div className="text-[10px] text-slate-500 uppercase font-bold tracking-tighter">Pipeline Throughput</div>
                            <div className="text-xl font-bold text-cyan-400 font-mono mt-1">SOTA HIGH</div>
                        </div>
                        <div className="p-3 rounded-lg bg-slate-900/50 border border-slate-800">
                            <div className="text-[10px] text-slate-500 uppercase font-bold tracking-tighter">Watchdog Latency</div>
                            <div className="text-xl font-bold text-white font-mono mt-1">12ms</div>
                        </div>
                        <div className="p-3 rounded-lg bg-slate-900/50 border border-slate-800">
                            <div className="text-[10px] text-slate-500 uppercase font-bold tracking-tighter">Routing Engine</div>
                            <div className="text-xl font-bold text-emerald-400 font-mono mt-1">ENABLED</div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                        <Zap className="h-4 w-4 text-indigo-400" />
                        Intelligence Matrix Visualization
                    </CardTitle>
                </CardHeader>
                <CardContent className="h-64 flex items-center justify-center border-t border-slate-800/50">
                    <div className="relative w-full max-w-md h-full flex items-center justify-center">
                        {/* Simulated connection lines */}
                        <div className="absolute inset-0 flex items-center justify-center">
                            <div className="w-full h-px bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 opacity-20" />
                            <div className="h-full w-px bg-gradient-to-b from-blue-500 via-indigo-500 to-purple-500 opacity-20" />
                        </div>
                        <div className="grid grid-cols-2 gap-16 relative z-10">
                            <div className="flex flex-col items-center gap-2 p-4 rounded-2xl bg-blue-500/10 border border-blue-500/20">
                                <Cpu className="h-8 w-8 text-blue-500" />
                                <span className="text-[10px] font-bold text-blue-400 text-center">ROBOTICS LAYER</span>
                            </div>
                            <div className="flex flex-col items-center gap-2 p-4 rounded-2xl bg-purple-500/10 border border-purple-500/20">
                                <Bot className="h-8 w-8 text-purple-500" />
                                <span className="text-[10px] font-bold text-purple-400 text-center">AGENT LAYER</span>
                            </div>
                            <div className="col-span-2 flex flex-col items-center gap-2 p-4 rounded-2xl bg-indigo-500/10 border border-indigo-500/20">
                                <Network className="h-8 w-8 text-indigo-500" />
                                <span className="text-[10px] font-bold text-indigo-400 text-center">MCP CONNECTOR HUB</span>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
