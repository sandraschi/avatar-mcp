import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Mic, Volume2, VolumeX, Music, Radio, Sliders } from "lucide-react";

interface AudioState {
  mic_active: boolean;
  mic_volume: number; // 0-1
  tts_active: boolean;
  tts_voice: string;
  tts_speed: number;
  tts_pitch: number;
  spatial_audio: boolean;
  voice_changer: boolean;
  voice_changer_preset: string;
  output_device: string;
  ambient_volume: number;
}

const TTS_VOICES = [
  "Alloy", "Echo", "Fable", "Onyx", "Nova", "Shimmer", "VRoid_Female_JP", "VRoid_Male_EN",
];

const VOICE_CHANGER_PRESETS = [
  "Bypass", "Anime Female", "Anime Male", "Deep", "High Pitch", "Robot", "Radio", "Chipmunk",
];

const AMBIENT_TRACKS = [
  { name: "Silence", key: "none" },
  { name: "Soft Chatter", key: "ambient_chatter" },
  { name: "City Ambience", key: "city" },
  { name: "Nature Forest", key: "forest" },
  { name: "Lo-fi Beats", key: "lofi" },
  { name: "Synthwave", key: "synthwave" },
];

function VUMeter({ level }: { level: number }) {
  const bars = 12;
  return (
    <div className="flex items-end gap-0.5 h-8">
      {Array.from({ length: bars }).map((_, i) => {
        const threshold = (i + 1) / bars;
        const active = level >= threshold;
        const color = i < 8 ? "bg-emerald-500" : i < 10 ? "bg-yellow-500" : "bg-red-500";
        return (
          <div
            key={i}
            className={`w-2 transition-all duration-75 ${active ? color : "bg-slate-800"}`}
            style={{ height: `${40 + i * 5}%` }}
          />
        );
      })}
    </div>
  );
}

export function Audio() {
  const [audioState, setAudioState] = useState<AudioState>({
    mic_active: false,
    mic_volume: 0,
    tts_active: false,
    tts_voice: "Nova",
    tts_speed: 1.0,
    tts_pitch: 1.0,
    spatial_audio: true,
    voice_changer: false,
    voice_changer_preset: "Bypass",
    output_device: "Default",
    ambient_volume: 0,
  });
  const [ttsText, setTtsText] = useState("");
  const [ttsStatus, setTtsStatus] = useState<"idle" | "generating" | "playing" | "error">("idle");

  useEffect(() => {
    fetch("http://127.0.0.1:10793/api/v1/audio/state")
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d) setAudioState(d); })
      .catch(() => { });

    const iv = setInterval(() => {
      fetch("http://127.0.0.1:10793/api/v1/audio/state")
        .then(r => r.ok ? r.json() : null)
        .then(d => { if (d) setAudioState(d); })
        .catch(() => { });
    }, 500);
    return () => clearInterval(iv);
  }, []);

  const patch = (updates: Partial<AudioState>) => {
    setAudioState(p => ({ ...p, ...updates }));
    fetch("http://127.0.0.1:10793/api/v1/audio/config", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updates),
    }).catch(() => { });
  };

  const sendTTS = () => {
    if (!ttsText.trim()) return;
    setTtsStatus("generating");
    fetch("http://127.0.0.1:10793/api/v1/call", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "audio_manager",
        arguments: {
          operation: "singing_synthesize",
          lyrics: ttsText,
          voice_style: audioState.tts_voice,
          tempo: Math.round(audioState.tts_speed * 120)
        }
      }),
    })
      .then(r => { setTtsStatus(r.ok ? "playing" : "error"); })
      .catch(() => setTtsStatus("error"))
      .finally(() => setTimeout(() => setTtsStatus("idle"), 3000));
  };

  const ttsStatusColor = { idle: "text-slate-500", generating: "text-yellow-400", playing: "text-emerald-400", error: "text-red-400" }[ttsStatus];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-cyan-500 bg-clip-text text-transparent">
            Audio Pipeline
          </h2>
          <p className="text-slate-400">Microphone · TTS · Voice changer · Spatial audio</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className={audioState.mic_active ? "border-emerald-500/20 text-emerald-400" : "border-slate-700 text-slate-500"}>
            {audioState.mic_active ? "MIC LIVE" : "MIC OFF"}
          </Badge>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {/* Microphone */}
        <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Mic className="h-4 w-4 text-blue-400" />
              Microphone Input
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-300">Microphone Active</span>
              <button
                onClick={() => patch({ mic_active: !audioState.mic_active })}
                className={`px-3 py-1 rounded text-xs font-mono border transition-all ${audioState.mic_active
                    ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-400"
                    : "border-slate-700 text-slate-500"
                  }`}
              >
                {audioState.mic_active ? "ACTIVE" : "MUTED"}
              </button>
            </div>
            <div>
              <div className="flex justify-between text-xs text-slate-500 mb-2">
                <span>Input Level</span>
              </div>
              <VUMeter level={audioState.mic_volume} />
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-xs text-slate-500">
                <span>Gain</span>
                <span className="font-mono">{Math.round(audioState.mic_volume * 100)}%</span>
              </div>
              <input
                type="range" min={0} max={1} step={0.01}
                value={audioState.mic_volume}
                onChange={e => patch({ mic_volume: Number(e.target.value) })}
                className="w-full h-1 accent-blue-400"
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-300">Voice Changer</span>
              <button
                onClick={() => patch({ voice_changer: !audioState.voice_changer })}
                className={`px-3 py-1 rounded text-xs font-mono border transition-all ${audioState.voice_changer
                    ? "bg-cyan-500/20 border-cyan-500/40 text-cyan-400"
                    : "border-slate-700 text-slate-500"
                  }`}
              >
                {audioState.voice_changer ? "ON" : "OFF"}
              </button>
            </div>
            {audioState.voice_changer && (
              <div className="flex flex-wrap gap-2">
                {VOICE_CHANGER_PRESETS.map(p => (
                  <button
                    key={p}
                    onClick={() => patch({ voice_changer_preset: p })}
                    className={`px-2 py-1 rounded text-xs font-mono border transition-all ${audioState.voice_changer_preset === p
                        ? "border-cyan-500/40 bg-cyan-500/10 text-cyan-400"
                        : "border-slate-700 text-slate-600 hover:text-slate-400"
                      }`}
                  >
                    {p}
                  </button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* TTS */}
        <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Volume2 className="h-4 w-4 text-cyan-400" />
              Text-to-Speech
              <span className={`ml-auto text-xs font-mono ${ttsStatusColor}`}>
                {ttsStatus === "generating" ? "Generating..." : ttsStatus === "playing" ? "Playing" : ttsStatus === "error" ? "Error" : "Ready"}
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <textarea
              value={ttsText}
              onChange={e => setTtsText(e.target.value)}
              placeholder="Enter text for avatar to speak..."
              className="w-full h-20 bg-slate-900 border border-slate-700 rounded-md px-3 py-2 text-sm text-slate-300 placeholder-slate-600 focus:outline-none focus:border-slate-500 resize-none"
            />
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-xs text-slate-500 block mb-1">Voice</label>
                <select
                  value={audioState.tts_voice}
                  onChange={e => patch({ tts_voice: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-sm text-slate-300 focus:outline-none"
                >
                  {TTS_VOICES.map(v => <option key={v} value={v}>{v}</option>)}
                </select>
              </div>
              <div>
                <label className="text-xs text-slate-500 block mb-1">Speed · {audioState.tts_speed}x</label>
                <input
                  type="range" min={0.5} max={2.0} step={0.1}
                  value={audioState.tts_speed}
                  onChange={e => patch({ tts_speed: Number(e.target.value) })}
                  className="w-full h-1 accent-cyan-400 mt-2"
                />
              </div>
            </div>
            <div>
              <label className="text-xs text-slate-500 block mb-1">Pitch · {audioState.tts_pitch.toFixed(1)}</label>
              <input
                type="range" min={0.5} max={2.0} step={0.05}
                value={audioState.tts_pitch}
                onChange={e => patch({ tts_pitch: Number(e.target.value) })}
                className="w-full h-1 accent-cyan-400"
              />
            </div>
            <button
              onClick={sendTTS}
              disabled={ttsStatus === "generating"}
              className="w-full py-2 rounded-lg bg-cyan-500/20 border border-cyan-500/40 text-cyan-400 text-sm font-mono hover:bg-cyan-500/30 transition-all disabled:opacity-40"
            >
              Speak
            </button>
          </CardContent>
        </Card>
      </div>

      {/* Spatial Audio + Ambient */}
      <div className="grid gap-4 lg:grid-cols-2">
        <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Radio className="h-4 w-4 text-purple-400" />
              Spatial Audio
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-slate-300">3D Positional Audio</div>
                <div className="text-xs text-slate-600">VRChat OSC-synced head position</div>
              </div>
              <button
                onClick={() => patch({ spatial_audio: !audioState.spatial_audio })}
                className={`px-3 py-1 rounded text-xs font-mono border transition-all ${audioState.spatial_audio
                    ? "bg-purple-500/20 border-purple-500/40 text-purple-400"
                    : "border-slate-700 text-slate-500"
                  }`}
              >
                {audioState.spatial_audio ? "ENABLED" : "DISABLED"}
              </button>
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-xs text-slate-500">
                <span>Output Device</span>
              </div>
              <div className="text-sm text-slate-400 font-mono bg-slate-900 border border-slate-800 rounded px-3 py-2">
                {audioState.output_device}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Music className="h-4 w-4 text-orange-400" />
              Ambient Audio
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-2">
              {AMBIENT_TRACKS.map(track => (
                <button
                  key={track.key}
                  className="px-2 py-1.5 rounded text-xs font-mono border border-slate-700 text-slate-500 hover:border-slate-600 hover:text-slate-300 transition-all text-left"
                >
                  {track.name}
                </button>
              ))}
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-xs text-slate-500">
                <span>Ambient Volume</span>
                <span className="font-mono">{Math.round(audioState.ambient_volume * 100)}%</span>
              </div>
              <input
                type="range" min={0} max={1} step={0.01}
                value={audioState.ambient_volume}
                onChange={e => patch({ ambient_volume: Number(e.target.value) })}
                className="w-full h-1 accent-orange-400"
              />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
