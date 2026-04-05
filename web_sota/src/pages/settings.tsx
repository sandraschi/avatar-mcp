import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Download, Upload, Shield, Globe, Cpu, RefreshCw } from "lucide-react";

type OllamaModel = { name: string; size?: number; modified_at?: string };

export function Settings() {
    const [ollamaConnected, setOllamaConnected] = useState<boolean | null>(null);
    const [ollamaModels, setOllamaModels] = useState<OllamaModel[]>([]);
    const [selectedModel, setSelectedModel] = useState("");
    const [modelsLoading, setModelsLoading] = useState(false);

    useEffect(() => {
        let cancelled = false;
        async function load() {
            try {
                const [statusRes, modelsRes, llmRes] = await Promise.all([
                    fetch("/api/v1/settings/ollama/status"),
                    fetch("/api/v1/settings/ollama/models"),
                    fetch("/api/v1/settings/llm"),
                ]);
                if (cancelled) return;
                const status = await statusRes.json().catch(() => ({}));
                const modelsData = await modelsRes.json().catch(() => ({ models: [] }));
                const llm = await llmRes.json().catch(() => ({ model: "" }));
                setOllamaConnected(status.connected === true);
                setOllamaModels(modelsData.models || []);
                setSelectedModel(llm.model || "");
            } catch {
                if (!cancelled) setOllamaConnected(false);
            }
        }
        load();
        return () => { cancelled = true; };
    }, []);

    async function refreshModels() {
        setModelsLoading(true);
        try {
            const [statusRes, modelsRes] = await Promise.all([
                fetch("/api/v1/settings/ollama/status"),
                fetch("/api/v1/settings/ollama/models"),
            ]);
            const status = await statusRes.json().catch(() => ({}));
            const modelsData = await modelsRes.json().catch(() => ({ models: [] }));
            setOllamaConnected(status.connected === true);
            setOllamaModels(modelsData.models || []);
        } finally {
            setModelsLoading(false);
        }
    }

    async function onModelChange(value: string) {
        setSelectedModel(value);
        try {
            await fetch("/api/v1/settings/llm", {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ model: value }),
            });
        } catch {
            setSelectedModel(selectedModel);
        }
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">System Settings</h2>
                    <p className="text-slate-400">Environment configuration and model orchestration</p>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" className="border-slate-800 bg-slate-900/50 hover:bg-slate-800 text-slate-300">
                        <Upload className="mr-2 h-4 w-4" />
                        Import Config
                    </Button>
                    <Button variant="outline" className="border-slate-800 bg-slate-900/50 hover:bg-slate-800 text-slate-300">
                        <Download className="mr-2 h-4 w-4" />
                        Export Config
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Globe className="h-4 w-4 text-emerald-500" />
                            Network & Ports
                        </CardTitle>
                        <CardDescription className="text-slate-400">Standard SOTA port reservations</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label className="text-slate-400 text-[10px] uppercase font-bold">Backend API Port</Label>
                            <Input className="bg-slate-900 border-slate-800 text-slate-100" defaultValue="10792" readOnly />
                        </div>
                        <div className="space-y-2">
                            <Label className="text-slate-400 text-[10px] uppercase font-bold">Frontend Web Port</Label>
                            <Input className="bg-slate-900 border-slate-800 text-slate-100" defaultValue="10702" readOnly />
                        </div>
                        <div className="pt-2">
                            <Button className="w-full bg-blue-600 hover:bg-blue-700">Rebind Ports</Button>
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Cpu className="h-4 w-4 text-emerald-500" />
                            Local Intelligence
                        </CardTitle>
                        <CardDescription className="text-slate-400">Ollama models for chat and agentic workflows</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex items-center justify-between p-3 rounded bg-slate-900/50 border border-slate-800">
                            <div className="flex items-center gap-3">
                                {ollamaConnected === null ? (
                                    <RefreshCw className="h-4 w-4 text-slate-500 animate-spin" />
                                ) : ollamaConnected ? (
                                    <RefreshCw className="h-4 w-4 text-blue-500" />
                                ) : (
                                    <Shield className="h-4 w-4 text-slate-600" />
                                )}
                                <span className="text-sm text-slate-300">Ollama (11434)</span>
                            </div>
                            {ollamaConnected === null ? (
                                <Badge variant="outline" className="text-slate-500 border-slate-700">Checking...</Badge>
                            ) : ollamaConnected ? (
                                <Badge className="bg-emerald-500/10 text-emerald-500">CONNECTED</Badge>
                            ) : (
                                <Badge variant="outline" className="text-slate-600 border-slate-800">NOT FOUND</Badge>
                            )}
                        </div>
                        {ollamaConnected && (
                            <>
                                <div className="space-y-2">
                                    <Label className="text-slate-400 text-[10px] uppercase font-bold">Model</Label>
                                    <select
                                        value={selectedModel}
                                        onChange={(e) => onModelChange(e.target.value)}
                                        className="w-full h-9 rounded-md border border-slate-800 bg-slate-900 px-3 py-1 text-sm text-slate-100 focus:outline-none focus:ring-1 focus:ring-blue-500"
                                    >
                                        <option value="">Select model...</option>
                                        {ollamaModels.map((m) => (
                                            <option key={m.name} value={m.name}>{m.name}</option>
                                        ))}
                                    </select>
                                </div>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    className="border-slate-800 text-slate-400"
                                    onClick={refreshModels}
                                    disabled={modelsLoading}
                                >
                                    {modelsLoading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                                    <span className="ml-2">Refresh models</span>
                                </Button>
                            </>
                        )}
                        <div className="flex items-center justify-between p-3 rounded bg-slate-900/50 border border-slate-800">
                            <div className="flex items-center gap-3">
                                <Shield className="h-4 w-4 text-slate-600" />
                                <span className="text-sm text-slate-500">LM Studio (1234)</span>
                            </div>
                            <Badge variant="outline" className="text-slate-600 border-slate-800">NOT FOUND</Badge>
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50 md:col-span-2">
                    <CardHeader>
                        <CardTitle className="text-white">Security & Audit</CardTitle>
                        <CardDescription className="text-slate-400">Session logs and identity management</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <div className="space-y-0.5">
                                    <div className="text-sm text-slate-200">Industrial Log Persistence</div>
                                    <div className="text-xs text-slate-500">Enable rotation of JSON-RPC audit logs</div>
                                </div>
                                <div className="h-6 w-10 rounded-full bg-emerald-600 relative">
                                    <div className="h-4 w-4 rounded-full bg-white absolute right-1 top-1" />
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
