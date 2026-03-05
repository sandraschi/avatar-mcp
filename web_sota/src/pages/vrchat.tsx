import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Radio, Activity, Zap, Shield, MessageSquare } from "lucide-react";

export function VRChat() {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">VRChat OSC Explorer</h2>
                    <p className="text-slate-400">Social VR telemetry and expression control</p>
                </div>
                <div className="flex items-center gap-2">
                    <Badge variant="outline" className="border-emerald-500/20 bg-emerald-500/10 text-emerald-500 font-mono">
                        OSC:9000 {"->"} 9001
                    </Badge>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="pb-2">
                        <CardDescription className="text-[10px] uppercase font-bold tracking-widest text-slate-500">
                            Heartbeat
                        </CardDescription>
                        <CardTitle className="text-2xl font-bold text-white flex items-baseline gap-2">
                            Active
                            <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-xs text-slate-400">Last seen: Just now</div>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="pb-2">
                        <CardDescription className="text-[10px] uppercase font-bold tracking-widest text-slate-500">
                            Latency
                        </CardDescription>
                        <CardTitle className="text-2xl font-bold text-blue-400">12ms</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-xs text-slate-400">Network stability: 99.9%</div>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="pb-2">
                        <CardDescription className="text-[10px] uppercase font-bold tracking-widest text-slate-500">
                            Parameters
                        </CardDescription>
                        <CardTitle className="text-2xl font-bold text-white">128</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-xs text-slate-400">Sync overhead: 0.2 MB/s</div>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="pb-2">
                        <CardDescription className="text-[10px] uppercase font-bold tracking-widest text-slate-500">
                            Expressions
                        </CardDescription>
                        <CardTitle className="text-2xl font-bold text-purple-400">8/32</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-xs text-slate-400">Standard VRM Blendshapes</div>
                    </CardContent>
                </Card>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-lg flex items-center gap-2">
                            <Radio className="h-5 w-5 text-emerald-500" />
                            Live OSC Monitor
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="bg-black/40 rounded border border-slate-800 p-4 font-mono text-[11px] h-[300px] overflow-y-auto space-y-1">
                            <div className="text-slate-500">[2026-02-15 00:03:03] <span className="text-emerald-400">RECV</span> /avatar/parameters/VelocityX (float) 0.12</div>
                            <div className="text-slate-500">[2026-02-15 00:03:03] <span className="text-emerald-400">RECV</span> /avatar/parameters/VelocityZ (float) -0.45</div>
                            <div className="text-slate-500">[2026-02-15 00:03:04] <span className="text-blue-400">SEND</span> /avatar/expression/MouthSmile (float) 1.00</div>
                            <div className="text-slate-500">[2026-02-15 00:03:04] <span className="text-emerald-400">RECV</span> /avatar/parameters/Grounded (bool) true</div>
                            <div className="text-slate-500">[2026-02-15 00:03:05] <span className="text-emerald-400">RECV</span> /avatar/parameters/InStation (bool) false</div>
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-lg flex items-center gap-2">
                            <Zap className="h-5 w-5 text-yellow-500" />
                            Expression Macros
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="grid grid-cols-2 gap-3">
                        <Button variant="outline" className="h-12 border-slate-800 bg-slate-900/50 hover:bg-slate-800 justify-start">
                            <MessageSquare className="mr-3 h-4 w-4 text-blue-400" />
                            Wave Greeting
                        </Button>
                        <Button variant="outline" className="h-12 border-slate-800 bg-slate-900/50 hover:bg-slate-800 justify-start">
                            <Shield className="mr-3 h-4 w-4 text-emerald-400" />
                            Shield Toggle
                        </Button>
                        <Button variant="outline" className="h-12 border-slate-800 bg-slate-900/50 hover:bg-slate-800 justify-start">
                            <Zap className="mr-3 h-4 w-4 text-yellow-400" />
                            Force Reset
                        </Button>
                        <Button variant="outline" className="h-12 border-slate-800 bg-slate-900/50 hover:bg-slate-800 justify-start">
                            <Activity className="mr-3 h-4 w-4 text-purple-400" />
                            Calibrate Tracking
                        </Button>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
