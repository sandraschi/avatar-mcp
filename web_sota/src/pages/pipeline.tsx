import { useCallback, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, CloudDownload, Sparkles, UserCircle } from 'lucide-react';

type Step = { step?: string; success?: boolean; error?: string; message?: string };

export function Pipeline() {
    const [vrmName, setVrmName] = useState('anime_gal.vrm');
    const [hubModelId, setHubModelId] = useState('');
    const [authCode, setAuthCode] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState<string | null>(null);
    const [steps, setSteps] = useState<Step[]>([]);

    const run = useCallback(async (operation: string, extra: Record<string, unknown> = {}) => {
        setLoading(true);
        setMessage(null);
        setSteps([]);
        try {
            const response = await fetch('/api/v1/tools/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    tool_name: 'avatar_pipeline',
                    arguments: { operation, vrm_filename: vrmName, pick_sample: true, ...extra },
                }),
            });
            const data = await response.json().catch(() => ({}));
            if (!response.ok) {
                setMessage(data.detail ?? response.statusText);
                return;
            }
            const result = data.result ?? data;
            const parsed = typeof result === 'string' ? JSON.parse(result) : result;
            if (parsed.steps) setSteps(parsed.steps);
            if (parsed.authorize_url) {
                window.open(parsed.authorize_url, '_blank', 'noopener,noreferrer');
            }
            setMessage(parsed.message ?? JSON.stringify(parsed, null, 2));
        } catch (err) {
            setMessage(err instanceof Error ? err.message : 'Request failed');
        } finally {
            setLoading(false);
        }
    }, [vrmName]);

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-white flex items-center gap-2">
                    <UserCircle className="h-8 w-8 text-pink-400" />
                    Creative Pipeline
                </h1>
                <p className="text-slate-400 mt-1">
                    VRoid Hub download, VRoid export, Blender validate, VTube staging — orchestrated in avatar-mcp.
                </p>
            </div>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-white">VRoid Hub</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <p className="text-sm text-slate-400">
                        Register OAuth app at hub.vroid.com. Set VROID_HUB_CLIENT_ID / SECRET. Redirect URI:
                        {' '}
                        <code className="text-emerald-400">http://127.0.0.1:10793/api/v1/pipeline/hub/callback</code>
                    </p>
                    <div className="grid gap-3 sm:grid-cols-2">
                        <div>
                            <label className="text-xs font-bold uppercase text-slate-500 block mb-2">Hub character model ID</label>
                            <input
                                value={hubModelId}
                                onChange={(e) => setHubModelId(e.target.value)}
                                placeholder="e.g. from hub.vroid.com character URL"
                                className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white"
                            />
                        </div>
                        <div>
                            <label className="text-xs font-bold uppercase text-slate-500 block mb-2">OAuth code (manual paste)</label>
                            <input
                                value={authCode}
                                onChange={(e) => setAuthCode(e.target.value)}
                                placeholder="After browser login, if callback fails"
                                className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white"
                            />
                        </div>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        <Button disabled={loading} onClick={() => run('hub_auth', { auth_step: 'status' })} variant="secondary">
                            Hub status
                        </Button>
                        <Button disabled={loading} onClick={() => run('hub_auth', { auth_step: 'start' })} variant="secondary">
                            Connect Hub
                        </Button>
                        <Button
                            disabled={loading || !authCode}
                            onClick={() => run('hub_auth', { auth_step: 'complete', auth_code: authCode })}
                            variant="secondary"
                        >
                            Complete OAuth
                        </Button>
                        <Button
                            disabled={loading || !hubModelId}
                            onClick={() => run('hub_download', { character_model_id: hubModelId, vrm_filename: vrmName })}
                            variant="secondary"
                        >
                            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <CloudDownload className="h-4 w-4 mr-2" />}
                            Hub download
                        </Button>
                    </div>
                </CardContent>
            </Card>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-white">Pipeline target</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div>
                        <label className="text-xs font-bold uppercase text-slate-500 block mb-2">VRM filename</label>
                        <input
                            value={vrmName}
                            onChange={(e) => setVrmName(e.target.value)}
                            className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white"
                        />
                    </div>
                    <div className="flex flex-wrap gap-2">
                        {[
                            ['status', 'Status'],
                            ['vroid_quick_avatar', 'VRoid export'],
                            ['blender_validate', 'Blender validate'],
                            ['stage_for_vts', 'Stage for VTube'],
                            ['full_pipeline', 'Full pipeline'],
                        ].map(([op, label]) => (
                            <Button key={op} disabled={loading} onClick={() => run(op)} variant="secondary">
                                {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Sparkles className="h-4 w-4 mr-2" />}
                                {label}
                            </Button>
                        ))}
                    </div>
                    {message && (
                        <pre className="text-sm text-emerald-400 whitespace-pre-wrap bg-slate-900/50 p-3 rounded-md">{message}</pre>
                    )}
                    {steps.length > 0 && (
                        <ul className="text-sm space-y-1 text-slate-300">
                            {steps.map((s, i) => (
                                <li key={i}>
                                    <span className={s.success ? 'text-emerald-400' : 'text-red-400'}>{s.success ? 'OK' : 'FAIL'}</span>
                                    {' '}{s.step}{s.message ? `: ${s.message}` : ''}
                                </li>
                            ))}
                        </ul>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
