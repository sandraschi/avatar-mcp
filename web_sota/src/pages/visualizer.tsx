import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Eye, GitMerge, Activity, Box, Cpu } from "lucide-react";

interface BoneState {
  name: string;
  rotation: { x: number; y: number; z: number };
  position: { x: number; y: number; z: number };
}

interface BlendShape {
  name: string;
  value: number;
}

interface VRMData {
  model_name: string;
  version: string;
  bone_count: number;
  mesh_count: number;
  blend_shape_count: number;
  vram_mb: number;
  poly_count: number;
}

interface VisualizerData {
  vrm: VRMData | null;
  bones: BoneState[];
  blend_shapes: BlendShape[];
  fps: number;
  frame: number;
  osc_active: boolean;
  last_update: string;
}

const EMPTY_DATA: VisualizerData = {
  vrm: null,
  bones: [],
  blend_shapes: [],
  fps: 0,
  frame: 0,
  osc_active: false,
  last_update: "Never",
};

function StatBar({ value, max, color }: { value: number; max: number; color: string }) {
  const pct = Math.min(100, Math.round((value / max) * 100));
  return (
    <div className="h-1 w-full bg-slate-800 rounded-full overflow-hidden">
      <div className={`h-full ${color} transition-all duration-500`} style={{ width: `${pct}%` }} />
    </div>
  );
}

export function Visualizer() {
  const [data, setData] = useState<VisualizerData>(EMPTY_DATA);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch("http://127.0.0.1:10793/api/v1/visualizer");
        if (res.ok) {
          const d = await res.json();
          setData(d);
        }
      } catch {
        // backend offline - keep defaults
      }
      setTick(t => t + 1);
    };
    fetchData();
    const iv = setInterval(fetchData, 2000);
    return () => clearInterval(iv);
  }, []);

  const activeBones = data.bones.filter(
    b => Math.abs(b.rotation.x) > 1 || Math.abs(b.rotation.y) > 1 || Math.abs(b.rotation.z) > 1
  );

  const activeBlends = data.blend_shapes
    .filter(b => b.value > 0.01)
    .sort((a, b) => b.value - a.value)
    .slice(0, 12);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
            Avatar Visualizer
          </h2>
          <p className="text-slate-400">Real-time VRM state · Bone map · Blend shapes</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className={data.osc_active ? "border-emerald-500/20 text-emerald-400" : "border-slate-700 text-slate-500"}>
            {data.osc_active ? "OSC LIVE" : "OSC IDLE"}
          </Badge>
          <Badge variant="outline" className="border-slate-700 text-slate-400 font-mono">
            {data.fps} FPS · Frame {data.frame}
          </Badge>
        </div>
      </div>

      {/* VRM Model Info */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Model", value: data.vrm?.model_name ?? "—", sub: `VRM ${data.vrm?.version ?? "—"}`, icon: Box, color: "text-purple-400" },
          { label: "Bones", value: data.vrm?.bone_count ?? 0, sub: `${activeBones.length} active`, icon: GitMerge, color: "text-blue-400" },
          { label: "Blend Shapes", value: data.vrm?.blend_shape_count ?? 0, sub: `${activeBlends.length} active`, icon: Activity, color: "text-pink-400" },
          { label: "VRAM", value: data.vrm ? `${data.vrm.vram_mb} MB` : "—", sub: `${data.vrm?.poly_count?.toLocaleString() ?? 0} polys`, icon: Cpu, color: "text-orange-400" },
        ].map(({ label, value, sub, icon: Icon, color }) => (
          <Card key={label} className="border-slate-800 bg-slate-950/40 backdrop-blur-xl hover:border-slate-700 transition-all">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">{label}</CardTitle>
              <Icon className={`h-4 w-4 ${color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white font-mono">{value}</div>
              <p className="text-xs text-slate-500 mt-1">{sub}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {/* Active Bone States */}
        <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <GitMerge className="h-4 w-4 text-blue-400" />
              Active Bone States
              <span className="ml-auto text-xs text-slate-500 font-mono">{activeBones.length} / {data.vrm?.bone_count ?? 0}</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {activeBones.length === 0 ? (
              <div className="h-32 flex items-center justify-center text-slate-600 text-sm font-mono">
                No bones in active rotation
              </div>
            ) : (
              <div className="space-y-3 max-h-64 overflow-y-auto pr-1">
                {activeBones.map(bone => (
                  <div key={bone.name} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-300 font-mono">{bone.name}</span>
                      <span className="text-slate-500 font-mono text-right">
                        {bone.rotation.x.toFixed(1)}° {bone.rotation.y.toFixed(1)}° {bone.rotation.z.toFixed(1)}°
                      </span>
                    </div>
                    <div className="grid grid-cols-3 gap-1">
                      <StatBar value={Math.abs(bone.rotation.x)} max={180} color="bg-red-500/60" />
                      <StatBar value={Math.abs(bone.rotation.y)} max={180} color="bg-green-500/60" />
                      <StatBar value={Math.abs(bone.rotation.z)} max={180} color="bg-blue-500/60" />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Blend Shape Activity */}
        <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Eye className="h-4 w-4 text-pink-400" />
              Blend Shape Activity
              <span className="ml-auto text-xs text-slate-500 font-mono">Top 12</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {activeBlends.length === 0 ? (
              <div className="h-32 flex items-center justify-center text-slate-600 text-sm font-mono">
                No active blend shapes
              </div>
            ) : (
              <div className="space-y-3 max-h-64 overflow-y-auto pr-1">
                {activeBlends.map(bs => (
                  <div key={bs.name} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-300 font-mono">{bs.name}</span>
                      <span className="text-pink-400 font-mono">{Math.round(bs.value * 100)}%</span>
                    </div>
                    <StatBar value={bs.value} max={1} color="bg-pink-500/60" />
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* All Bones Grid */}
      <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Activity className="h-4 w-4 text-slate-400" />
            Full Skeleton Map
          </CardTitle>
        </CardHeader>
        <CardContent>
          {data.bones.length === 0 ? (
            <div className="h-24 flex items-center justify-center text-slate-600 text-sm font-mono">
              No VRM model loaded · Connect Unity or VRChat to stream bone data
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
              {data.bones.map(bone => {
                const magnitude = Math.sqrt(
                  bone.rotation.x ** 2 + bone.rotation.y ** 2 + bone.rotation.z ** 2
                );
                const isActive = magnitude > 1;
                return (
                  <div
                    key={bone.name}
                    className={`px-2 py-1 rounded text-xs font-mono border transition-all ${
                      isActive
                        ? "border-blue-500/40 bg-blue-500/10 text-blue-300"
                        : "border-slate-800 text-slate-600"
                    }`}
                  >
                    {bone.name}
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
