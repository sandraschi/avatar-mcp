import { useCallback, useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
    Loader2,
    CloudDownload,
    Sparkles,
    UserCircle,
    Database,
    FolderOpen,
    Link2,
} from 'lucide-react';

type Step = { step?: string; success?: boolean; error?: string; message?: string; note?: string };
type DepotEntry = {
    id: string;
    kind: string;
    source: string;
    name: string;
    path: string;
    editable_in_studio?: boolean;
};

export function Pipeline() {
    const [vrmName, setVrmName] = useState('anime_gal.vrm');
    const [hubModelId, setHubModelId] = useState('');
    const [authCode, setAuthCode] = useState('');
    const [projectPath, setProjectPath] = useState('');
    const [depotId, setDepotId] = useState('');
    const [sourcePath, setSourcePath] = useState('');
    const [exportAfter, setExportAfter] = useState(false);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState<string | null>(null);
    const [note, setNote] = useState<string | null>(null);
    const [steps, setSteps] = useState<Step[]>([]);
    const [depotEntries, setDepotEntries] = useState<DepotEntry[]>([]);
    const [pipelineOnline, setPipelineOnline] = useState<boolean | null>(null);

    const run = useCallback(async (operation: string, extra: Record<string, unknown> = {}, silent = false) => {
        if (!silent) {
            setLoading(true);
            setMessage(null);
            setNote(null);
            setSteps([]);
        }
        try {
            const response = await fetch('/api/v1/tools/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    tool_name: 'avatar_pipeline',
                    arguments: {
                        operation,
                        vrm_filename: vrmName,
                        pick_sample: true,
                        project_path: projectPath,
                        depot_id: depotId,
                        export_after: exportAfter,
                        source_path: sourcePath,
                        ...extra,
                    },
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
            if (parsed.entries) setDepotEntries(parsed.entries);
            if (parsed.entry) {
                setDepotEntries((prev) => {
                    const entry = parsed.entry as DepotEntry;
                    if (prev.some((e) => e.id === entry.id)) return prev;
                    return [entry, ...prev];
                });
                if (parsed.entry.id) setDepotId(parsed.entry.id);
            }
            if (parsed.authorize_url) {
                window.open(parsed.authorize_url, '_blank', 'noopener,noreferrer');
            }
            if (parsed.note) setNote(parsed.note);
            if (operation === 'status' && parsed.success !== false) setPipelineOnline(true);
            if (!silent) {
                setMessage(parsed.message ?? (parsed.success === false ? parsed.error : JSON.stringify(parsed, null, 2)));
            }
        } catch (err) {
            if (operation === 'status') setPipelineOnline(false);
            if (!silent) setMessage(err instanceof Error ? err.message : 'Request failed');
        } finally {
            if (!silent) setLoading(false);
        }
    }, [vrmName, projectPath, depotId, exportAfter, sourcePath]);

    const selectDepotEntry = useCallback((entry: DepotEntry) => {
        setDepotId(entry.id);
        if (entry.kind === 'vroid' || entry.editable_in_studio) {
            setProjectPath(entry.path);
        }
    }, []);

    const openDepotInStudio = useCallback((entry: DepotEntry) => {
        selectDepotEntry(entry);
        run('hub_to_studio', {
            depot_id: entry.id,
            project_path: entry.kind === 'vroid' ? entry.path : projectPath,
            open_in_studio: true,
        });
    }, [projectPath, run, selectDepotEntry]);

    const loadDepot = useCallback((silent = false) => {
        run('depot_list', { scan_depot: true }, silent);
    }, [run]);

    useEffect(() => {
        void run('status', {}, true);
        void loadDepot(true);
        // eslint-disable-next-line react-hooks/exhaustive-deps -- mount-only bootstrap
    }, []);

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-white flex items-center gap-2">
                    <UserCircle className="h-8 w-8 text-pink-400" />
                    Creative Pipeline
                </h1>
                <p className="text-slate-400 mt-1">
                    Hub download, local depot, VRoid Studio projects, Blender validate, VTube staging.
                </p>
                <div
                    className={`inline-flex mt-3 text-xs px-3 py-1 rounded-full border ${
                        pipelineOnline === null
                            ? 'border-slate-700 text-slate-500'
                            : pipelineOnline
                              ? 'border-emerald-800 text-emerald-400 bg-emerald-950/30'
                              : 'border-amber-800 text-amber-400 bg-amber-950/30'
                    }`}
                >
                    Pipeline {pipelineOnline === null ? 'checking…' : pipelineOnline ? 'online' : 'offline — start avatar-mcp :10793'}
                </div>
            </div>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                        <CloudDownload className="h-5 w-5 text-sky-400" />
                        VRoid Hub
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <p className="text-sm text-slate-400">
                        OAuth at hub.vroid.com. Redirect:
                        {' '}
                        <code className="text-emerald-400 text-xs">http://127.0.0.1:10793/api/v1/pipeline/hub/callback</code>
                    </p>
                    <div className="grid gap-3 sm:grid-cols-2">
                        <div>
                            <label className="text-xs font-bold uppercase text-slate-500 block mb-2">Character model ID</label>
                            <input
                                value={hubModelId}
                                onChange={(e) => setHubModelId(e.target.value)}
                                placeholder="From hub character URL"
                                className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white"
                            />
                        </div>
                        <div>
                            <label className="text-xs font-bold uppercase text-slate-500 block mb-2">OAuth code (manual)</label>
                            <input
                                value={authCode}
                                onChange={(e) => setAuthCode(e.target.value)}
                                className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white"
                            />
                        </div>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        <Button disabled={loading} onClick={() => run('hub_auth', { auth_step: 'status' })} variant="secondary">Hub status</Button>
                        <Button disabled={loading} onClick={() => run('hub_auth', { auth_step: 'start' })} variant="secondary">Connect</Button>
                        <Button disabled={loading || !authCode} onClick={() => run('hub_auth', { auth_step: 'complete', auth_code: authCode })} variant="secondary">Complete OAuth</Button>
                        <Button disabled={loading || !hubModelId} onClick={() => run('hub_download', { character_model_id: hubModelId })} variant="secondary">
                            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <CloudDownload className="h-4 w-4 mr-2" />}
                            Download VRM
                        </Button>
                    </div>
                </CardContent>
            </Card>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                        <Link2 className="h-5 w-5 text-violet-400" />
                        Hub to Studio
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <p className="text-sm text-slate-400">
                        Download from Hub and/or open a .vroid project in VRoid Studio. Hub assets are VRM — editable Studio work needs a .vroid file.
                    </p>
                    <div className="grid gap-3 sm:grid-cols-2">
                        <div className="sm:col-span-2">
                            <label className="text-xs font-bold uppercase text-slate-500 block mb-2">Project path (.vroid)</label>
                            <input
                                value={projectPath}
                                onChange={(e) => setProjectPath(e.target.value)}
                                placeholder="D:\avatars\mychar.vroid"
                                className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white font-mono text-sm"
                            />
                        </div>
                        <div>
                            <label className="text-xs font-bold uppercase text-slate-500 block mb-2">Depot entry id</label>
                            <input
                                value={depotId}
                                onChange={(e) => setDepotId(e.target.value)}
                                placeholder="From depot list"
                                className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white font-mono text-sm"
                            />
                        </div>
                        <div className="flex items-end pb-2">
                            <label className="flex items-center gap-2 text-sm text-slate-300">
                                <input type="checkbox" checked={exportAfter} onChange={(e) => setExportAfter(e.target.checked)} />
                                Export VRM after open
                            </label>
                        </div>
                    </div>
                    <Button
                        disabled={loading || (!hubModelId && !projectPath && !depotId)}
                        onClick={() => run('hub_to_studio', { character_model_id: hubModelId, open_in_studio: true })}
                    >
                        {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <FolderOpen className="h-4 w-4 mr-2" />}
                        Hub to Studio
                    </Button>
                </CardContent>
            </Card>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                        <Database className="h-5 w-5 text-amber-400" />
                        Local depot
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div>
                        <label className="text-xs font-bold uppercase text-slate-500 block mb-2">Register file path</label>
                        <input
                            value={sourcePath}
                            onChange={(e) => setSourcePath(e.target.value)}
                            placeholder=".vrm or .vroid path"
                            className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white font-mono text-sm"
                        />
                    </div>
                    <div className="flex flex-wrap gap-2">
                        <Button disabled={loading} onClick={() => loadDepot()} variant="secondary">Scan + list depot</Button>
                        <Button disabled={loading || !sourcePath} onClick={() => run('depot_register', { copy_to_depot: true })} variant="secondary">Register file</Button>
                        <Button disabled={loading || !depotId} onClick={() => run('depot_get')} variant="secondary">Get entry</Button>
                    </div>
                    {depotEntries.length > 0 && (
                        <div className="overflow-x-auto rounded-md border border-slate-800">
                            <table className="w-full text-sm text-left">
                                <thead className="text-slate-500 uppercase text-xs bg-slate-900/80">
                                    <tr>
                                        <th className="px-3 py-2">ID</th>
                                        <th className="px-3 py-2">Kind</th>
                                        <th className="px-3 py-2">Source</th>
                                        <th className="px-3 py-2">Name</th>
                                        <th className="px-3 py-2"></th>
                                    </tr>
                                </thead>
                                <tbody className="text-slate-300">
                                    {depotEntries.map((e) => (
                                        <tr key={e.id} className="border-t border-slate-800 hover:bg-slate-900/50">
                                            <td className="px-3 py-2 font-mono text-xs">{e.id}</td>
                                            <td className="px-3 py-2">{e.kind}</td>
                                            <td className="px-3 py-2">{e.source}</td>
                                            <td className="px-3 py-2">{e.name}</td>
                                            <td className="px-3 py-2">
                                                <div className="flex gap-2">
                                                    <button
                                                        type="button"
                                                        className="text-violet-400 hover:underline text-xs"
                                                        onClick={() => selectDepotEntry(e)}
                                                    >
                                                        Use
                                                    </button>
                                                    {(e.kind === 'vroid' || e.editable_in_studio) && (
                                                        <button
                                                            type="button"
                                                            className="text-sky-400 hover:underline text-xs"
                                                            onClick={() => openDepotInStudio(e)}
                                                        >
                                                            Studio
                                                        </button>
                                                    )}
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </CardContent>
            </Card>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-white">Pipeline</CardTitle>
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
                            ['list_staging', 'List staging'],
                            ['vroid_quick_avatar', 'VRoid export'],
                            ['blender_validate', 'Blender validate'],
                            ['blender_reexport', 'Blender reexport'],
                            ['stage_for_vts', 'Stage VTube'],
                            ['full_pipeline', 'Full pipeline'],
                        ].map(([op, label]) => (
                            <Button key={op} disabled={loading} onClick={() => run(op)} variant="secondary">
                                {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Sparkles className="h-4 w-4 mr-2" />}
                                {label}
                            </Button>
                        ))}
                    </div>
                    {note && (
                        <p className="text-sm text-amber-300/90 bg-amber-950/20 border border-amber-900/40 rounded-md p-3">{note}</p>
                    )}
                    {message && (
                        <pre className="text-sm text-emerald-400 whitespace-pre-wrap bg-slate-900/50 p-3 rounded-md max-h-64 overflow-auto">{message}</pre>
                    )}
                    {steps.length > 0 && (
                        <ul className="text-sm space-y-1 text-slate-300">
                            {steps.map((s, i) => (
                                <li key={i}>
                                    <span className={s.success !== false ? 'text-emerald-400' : 'text-red-400'}>
                                        {s.success !== false ? 'OK' : 'FAIL'}
                                    </span>
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
