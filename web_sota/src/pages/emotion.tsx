import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Heart, Smile, Frown, Zap, Meh, RefreshCw } from "lucide-react";

interface EmotionState {
  dominant: string;
  intensity: number;
  expressions: Record<string, number>;
  auto_blink: boolean;
  auto_eye_movement: boolean;
  voice_reactive: boolean;
}

const EMOTION_PRESETS = [
  { name: "Neutral", icon: Meh, color: "slate", key: "neutral" },
  { name: "Happy", icon: Smile, color: "yellow", key: "joy" },
  { name: "Sad", icon: Frown, color: "blue", key: "sorrow" },
  { name: "Angry", icon: Zap, color: "red", key: "angry" },
  { name: "Surprised", icon: Heart, color: "pink", key: "surprised" },
  { name: "Disgusted", icon: Frown, color: "green", key: "disgust" },
  { name: "Fearful", icon: Zap, color: "purple", key: "fear" },
];

const EXPRESSION_SLIDERS = [
  { label: "Joy", key: "joy" },
  { label: "Sorrow", key: "sorrow" },
  { label: "Angry", key: "angry" },
  { label: "Surprised", key: "surprised" },
  { label: "Disgust", key: "disgust" },
  { label: "Fear", key: "fear" },
  { label: "Blink", key: "blink" },
  { label: "Blink L", key: "blink_l" },
  { label: "Blink R", key: "blink_r" },
  { label: "Look Up", key: "look_up" },
  { label: "Look Down", key: "look_down" },
  { label: "Look Left", key: "look_left" },
  { label: "Look Right", key: "look_right" },
  { label: "Mouth A", key: "mouth_a" },
  { label: "Mouth I", key: "mouth_i" },
  { label: "Mouth U", key: "mouth_u" },
  { label: "Mouth E", key: "mouth_e" },
  { label: "Mouth O", key: "mouth_o" },
];

const colorMap: Record<string, { btn: string; bar: string }> = {
  slate: { btn: "border-slate-600 text-slate-400 bg-slate-800/30", bar: "bg-slate-400" },
  yellow: { btn: "border-yellow-500/40 text-yellow-400 bg-yellow-500/10", bar: "bg-yellow-400" },
  blue: { btn: "border-blue-500/40 text-blue-400 bg-blue-500/10", bar: "bg-blue-400" },
  red: { btn: "border-red-500/40 text-red-400 bg-red-500/10", bar: "bg-red-400" },
  pink: { btn: "border-pink-500/40 text-pink-400 bg-pink-500/10", bar: "bg-pink-400" },
  green: { btn: "border-green-500/40 text-green-400 bg-green-500/10", bar: "bg-green-400" },
  purple: { btn: "border-purple-500/40 text-purple-400 bg-purple-500/10", bar: "bg-purple-400" },
};

export function Emotion() {
  const [state, setState] = useState<EmotionState>({
    dominant: "neutral",
    intensity: 0,
    expressions: Object.fromEntries(EXPRESSION_SLIDERS.map(s => [s.key, 0])),
    auto_blink: true,
    auto_eye_movement: true,
    voice_reactive: false,
  });
  const [activePreset, setActivePreset] = useState("neutral");

  useEffect(() => {
    fetch("http://127.0.0.1:10793/api/v1/emotion/state")
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d) setState(d); })
      .catch(() => { });

    const iv = setInterval(() => {
      fetch("http://127.0.0.1:10793/api/v1/emotion/state")
        .then(r => r.ok ? r.json() : null)
        .then(d => { if (d) setState(d); })
        .catch(() => { });
    }, 2000);
    return () => clearInterval(iv);
  }, []);

  const applyPreset = (key: string, name: string) => {
    setActivePreset(key);
    const exprs = Object.fromEntries(EXPRESSION_SLIDERS.map(s => [s.key, s.key === key ? 1.0 : 0]));
    setState(p => ({ ...p, expressions: exprs, dominant: key, intensity: 1.0 }));
    fetch("http://127.0.0.1:10793/api/v1/call", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "emotion_manager",
        arguments: { operation: "apply_personality", preset: key }
      }),
    }).catch(() => { });
  };

  const setExpr = (key: string, val: number) => {
    setState(p => ({ ...p, expressions: { ...p.expressions, [key]: val } }));
    fetch("http://127.0.0.1:10793/api/v1/call", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "emotion_manager",
        arguments: { operation: "micro_expressions", key, value: val }
      }),
    }).catch(() => { });
  };

  const toggleFlag = (flag: "auto_blink" | "auto_eye_movement" | "voice_reactive") => {
    const val = !state[flag];
    setState(p => ({ ...p, [flag]: val }));
    fetch("http://127.0.0.1:10793/api/v1/call", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "emotion_manager",
        arguments: { operation: "state_machine", [flag]: val }
      }),
    }).catch(() => { });
  };

  const resetAll = () => {
    const exprs = Object.fromEntries(EXPRESSION_SLIDERS.map(s => [s.key, 0]));
    setState(p => ({ ...p, expressions: exprs, dominant: "neutral", intensity: 0 }));
    setActivePreset("neutral");
    fetch("http://127.0.0.1:10793/api/v1/emotion/reset", { method: "POST" }).catch(() => { });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-yellow-400 to-pink-500 bg-clip-text text-transparent">
            Emotion &amp; Expression
          </h2>
          <p className="text-slate-400">Facial expressions · Blend shapes · Auto-behavior</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="border-yellow-500/20 text-yellow-400 font-mono capitalize">
            {state.dominant} · {Math.round(state.intensity * 100)}%
          </Badge>
          <button onClick={resetAll} className="px-3 py-1 text-xs border border-slate-700 text-slate-500 rounded font-mono hover:text-red-400 hover:border-red-500/30 transition-all flex items-center gap-1">
            <RefreshCw className="h-3 w-3" /> Reset
          </button>
        </div>
      </div>

      {/* Emotion Presets */}
      <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Smile className="h-4 w-4 text-yellow-400" />
            Emotion Presets
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 md:grid-cols-7 gap-3">
            {EMOTION_PRESETS.map(({ name, icon: Icon, color, key }) => {
              const isActive = activePreset === key;
              const c = colorMap[color];
              return (
                <button
                  key={key}
                  onClick={() => applyPreset(key, name)}
                  className={`flex flex-col items-center gap-2 p-3 rounded-xl border transition-all ${isActive ? c.btn : "border-slate-800 text-slate-600 hover:border-slate-700 hover:text-slate-400"
                    }`}
                >
                  <Icon className="h-6 w-6" />
                  <span className="text-xs font-mono">{name}</span>
                </button>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Expression Sliders */}
      <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Heart className="h-4 w-4 text-pink-400" />
            Fine Expression Control
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {EXPRESSION_SLIDERS.map(({ label, key }) => {
              const val = state.expressions[key] ?? 0;
              return (
                <div key={key} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-400 font-mono">{label}</span>
                    <span className="text-slate-500 font-mono">{Math.round(val * 100)}%</span>
                  </div>
                  <input
                    type="range"
                    min={0}
                    max={1}
                    step={0.01}
                    value={val}
                    onChange={e => setExpr(key, Number(e.target.value))}
                    className="w-full h-1 accent-yellow-400"
                  />
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Auto-Behavior Flags */}
      <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Zap className="h-4 w-4 text-orange-400" />
            Auto-Behavior
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            {(["auto_blink", "auto_eye_movement", "voice_reactive"] as const).map(flag => {
              const labels: Record<string, string> = {
                auto_blink: "Auto Blink",
                auto_eye_movement: "Auto Eye Movement",
                voice_reactive: "Voice Reactive Mouth",
              };
              const on = state[flag];
              return (
                <button
                  key={flag}
                  onClick={() => toggleFlag(flag)}
                  className={`px-4 py-2 rounded-lg border text-sm font-mono transition-all ${on
                      ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-400"
                      : "border-slate-700 text-slate-500 hover:border-slate-600"
                    }`}
                >
                  {on ? "ON" : "OFF"} · {labels[flag]}
                </button>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
