import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Plus, RefreshCw, Edit2, Download } from "lucide-react";

interface Avatar {
    id: string;
    name: string;
    path: string;
    is_active: boolean;
}

export function Registry() {
    const [avatars, setAvatars] = useState<Avatar[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchAvatars = async () => {
        try {
            setLoading(true);
            const response = await fetch('/api/v1/avatars');
            if (!response.ok) throw new Error('Failed to fetch avatars');
            const data = await response.json();
            setAvatars(Array.isArray(data) ? data : []);
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
            setAvatars([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAvatars();
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Avatar Registry</h2>
                    <p className="text-slate-400">Loaded avatars from MCP server (live from backend)</p>
                </div>
                <Button variant="outline" onClick={fetchAvatars} disabled={loading} className="border-slate-800 bg-slate-900/50 hover:bg-slate-800 text-slate-200">
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Refresh
                </Button>
            </div>

            {error && (
                <Card className="border-amber-900/50 bg-amber-950/20">
                    <CardContent className="pt-6 text-amber-400 text-sm">
                        {error}. Ensure backend is running (web_sota/start.ps1). Load avatars via MCP tools (e.g. avatar_manager).
                    </CardContent>
                </Card>
            )}

            {loading ? (
                <div className="py-12 flex flex-col items-center justify-center text-slate-500">
                    <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mb-4" />
                    <p>Loading avatar list...</p>
                </div>
            ) : avatars.length === 0 ? (
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardContent className="py-12 text-center text-slate-500">
                        No avatars loaded. Use the Tools Hub to run <span className="font-mono text-slate-400">avatar_manager</span> (e.g. operation: load) or connect your MCP client.
                    </CardContent>
                </Card>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {avatars.map((avatar) => (
                        <Card key={avatar.id} className={`border-slate-800 bg-slate-950/50 hover:border-slate-700 transition-all ${avatar.is_active ? 'ring-2 ring-blue-500/50' : ''}`}>
                            <CardHeader className="pb-3">
                                <div className="flex justify-between items-start">
                                    <div className="space-y-1">
                                        <CardTitle className="text-lg text-white">{avatar.name || avatar.id}</CardTitle>
                                        <CardDescription className="text-[10px] font-mono uppercase tracking-widest text-slate-500">ID: {avatar.id}</CardDescription>
                                    </div>
                                    <Badge className={avatar.is_active ? 'bg-emerald-500/10 text-emerald-500' : 'bg-slate-800 text-slate-400'}>
                                        {avatar.is_active ? 'ACTIVE' : 'LOADED'}
                                    </Badge>
                                </div>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {avatar.path && (
                                    <div className="text-xs text-slate-500 truncate" title={avatar.path}>Path: {avatar.path}</div>
                                )}
                                <div className="flex gap-2 pt-2">
                                    <Button size="sm" variant="ghost" className="flex-1 justify-center h-8 text-slate-400 hover:text-white hover:bg-slate-800">
                                        <Edit2 className="h-3.5 w-3.5 mr-2" />
                                        Edit
                                    </Button>
                                    <Button size="sm" variant="ghost" className="flex-1 justify-center h-8 text-slate-400 hover:text-white hover:bg-slate-800">
                                        <Download className="h-3.5 w-3.5 mr-2" />
                                        Export
                                    </Button>
                                </div>
                                <Button disabled={avatar.is_active} className={`w-full ${avatar.is_active ? 'bg-blue-600/50 text-white' : 'bg-blue-600 hover:bg-blue-700 text-white'} mt-2`}>
                                    {avatar.is_active ? 'Currently Active' : 'Set as Active'}
                                </Button>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}

            <div className="mt-8 border-t border-slate-800 pt-6">
                <Card className="border-slate-800 bg-slate-950/20">
                    <CardHeader>
                        <CardTitle className="text-sm font-semibold flex items-center gap-2">
                            <Download className="h-4 w-4 text-emerald-500" />
                            Bulk Operations
                        </CardTitle>
                        <CardDescription className="text-slate-500 text-xs">Use MCP tools (avatar_manager, artifact_manager) for load/import. This UI shows live state from the server.</CardDescription>
                    </CardHeader>
                    <CardContent className="flex gap-4">
                        <Button variant="outline" size="sm" className="border-slate-800 bg-slate-900/50 hover:bg-slate-800 text-slate-300" onClick={fetchAvatars}>
                            <RefreshCw className="h-3.5 w-3.5 mr-2" />
                            Refresh list
                        </Button>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
