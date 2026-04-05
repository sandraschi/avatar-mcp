import { useState, useEffect } from 'react';
import { Activity, Cpu, HardDrive, Network } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface Health {
    status?: string;
    uptime?: number;
    bridge_active?: boolean;
    server?: string;
    version?: string;
}

interface ApiStatus {
    active_avatars?: number;
    system_load_pct?: number;
    unity_engine?: string;
    vrchat_bridge?: string;
    error?: string;
}

export function Status() {
    const [health, setHealth] = useState<Health | null>(null);
    const [status, setStatus] = useState<ApiStatus | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [healthRes, statusRes] = await Promise.all([
                    fetch('/api/v1/health'),
                    fetch('/api/v1/status'),
                ]);
                if (healthRes.ok) setHealth(await healthRes.json());
                else setHealth(null);
                if (statusRes.ok) setStatus(await statusRes.json());
                else setStatus(await statusRes.json().catch(() => ({ error: 'Not available' })));
                setError(null);
            } catch (e) {
                setError(e instanceof Error ? e.message : 'Failed to reach backend');
                setHealth(null);
                setStatus(null);
            }
        };
        fetchData();
        const interval = setInterval(fetchData, 10000);
        return () => clearInterval(interval);
    }, []);

    const uptimeSec = health?.uptime != null ? Math.floor(health.uptime) : null;

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-white">System Status</h1>
                <p className="text-slate-400">Real-time health from MCP backend (no mocks).</p>
                {error && (
                    <p className="text-amber-400 text-sm mt-2">Backend unreachable: {error}. Run web_sota/start.ps1.</p>
                )}
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">CPU Usage</CardTitle>
                        <Cpu className="h-4 w-4 text-blue-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">
                            {status?.system_load_pct != null ? `${status.system_load_pct}%` : '—'}
                        </div>
                        <p className="text-xs text-slate-500">From backend (psutil if available)</p>
                    </CardContent>
                </Card>
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">Bridge</CardTitle>
                        <Network className="h-4 w-4 text-emerald-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white uppercase">
                            {status?.vrchat_bridge ?? (status?.error ? 'Error' : '—')}
                        </div>
                        <p className="text-xs text-slate-500">MCP bridge status</p>
                    </CardContent>
                </Card>
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">Active Avatars</CardTitle>
                        <HardDrive className="h-4 w-4 text-orange-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">{status?.active_avatars ?? '—'}</div>
                        <p className="text-xs text-slate-500">Loaded models</p>
                    </CardContent>
                </Card>
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">Uptime</CardTitle>
                        <Activity className="h-4 w-4 text-purple-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">
                            {uptimeSec != null ? `${uptimeSec}s` : '—'}
                        </div>
                        <p className="text-xs text-slate-500">{health?.bridge_active ? 'Bridge active' : '—'}</p>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
