import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Download, Upload, Shield, Globe, Cpu } from "lucide-react";

export function Settings() {

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
                        <CardDescription className="text-slate-400">Provider and model selection</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <LLMSettings />
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

function LLMSettings() {
    const [providers, setProviders] = useState<Record<string, {name:string}[]>>({});
    const [selectedProvider, setSelectedProvider] = useState("ollama");
    const [selectedModel, setSelectedModel] = useState("");
    const [status, setStatus] = useState<"loading"|"ready"|"error">("loading");
    useEffect(() => {
        fetch("/api/llm/providers").then(r => r.json()).then(d => {
            setProviders(d);
            const savedP = localStorage.getItem("llm_provider") || "ollama";
            const savedM = localStorage.getItem("llm_model") || "";
            setSelectedProvider(savedP);
            const models = d[savedP === "ollama" ? "ollama" : "lm_studio"] || [];
            setSelectedModel(savedM && models.some((m:{name:string}) => m.name === savedM) ? savedM : (models[0]?.name || ""));
            setStatus(models.length > 0 ? "ready" : "error");
        }).catch(() => {
            setProviders({ ollama: [{name:"llama3.2:3b"}] });
            setSelectedModel(localStorage.getItem("llm_model") || "llama3.2:3b");
            setStatus("ready");
        });
    }, []);
    const save = (p:string, m:string) => { localStorage.setItem("llm_provider", p); localStorage.setItem("llm_model", m); };
    const models = providers[selectedProvider === "ollama" ? "ollama" : "lm_studio"] || [];
    return (
        <div className="space-y-3">
            <select
                className="h-9 w-full rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100"
                value={selectedProvider}
                onChange={(e) => { setSelectedProvider(e.target.value); save(e.target.value, ""); }}
            >
                <option value="ollama">Ollama</option>
                <option value="lm_studio">LM Studio</option>
            </select>
            <select
                className="h-9 w-full rounded-md border border-slate-800 bg-slate-900 px-3 text-sm text-slate-100"
                value={selectedModel}
                onChange={(e) => { setSelectedModel(e.target.value); save(selectedProvider, e.target.value); }}
            >
                {models.map((m) => <option key={m.name} value={m.name}>{m.name}</option>)}
            </select>
        </div>
    );
}
