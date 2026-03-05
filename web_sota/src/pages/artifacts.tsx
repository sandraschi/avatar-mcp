import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
    Download,
    Search,
    ArrowRightLeft,
    FileCheck,
    AlertCircle,
    Package,
    Boxes
} from "lucide-react";

interface Artifact {
    name: string;
    path: string;
    size_mb: number;
    created: number;
    suggested_target: string;
    tier?: string;
}

interface PipelineStatus {
    health: string;
    monitoring_path: string;
    last_scan: string;
}

export function Artifacts() {
    const [artifacts, setArtifacts] = useState<Artifact[]>([]);
    const [scanning, setScanning] = useState(false);
    const [status, setStatus] = useState<PipelineStatus | null>(null);

    const scan = () => {
        setScanning(true);
        fetch("http://127.0.0.1:10793/api/v1/call", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: "artifact_manager",
                arguments: { operation: "monitor_scan" }
            }),
        })
            .then(r => r.json())
            .then(d => {
                if (d.result && d.result.artifacts) {
                    setArtifacts(d.result.artifacts);
                }
            })
            .finally(() => setScanning(false));
    };

    const deposit = (file_path: string) => {
        fetch("http://127.0.0.1:10793/api/v1/call", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: "artifact_manager",
                arguments: { operation: "deposit", file_path }
            }),
        })
            .then(r => r.json())
            .then(() => scan());
    };

    useEffect(() => {
        let mounted = true;

        const initialize = async () => {
            if (!mounted) return;
            setScanning(true);
            try {
                // Fetch status first
                const statusRes = await fetch("http://127.0.0.1:10793/api/v1/call", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        tool: "artifact_manager",
                        method: "get_status",
                        params: {}
                    })
                });
                const statusData = await statusRes.json();
                if (mounted && statusData.status === "success") {
                    setStatus(statusData.result);
                }

                // Initial scan
                const scanRes = await fetch("http://127.0.0.1:10793/api/v1/call", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        tool: "artifact_manager",
                        method: "monitor_scan",
                        params: {}
                    })
                });
                const scanData = await scanRes.json();
                if (mounted && scanData.status === "success") {
                    setArtifacts(scanData.result.artifacts);
                }
            } catch (error) {
                console.error("Initial fetch failed:", error);
            } finally {
                if (mounted) setScanning(false);
            }
        };

        initialize();

        return () => {
            mounted = false;
        };
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-500 bg-clip-text text-transparent">
                        Artifact Pipeline
                    </h2>
                    <p className="text-slate-400">External Landfalls · File Deposit · Automated Routing</p>
                </div>
                <div className="flex gap-2">
                    {status && (
                        <Badge variant="outline" className="border-emerald-500/20 text-emerald-400 bg-emerald-500/5">
                            Hawk-Mode: {status.health.toUpperCase()}
                        </Badge>
                    )}
                    <button
                        onClick={scan}
                        disabled={scanning}
                        className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-lg text-sm transition-all border border-slate-700"
                    >
                        <Search className={`h-4 w-4 ${scanning ? 'animate-spin' : ''}`} />
                        {scanning ? 'Scanning...' : 'Scan Landfalls'}
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <Card className="md:col-span-3 border-slate-800 bg-slate-950/40 backdrop-blur-xl">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Download className="h-4 w-4 text-cyan-400" />
                            Detected Landfalls
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        {artifacts.length === 0 ? (
                            <div className="flex flex-col items-center justify-center py-12 text-slate-500">
                                <Boxes className="h-12 w-12 opacity-20 mb-4" />
                                <p className="text-sm">No new artifacts detected in Downloads.</p>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {artifacts.map((art) => (
                                    <div key={art.path} className="flex items-center justify-between p-4 rounded-xl bg-slate-900/50 border border-slate-800 hover:border-slate-700 transition-colors">
                                        <div className="flex items-center gap-4 overflow-hidden">
                                            <div className="p-3 rounded-lg bg-slate-800 text-cyan-400">
                                                <Package className="h-5 w-5" />
                                            </div>
                                            <div className="overflow-hidden">
                                                <h4 className="text-sm font-bold text-slate-200 truncate">{art.name}</h4>
                                                <div className="flex items-center gap-3 text-[10px] text-slate-500 font-mono">
                                                    <span>{art.size_mb} MB</span>
                                                    <span>•</span>
                                                    <span className="uppercase text-cyan-500/70">{art.suggested_target}</span>
                                                    {art.tier && (
                                                        <>
                                                            <span>•</span>
                                                            <span className="text-indigo-400 font-bold">{art.tier}</span>
                                                        </>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => deposit(art.path)}
                                            className="flex items-center gap-2 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 px-3 py-1.5 rounded-lg text-xs font-bold border border-cyan-500/30 transition-all group"
                                        >
                                            <ArrowRightLeft className="h-3 w-3 group-hover:rotate-180 transition-transform duration-500" />
                                            DEPOSIT
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>

                <div className="space-y-6">
                    <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl border-l-4 border-l-cyan-500">
                        <CardHeader>
                            <CardTitle className="text-xs font-bold text-slate-400 uppercase tracking-widest">Pipeline Health</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex items-center justify-between">
                                <span className="text-xs text-slate-500">Watcher Node</span>
                                <div className="flex items-center gap-1.5">
                                    <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                                    <span className="text-xs text-emerald-500 font-mono">ONLINE</span>
                                </div>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-xs text-slate-500">Last LANDFALL</span>
                                <span className="text-xs text-slate-300 font-mono">2m ago</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-xs text-slate-500">Auth Signature</span>
                                <FileCheck className="h-3 w-3 text-emerald-500" />
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl">
                        <CardHeader>
                            <CardTitle className="text-xs font-bold text-slate-400 uppercase tracking-widest">Active Links</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-2">
                            {['Resonite', 'Unity3D', 'VRChat', 'Gazebo'].map(link => (
                                <div key={link} className="flex items-center justify-between p-2 rounded-lg bg-slate-900/50 border border-slate-800/50">
                                    <span className="text-[10px] font-bold text-slate-400 tracking-wider uppercase">{link}</span>
                                    <div className="h-1.5 w-1.5 rounded-full bg-cyan-500/50 shadow-[0_0_8px_rgba(6,182,212,0.5)]" />
                                </div>
                            ))}
                        </CardContent>
                    </Card>

                    <AlertCircle className="h-12 w-12 text-slate-800 mx-auto mt-8 opacity-20" />
                </div>
            </div>
        </div>
    );
}
