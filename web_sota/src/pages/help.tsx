import { useState } from 'react';
import { HelpCircle, Monitor, Wrench, Box, Palette } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

const SECTIONS = [
    { id: 'mcp', label: 'MCP Server', icon: Monitor },
    { id: 'webapp', label: 'Webapp', icon: Monitor },
    { id: 'tools', label: 'Tools', icon: Wrench },
    { id: 'vrm', label: 'VRM Standard', icon: Box },
    { id: 'vroid', label: 'Vroid Studio', icon: Palette },
];

export function Help() {
    const [tab, setTab] = useState('mcp');

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-white flex items-center gap-2">
                    <HelpCircle className="h-8 w-8 text-blue-500" />
                    Help & Documentation
                </h1>
                <p className="text-slate-400">Multilevel help for Avatar-MCP: server, webapp, tools, VRM, and Vroid Studio.</p>
            </div>

            <Tabs value={tab} onValueChange={setTab} className="w-full">
                <TabsList className="grid w-full grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 bg-slate-900/80 border border-slate-800">
                    {SECTIONS.map((s) => (
                        <TabsTrigger key={s.id} value={s.id} className="data-[state=active]:bg-slate-800 data-[state=active]:text-white text-slate-400">
                            <s.icon className="h-4 w-4 mr-2 hidden sm:inline" />
                            {s.label}
                        </TabsTrigger>
                    ))}
                </TabsList>

                <TabsContent value="mcp" className="mt-6">
                    <Card className="border-slate-800 bg-slate-950/50">
                        <CardHeader><CardTitle className="text-white">MCP Server (Avatar-MCP)</CardTitle></CardHeader>
                        <CardContent className="space-y-4 text-slate-300 text-sm">
                            <div>
                                <h3 className="font-semibold text-slate-200 mb-1">What it is</h3>
                                <p>Avatar-MCP is a FastMCP 3.1+ server that exposes tools for loading and animating VRM avatars, OSC (Unity/VRChat), animations, emotions, and agentic workflows. It runs over stdio (for Claude/Cursor) or HTTP (this webapp backend).</p>
                            </div>
                            <div>
                                <h3 className="font-semibold text-slate-200 mb-1">How to run</h3>
                                <ul className="list-disc pl-5 space-y-1">
                                    <li><strong>Stdio (IDE)</strong>: <code className="bg-slate-800 px-1 rounded">uv run python -m avatarmcp</code> with <code className="bg-slate-800 px-1 rounded">--mcp</code> or <code className="bg-slate-800 px-1 rounded">--stdio</code>. Configure your MCP client to use that command.</li>
                                    <li><strong>HTTP (webapp)</strong>: Backend runs as <code className="bg-slate-800 px-1 rounded">uvicorn avatarmcp.http_server:app --host 127.0.0.1 --port 10793</code>. Started automatically by <code className="bg-slate-800 px-1 rounded">web_sota/start.ps1</code>.</li>
                                </ul>
                            </div>
                            <div>
                                <h3 className="font-semibold text-slate-200 mb-1">Capabilities</h3>
                                <p>Tools (avatar_manager, animation_manager, emotion_manager, avatar_agentic_workflow, etc.), prompts (avatar_workflow_guide, animation_assistant), and optional sampling (SEP-1577) when the client supports it.</p>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="webapp" className="mt-6">
                    <Card className="border-slate-800 bg-slate-950/50">
                        <CardHeader><CardTitle className="text-white">Webapp (SOTA UI)</CardTitle></CardHeader>
                        <CardContent className="space-y-4 text-slate-300 text-sm">
                            <div>
                                <h3 className="font-semibold text-slate-200 mb-1">Start</h3>
                                <p>From repo root run <code className="bg-slate-800 px-1 rounded">web_sota/start.ps1</code>. It starts the Python backend on port 10793 and the Vite frontend on 10792. Open <code className="bg-slate-800 px-1 rounded">http://127.0.0.1:10792</code>.</p>
                            </div>
                            <div>
                                <h3 className="font-semibold text-slate-200 mb-1">Bridge</h3>
                                <p>Frontend proxies <code className="bg-slate-800 px-1 rounded">/api</code> to the backend. All API calls use relative URLs so the proxy works. Endpoints: <code className="bg-slate-800 px-1 rounded">/api/v1/health</code>, <code className="bg-slate-800 px-1 rounded">/api/v1/status</code>, <code className="bg-slate-800 px-1 rounded">/api/v1/tools</code>, <code className="bg-slate-800 px-1 rounded">/api/v1/tools/execute</code>, <code className="bg-slate-800 px-1 rounded">/api/v1/avatars</code>, <code className="bg-slate-800 px-1 rounded">/api/v1/fleet/launch</code>.</p>
                            </div>
                            <div>
                                <h3 className="font-semibold text-slate-200 mb-1">Pages that use the backend</h3>
                                <ul className="list-disc pl-5">
                                    <li><strong>Overview / Dashboard</strong> – status from <code className="bg-slate-800 px-1 rounded">/api/v1/status</code></li>
                                    <li><strong>Status</strong> – health + status</li>
                                    <li><strong>Tools Hub</strong> – list tools, run any tool with JSON arguments</li>
                                    <li><strong>Workflow</strong> – run <code className="bg-slate-800 px-1 rounded">avatar_agentic_workflow</code></li>
                                    <li><strong>Avatar Registry</strong> – list from <code className="bg-slate-800 px-1 rounded">/api/v1/avatars</code></li>
                                    <li><strong>App Hub</strong> – fleet launch</li>
                                </ul>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="tools" className="mt-6">
                    <Card className="border-slate-800 bg-slate-950/50">
                        <CardHeader><CardTitle className="text-white">Tools reference</CardTitle></CardHeader>
                        <CardContent className="space-y-4 text-slate-300 text-sm">
                            <p>Avatar-MCP exposes many tools. Use the <strong>Tools Hub</strong> page to list and run them. Summary of main categories:</p>
                            <div>
                                <h3 className="font-semibold text-slate-200 mb-1">Avatar &amp; models</h3>
                                <p><code className="bg-slate-800 px-1 rounded">avatar_manager</code> – load, list, unload VRM; set active. <code className="bg-slate-800 px-1 rounded">avatar_agentic_workflow</code> – run a natural-language workflow (e.g. &quot;smile and wave&quot;) with optional LLM sampling.</p>
                            </div>
                            <div>
                                <h3 className="font-semibold text-slate-200 mb-1">Animation &amp; emotion</h3>
                                <p><code className="bg-slate-800 px-1 rounded">animation_manager</code>, <code className="bg-slate-800 px-1 rounded">emotion_manager</code> – play animations, set emotions/morphs.</p>
                            </div>
                            <div>
                                <h3 className="font-semibold text-slate-200 mb-1">Unity / VRChat / OSC</h3>
                                <p><code className="bg-slate-800 px-1 rounded">unity_integration</code>, <code className="bg-slate-800 px-1 rounded">unity_window_manager</code> – Unity bridge. OSC is used for VRChat and desktop avatar control.</p>
                            </div>
                            <div>
                                <h3 className="font-semibold text-slate-200 mb-1">Other</h3>
                                <p><code className="bg-slate-800 px-1 rounded">artifact_manager</code>, <code className="bg-slate-800 px-1 rounded">audio_manager</code>, <code className="bg-slate-800 px-1 rounded">chat_manager</code>, <code className="bg-slate-800 px-1 rounded">system_monitor</code>, etc. See Tools Hub for the full list and parameters.</p>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="vrm" className="mt-6">
                    <Card className="border-slate-800 bg-slate-950/50">
                        <CardHeader><CardTitle className="text-white">VRM standard</CardTitle></CardHeader>
                        <CardContent className="space-y-4 text-slate-300 text-sm">
                            <div>
                                <h3 className="font-semibold text-slate-200 mb-1">What is VRM</h3>
                                <p>VRM is an open format for 3D humanoid avatars (geometry, bones, blend shapes, materials). It is widely used for VTubing, VRChat, and Unity. Spec: <a href="https://vrm.dev/" target="_blank" rel="noreferrer" className="text-blue-400 hover:underline">vrm.dev</a>.</p>
                            </div>
                            <div>
                                <h3 className="font-semibold text-slate-200 mb-1">VRM 1.0 / 2.0</h3>
                                <p>Avatar-MCP supports VRM models (1.0 and 2.0). Models are loaded via <code className="bg-slate-800 px-1 rounded">avatar_manager</code> (operation: load, path: path to .vrm file). Metadata (name, etc.) is read from the file.</p>
                            </div>
                            <div>
                                <h3 className="font-semibold text-slate-200 mb-1">Creating VRM avatars</h3>
                                <p>Use tools like Vroid Studio to create and export .vrm files, then load them in Avatar-MCP. See the Vroid Studio tab for export steps.</p>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="vroid" className="mt-6">
                    <Card className="border-slate-800 bg-slate-950/50">
                        <CardHeader><CardTitle className="text-white">Vroid Studio</CardTitle></CardHeader>
                        <CardContent className="space-y-4 text-slate-300 text-sm">
                            <div>
                                <h3 className="font-semibold text-slate-200 mb-1">What it is</h3>
                                <p>Vroid Studio is a free character creation tool by Pixiv. You design a 3D avatar and export it as VRM for use in games, VTubing, and MCP-driven apps like Avatar-MCP. <a href="https://vroid.com/en/studio" target="_blank" rel="noreferrer" className="text-blue-400 hover:underline">vroid.com/en/studio</a>.</p>
                            </div>
                            <div>
                                <h3 className="font-semibold text-slate-200 mb-1">Export to VRM</h3>
                                <ul className="list-disc pl-5 space-y-1">
                                    <li>Create or open your character in Vroid Studio.</li>
                                    <li>File → Export as VRM (or similar). Choose VRM 1.0 or 2.0 if offered.</li>
                                    <li>Save the .vrm file to a folder accessible by Avatar-MCP.</li>
                                </ul>
                            </div>
                            <div>
                                <h3 className="font-semibold text-slate-200 mb-1">Using with Avatar-MCP</h3>
                                <p>Load the exported .vrm via the MCP tool <code className="bg-slate-800 px-1 rounded">avatar_manager</code> with operation <code className="bg-slate-800 px-1 rounded">load</code> and <code className="bg-slate-800 px-1 rounded">path</code> set to the file path. Or use the Tools Hub / Workflow page in this webapp to run the tool.</p>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
}
