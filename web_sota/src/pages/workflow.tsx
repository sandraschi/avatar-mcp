import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Play, ListTodo } from 'lucide-react';

export function Workflow() {
    const [workflowPrompt, setWorkflowPrompt] = useState('');
    const [avatarId, setAvatarId] = useState('');
    const [avatars, setAvatars] = useState<{ id: string; name: string }[]>([]);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<unknown>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const f = async () => {
            try {
                const r = await fetch('/api/v1/avatars');
                if (r.ok) {
                    const data = await r.json();
                    setAvatars(Array.isArray(data) ? data.map((a: { id: string; name?: string }) => ({ id: a.id, name: a.name ?? a.id })) : []);
                }
            } catch {
                setAvatars([]);
            }
        };
        f();
    }, []);

    const runWorkflow = async () => {
        if (!workflowPrompt.trim() || !avatarId.trim()) {
            setError('Set workflow prompt and avatar ID.');
            return;
        }
        setLoading(true);
        setError(null);
        setResult(null);
        try {
            const response = await fetch('/api/v1/tools/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    tool_name: 'avatar_agentic_workflow',
                    arguments: {
                        workflow_prompt: workflowPrompt.trim(),
                        avatar_id: avatarId.trim(),
                        max_iterations: 5,
                    },
                }),
            });
            const data = await response.json().catch(() => ({}));
            if (!response.ok) {
                setError(data.detail ?? response.statusText);
                setResult(data);
                return;
            }
            setResult(data.result ?? data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Request failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-white">Agentic Workflow</h1>
                <p className="text-slate-400">Run avatar_agentic_workflow via MCP: describe a behavior and pick an avatar.</p>
            </div>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                        <ListTodo className="h-5 w-5 text-blue-500" />
                        Workflow parameters
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div>
                        <label className="text-xs font-bold uppercase text-slate-500 block mb-2">Workflow prompt (e.g. &quot;smile and wave&quot;)</label>
                        <textarea
                            className="w-full h-20 rounded bg-slate-950 border border-slate-700 text-slate-200 p-2 text-sm"
                            value={workflowPrompt}
                            onChange={(e) => setWorkflowPrompt(e.target.value)}
                            placeholder="Describe what the avatar should do..."
                        />
                    </div>
                    <div>
                        <label className="text-xs font-bold uppercase text-slate-500 block mb-2">Avatar ID</label>
                        <select
                            className="w-full rounded bg-slate-950 border border-slate-700 text-slate-200 p-2 text-sm"
                            value={avatarId}
                            onChange={(e) => setAvatarId(e.target.value)}
                        >
                            <option value="">Select or type ID</option>
                            {avatars.map((a) => (
                                <option key={a.id} value={a.id}>{a.name}</option>
                            ))}
                        </select>
                        {avatars.length === 0 && (
                            <p className="text-xs text-slate-500 mt-1">No avatars from API. Type an ID if you have one loaded via MCP.</p>
                        )}
                        <input
                            type="text"
                            className="w-full mt-2 rounded bg-slate-950 border border-slate-700 text-slate-200 p-2 text-sm font-mono"
                            placeholder="Or type avatar_id"
                            value={avatarId}
                            onChange={(e) => setAvatarId(e.target.value)}
                        />
                    </div>
                    {error && <p className="text-amber-400 text-sm">{error}</p>}
                    <Button className="bg-emerald-600 hover:bg-emerald-700 text-white" onClick={runWorkflow} disabled={loading}>
                        {loading ? 'Running…' : <><Play className="h-4 w-4 mr-2" /> Run workflow</>}
                    </Button>
                </CardContent>
            </Card>

            {result != null && (
                <Card className="border-slate-700 bg-slate-900/50">
                    <CardHeader><CardTitle className="text-sm text-slate-300">Result</CardTitle></CardHeader>
                    <CardContent>
                        <pre className="text-xs text-slate-400 overflow-auto max-h-64 rounded bg-slate-950 p-3">
                            {typeof result === 'string' ? result : JSON.stringify(result, null, 2)}
                        </pre>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
