import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, GitMerge, Box, Cpu, Shield, Zap } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface SystemStatus {
    active_avatars?: number;
    system_load_pct?: number;
    unity_engine?: string;
    vrchat_bridge?: string;
    osc_pipeline?: string;
}

export function Dashboard() {
    const [status, setStatus] = useState<SystemStatus>({
        active_avatars: 0,
        system_load_pct: 0,
        unity_engine: "loading...",
        vrchat_bridge: "loading...",
        osc_pipeline: "loading...",
    });

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const response = await fetch("/api/v1/status");
                if (response.ok) {
                    const data = await response.json();
                    setStatus(data);
                }
            } catch (error) {
                console.error("Failed to fetch status:", error);
            }
        };

        fetchStatus();
        const interval = setInterval(fetchStatus, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight text-white bg-gradient-to-r from-emerald-400 to-blue-500 bg-clip-text text-transparent">
                        Avatar System Dashboard
                    </h2>
                    <p className="text-slate-400">SOTA Unified Robotics Orchestration</p>
                </div>
                <div className="flex gap-2">
                    <Badge variant="outline" className="border-emerald-500/20 text-emerald-400">
                        v2026.2.17.SOTA
                    </Badge>
                </div>
            </div>

            {/* KPI Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl hover:border-emerald-500/30 transition-all duration-300">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-300">
                            Active Avatars
                        </CardTitle>
                        <Cpu className="h-4 w-4 text-emerald-400" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-white tracking-tighter">{status.active_avatars ?? "—"}</div>
                        <p className="text-xs text-slate-500 mt-1">Fleet Presence Status</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl hover:border-blue-500/30 transition-all duration-300">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-300">
                            Neural Load
                        </CardTitle>
                        <Activity className="h-4 w-4 text-blue-400" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-white tracking-tighter">{status.system_load_pct != null ? `${status.system_load_pct}%` : "N/A"}</div>
                        <p className="text-xs text-slate-500 mt-1">NVIDIA RTX 4090 Utilization</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl hover:border-purple-500/30 transition-all duration-300">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-300">
                            Unity Engine
                        </CardTitle>
                        <Box className="h-4 w-4 text-purple-400" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-white tracking-tighter uppercase">{status.unity_engine ?? "—"}</div>
                        <p className="text-xs text-slate-500 mt-1">Simulation Environment</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl hover:border-orange-500/30 transition-all duration-300">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-300">
                            OSC Pipeline
                        </CardTitle>
                        <GitMerge className="h-4 w-4 text-orange-400" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-white tracking-tighter uppercase">{status.osc_pipeline}</div>
                        <p className="text-xs text-slate-500 mt-1">Real-time Telemetry Pipe</p>
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <Card className="col-span-4 border-slate-800 bg-slate-950/40 backdrop-blur-xl">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Activity className="h-4 w-4 text-blue-400" />
                            Live Telemetry Feed
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-[300px] flex items-center justify-center border border-slate-800/50 rounded-xl bg-slate-900/10 group relative overflow-hidden">
                            <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                            <div className="flex flex-col items-center gap-3 z-10">
                                <Zap className="h-10 w-10 text-emerald-500/40 animate-pulse" />
                                <span className="text-slate-400 text-sm font-mono tracking-widest uppercase">Awaiting Robotic Sync</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card className="col-span-3 border-slate-800 bg-slate-950/40 backdrop-blur-xl">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Shield className="h-4 w-4 text-emerald-400" />
                            Fleet Integrity
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-6">
                            <div className="flex items-center justify-between group">
                                <div className="space-y-1">
                                    <p className="text-sm font-bold leading-none text-slate-200 font-mono tracking-wider">PROTOCOL</p>
                                    <p className="text-xs text-slate-500">FastMCP 2.14.3 SOTA</p>
                                </div>
                                <Badge className="bg-emerald-500/5 text-emerald-400 border-emerald-500/20">VERIFIED</Badge>
                            </div>
                            <div className="flex items-center justify-between group">
                                <div className="space-y-1">
                                    <p className="text-sm font-bold leading-none text-slate-200 font-mono tracking-wider">BRIDGE STATUS</p>
                                    <p className="text-xs text-slate-500 uppercase">{status.vrchat_bridge ?? "—"}</p>
                                </div>
                                <Badge className={`bg-blue-500/5 text-blue-400 border-blue-500/20`}>STABLE</Badge>
                            </div>
                            <div className="pt-4 border-t border-slate-800/50">
                                <div className="flex flex-col gap-2">
                                    <div className="text-[10px] text-slate-600 font-mono uppercase font-bold">Bridge health</div>
                                    <div className="h-1 w-full bg-slate-800 rounded-full overflow-hidden">
                                        <div className="h-full bg-emerald-500 w-full animate-pulse opacity-70" title="Bridge active when backend is up" />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
