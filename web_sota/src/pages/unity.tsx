import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Settings, Monitor, Activity, Power } from "lucide-react";

export function Unity() {
    const [connected] = useState(true); // [MOCK] Connectivity status

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Unity Bridge</h2>
                    <p className="text-slate-400">High-fidelity virtual robotics orchestration</p>
                </div>
                <Badge variant={connected ? 'default' : 'destructive'} className={connected ? 'bg-emerald-500/10 text-emerald-500' : ''}>
                    {connected ? 'LINK ESTABLISHED' : 'DISCONNECTED'}
                </Badge>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="border-slate-800 bg-slate-950/50 md:col-span-2">
                    <CardHeader>
                        <div className="flex items-center justify-between">
                            <CardTitle className="text-lg flex items-center gap-2">
                                <Monitor className="h-5 w-5 text-blue-500" />
                                Viewport Control
                            </CardTitle>
                            <div className="flex gap-2">
                                <Button size="sm" variant="outline" className="h-8 border-slate-800 bg-slate-900 hover:bg-slate-800">
                                    Capture Frame
                                </Button>
                                <Button size="sm" className="h-8 bg-blue-600 hover:bg-blue-700">
                                    Focus Window
                                </Button>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="aspect-video bg-slate-900 rounded-lg border border-slate-800 flex items-center justify-center relative group overflow-hidden">
                            <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-4">
                                <div className="text-[10px] font-mono text-slate-400">
                                    [MOCK] Unity Instance: 0x7FFD_2841_90BC | Framerate: 120 FPS
                                </div>
                            </div>
                            <div className="text-center space-y-2">
                                <Activity className="h-8 w-8 text-slate-700 mx-auto animate-pulse" />
                                <p className="text-sm text-slate-600 font-medium">Virtual Viewport Active</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <div className="space-y-6">
                    <Card className="border-slate-800 bg-slate-950/50">
                        <CardHeader>
                            <CardTitle className="text-sm font-semibold flex items-center gap-2">
                                <Power className="h-4 w-4 text-emerald-500" />
                                Instance Lifecycle
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <Button className="w-full bg-slate-800 hover:bg-emerald-600/20 hover:text-emerald-400 hover:border-emerald-600/50 transition-all">
                                Launch Virtual Environment
                            </Button>
                            <Button variant="outline" className="w-full border-slate-800 bg-slate-900/50 text-red-400 hover:bg-red-900/20 hover:text-red-300">
                                Terminate Instance
                            </Button>
                        </CardContent>
                    </Card>

                    <Card className="border-slate-800 bg-slate-950/50">
                        <CardHeader>
                            <CardTitle className="text-sm font-semibold flex items-center gap-2">
                                <Settings className="h-4 w-4 text-slate-500" />
                                Integration Config
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                            <div className="flex justify-between text-xs">
                                <span className="text-slate-500">API Port</span>
                                <span className="text-slate-300 font-mono">10793</span>
                            </div>
                            <div className="flex justify-between text-xs">
                                <span className="text-slate-500">Plugin Version</span>
                                <span className="text-slate-300 font-mono">v1.2.0-SOTA</span>
                            </div>
                            <div className="flex justify-between text-xs">
                                <span className="text-slate-500">Physics Engine</span>
                                <span className="text-slate-300 font-mono">PhysX 5.0</span>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
