import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Plus, RefreshCw, Trash2, Edit2, Download } from "lucide-react";

interface Avatar {
    id: string;
    name: string;
    status: 'loaded' | 'available';
    is_active: boolean;
    author?: string;
    version?: string;
}

const MOCK_AVATARS: Avatar[] = [
    { id: 'vienna_companion_v1', name: 'Vienna Companion (SOTA)', status: 'loaded', is_active: true, author: 'Sandra Schipal', version: '12.1' },
    { id: 'unity_test_bot', name: 'Standard Unity Bot', status: 'available', is_active: false, author: 'System', version: '1.0' },
    { id: 'benny_virtual', name: 'Benny (Virtual Shepherd)', status: 'loaded', is_active: false, author: 'Sandra Schipal', version: '2.0' },
];

export function Registry() {
    const [avatars] = useState<Avatar[]>(MOCK_AVATARS); // [MOCK] Data for initial view

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Avatar Registry</h2>
                    <p className="text-slate-400">Manage and catalog your VRM model fleet</p>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" className="border-slate-800 bg-slate-900/50 hover:bg-slate-800 text-slate-200">
                        <RefreshCw className="mr-2 h-4 w-4" />
                        Scan Directory
                    </Button>
                    <Button className="bg-blue-600 hover:bg-blue-700 text-white border-0">
                        <Plus className="mr-2 h-4 w-4" />
                        Import VRM
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {avatars.map((avatar) => (
                    <Card key={avatar.id} className={`border-slate-800 bg-slate-950/50 hover:border-slate-700 transition-all ${avatar.is_active ? 'ring-2 ring-blue-500/50' : ''}`}>
                        <CardHeader className="pb-3">
                            <div className="flex justify-between items-start">
                                <div className="space-y-1">
                                    <CardTitle className="text-lg text-white">{avatar.name}</CardTitle>
                                    <CardDescription className="text-[10px] font-mono uppercase tracking-widest text-slate-500">
                                        ID: {avatar.id}
                                    </CardDescription>
                                </div>
                                <Badge variant={avatar.status === 'loaded' ? 'default' : 'secondary'} className={avatar.status === 'loaded' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-slate-800 text-slate-400'}>
                                    {avatar.status.toUpperCase()}
                                </Badge>
                            </div>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-2 gap-2 text-xs">
                                <div className="text-slate-500 uppercase tracking-tighter font-bold">Creator</div>
                                <div className="text-slate-300">{avatar.author || 'Unknown'}</div>
                                <div className="text-slate-500 uppercase tracking-tighter font-bold">Version</div>
                                <div className="text-slate-300">{avatar.version || '0.0.0'}</div>
                            </div>

                            <div className="flex gap-2 pt-2">
                                <Button size="sm" variant="ghost" className="flex-1 justify-center h-8 text-slate-400 hover:text-white hover:bg-slate-800">
                                    <Edit2 className="h-3.5 w-3.5 mr-2" />
                                    Edit
                                </Button>
                                <Button size="sm" variant="ghost" className="flex-1 justify-center h-8 text-slate-400 hover:text-white hover:bg-slate-800">
                                    <Download className="h-3.5 w-3.5 mr-2" />
                                    Export
                                </Button>
                                <Button size="sm" variant="ghost" className="h-8 w-8 p-0 text-red-400 hover:text-red-300 hover:bg-red-900/20">
                                    <Trash2 className="h-3.5 w-3.5" />
                                </Button>
                            </div>

                            {avatar.status === 'available' ? (
                                <Button className="w-full bg-slate-800 hover:bg-slate-700 text-white mt-2">
                                    Load Model
                                </Button>
                            ) : (
                                <Button disabled={avatar.is_active} className={`w-full ${avatar.is_active ? 'bg-blue-600/50 text-white' : 'bg-blue-600 hover:bg-blue-700 text-white'} mt-2`}>
                                    {avatar.is_active ? 'Currently Active' : 'Set as Active'}
                                </Button>
                            )}
                        </CardContent>
                    </Card>
                ))}
            </div>

            <div className="mt-8 border-t border-slate-800 pt-6">
                <Card className="border-slate-800 bg-slate-950/20">
                    <CardHeader>
                        <CardTitle className="text-sm font-semibold flex items-center gap-2">
                            <Download className="h-4 w-4 text-emerald-500" />
                            Bulk Operations
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="flex gap-4">
                        <Button variant="outline" size="sm" className="border-slate-800 bg-slate-900/50 hover:bg-slate-800 text-slate-300">
                            Download Metadata (CSV)
                        </Button>
                        <Button variant="outline" size="sm" className="border-slate-800 bg-slate-900/50 hover:bg-slate-800 text-slate-300">
                            Cleanup Unused Models
                        </Button>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
