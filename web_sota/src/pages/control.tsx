import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Gamepad2, RotateCcw, Sliders, Hand, RefreshCw } from "lucide-react";

const BONE_GROUPS = [
  {
    group: "Head",
    bones: ["Head", "Neck", "Jaw"],
    color: "emerald",
  },
  {
    group: "Left Arm",
    bones: ["LeftUpperArm", "LeftLowerArm", "LeftHand"],
    color: "blue",
  },
  {
    group: "Right Arm",
    bones: ["RightUpperArm", "RightLowerArm", "RightHand"],
    color: "purple",
  },
  {
    group: "Spine",
    bones: ["Spine", "Chest", "UpperChest"],
    color: "orange",
  },
];

const MORPH_TARGETS = [
  { name: "Joy", key: "joy" },
  { name: "Sorrow", key: "sorrow" },
  { name: "Angry", key: "angry" },
  { name: "Surprised", key: "surprised" },
  { name: "Blink", key: "blink" },
  { name: "BlinkL", key: "blink_l" },
  { name: "BlinkR", key: "blink_r" },
  { name: "LookUp", key: "look_up" },
  { name: "LookDown", key: "look_down" },
  { name: "LookLeft", key: "look_left" },
  { name: "LookRight", key: "look_right" },
  { name: "Neutral", key: "neutral" },
];

const POSE_PRESETS = [
  "T-Pose", "A-Pose", "Wave", "Point", "Bow", "Dance Idle", "Victory", "Thinking",
];

type BoneRotations = Record<string, { x: number; y: number; z: number }>;
type MorphValues = Record<string, number>;

export function Control() {
  const [boneRotations, setBoneRotations] = useState<BoneRotations>({});
  const [morphValues, setMorphValues] = useState<MorphValues>({});
  const [activePreset, setActivePreset] = useState<string | null>(null);
  const [sendStatus, setSendStatus] = useState<string>("idle");
  const [activeAvatar, setActiveAvatar] = useState<string>("Loading...");

  useEffect(() => {
    fetch("http://127.0.0.1:10793/api/v1/status")
      .then(r => r.ok ? r.json() : null)
      .then(d => {
        if (d) setActiveAvatar(d.active_avatars > 0 ? `Avatar #${d.active_avatars}` : "No Avatar Loaded");
      })
      .catch(() => setActiveAvatar("Offline"));

    const init: MorphValues = {};
    MORPH_TARGETS.forEach(m => { init[m.key] = 0; });
    setMorphValues(init);
  }, []);

  const getBoneVal = (bone: string, axis: "x" | "y" | "z") =>
    boneRotations[bone]?.[axis] ?? 0;

  const setBoneAxis = (bone: string, axis: "x" | "y" | "z", val: number) => {
    setBoneRotations(prev => ({
      ...prev,
      [bone]: { ...(prev[bone] ?? { x: 0, y: 0, z: 0 }), [axis]: val },
    }));
  };

  const setMorph = (key: string, val: number) => {
    setMorphValues(prev => ({ ...prev, [key]: val }));
  };

  const applyPreset = (preset: string) => {
    setActivePreset(preset);
    setSendStatus("sending");
    fetch("http://127.0.0.1:10793/api/v1/call", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "animation_manager",
        arguments: { operation: "play", animation_name: preset }
      }),
    })
      .then(r => setSendStatus(r.ok ? "ok" : "error"))
      .catch(() => setSendStatus("error"))
      .finally(() => setTimeout(() => setSendStatus("idle"), 2000));
  };

  const sendBoneData = () => {
    setSendStatus("sending");
    fetch("http://127.0.0.1:10793/api/v1/call", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "unity_integration",
        arguments: { operation: "control_animation", action: "play", bones: boneRotations }
      }),
    })
      .then(r => setSendStatus(r.ok ? "ok" : "error"))
      .catch(() => setSendStatus("error"))
      .finally(() => setTimeout(() => setSendStatus("idle"), 2000));
  };

  const sendMorphData = () => {
    fetch("http://127.0.0.1:10793/api/v1/call", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "unity_integration",
        arguments: { operation: "set_expression", expressions: morphValues }
      }),
    }).catch(() => { });
  };

  const colorMap: Record<string, string> = {
    emerald: "text-emerald-400 border-emerald-500/20",
    blue: "text-blue-400 border-blue-500/20",
    purple: "text-purple-400 border-purple-500/20",
    orange: "text-orange-400 border-orange-500/20",
  };

  const statusColor = sendStatus === "ok" ? "text-emerald-400" : sendStatus === "error" ? "text-red-400" : "text-slate-400";

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-blue-500 bg-clip-text text-transparent">
            Control Center
          </h2>
          <p className="text-slate-400">Bone manipulation · Morph targets · Pose presets</p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="border-emerald-500/20 text-emerald-400">
            {activeAvatar}
          </Badge>
          <span className={`text-xs font-mono ${statusColor}`}>
            {sendStatus === "sending" ? "Sending..." : sendStatus === "ok" ? "Sent" : sendStatus === "error" ? "Error" : "Ready"}
          </span>
        </div>
      </div>

      {/* Pose Presets */}
      <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Gamepad2 className="h-4 w-4 text-emerald-400" />
            Pose Presets
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {POSE_PRESETS.map(preset => (
              <button
                key={preset}
                onClick={() => applyPreset(preset)}
                className={`px-3 py-1.5 rounded-md text-sm font-mono transition-all border ${activePreset === preset
                  ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-300"
                  : "border-slate-700 text-slate-400 hover:border-slate-600 hover:text-slate-200"
                  }`}
              >
                {preset}
              </button>
            ))}
            <button
              onClick={() => { setActivePreset(null); setBoneRotations({}); }}
              className="px-3 py-1.5 rounded-md text-sm font-mono border border-slate-700 text-slate-500 hover:text-red-400 hover:border-red-500/30 transition-all flex items-center gap-1"
            >
              <RotateCcw className="h-3 w-3" /> Reset
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Bone Controls */}
      <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Sliders className="h-4 w-4 text-blue-400" />
            Bone Rotations
            <button
              onClick={sendBoneData}
              className="ml-auto px-3 py-1 rounded-md text-xs bg-blue-500/10 text-blue-400 border border-blue-500/20 hover:bg-blue-500/20 transition-all flex items-center gap-1"
            >
              <RefreshCw className="h-3 w-3" /> Apply
            </button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            {BONE_GROUPS.map(({ group, bones, color }) => (
              <div key={group} className="space-y-3">
                <div className={`text-xs font-mono font-bold uppercase tracking-widest ${colorMap[color].split(" ")[0]}`}>
                  {group}
                </div>
                {bones.map(bone => (
                  <div key={bone} className="space-y-1">
                    <div className="text-xs text-slate-500 font-mono">{bone}</div>
                    {(["x", "y", "z"] as const).map(axis => (
                      <div key={axis} className="flex items-center gap-2">
                        <span className="w-4 text-xs text-slate-600 font-mono">{axis}</span>
                        <input
                          type="range"
                          title={`Rotation axis ${axis} for ${bone}`}
                          min={-180}
                          max={180}
                          value={getBoneVal(bone, axis)}
                          onChange={e => setBoneAxis(bone, axis, Number(e.target.value))}
                          className="flex-1 h-1 accent-blue-400"
                        />
                        <span className="w-10 text-right text-xs text-slate-400 font-mono">
                          {getBoneVal(bone, axis)}°
                        </span>
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Morph Targets */}
      <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Hand className="h-4 w-4 text-purple-400" />
            Blend Shapes / Morph Targets
            <button
              onClick={sendMorphData}
              className="ml-auto px-3 py-1 rounded-md text-xs bg-purple-500/10 text-purple-400 border border-purple-500/20 hover:bg-purple-500/20 transition-all flex items-center gap-1"
            >
              <RefreshCw className="h-3 w-3" /> Apply
            </button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {MORPH_TARGETS.map(({ name, key }) => (
              <div key={key} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400 font-mono">{name}</span>
                  <span className="text-slate-500 font-mono">{Math.round((morphValues[key] ?? 0) * 100)}%</span>
                </div>
                <input
                  type="range"
                  title={`Morph target: ${name}`}
                  min={0}
                  max={1}
                  step={0.01}
                  value={morphValues[key] ?? 0}
                  onChange={e => setMorph(key, Number(e.target.value))}
                  className="w-full h-1 accent-purple-400"
                />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
