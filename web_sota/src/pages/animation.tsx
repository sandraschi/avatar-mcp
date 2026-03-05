import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Play, Square, SkipForward, SkipBack, Repeat, Clock, Layers } from "lucide-react";

interface AnimationClip {
  name: string;
  duration_sec: number;
  loop: boolean;
  category: string;
  tags: string[];
}

interface PlaybackState {
  current_clip: string | null;
  playing: boolean;
  progress: number; // 0-1
  speed: number;
  loop: boolean;
}

const MOCK_CLIPS: AnimationClip[] = [
  { name: "Idle_Breathe", duration_sec: 3.0, loop: true, category: "Idle", tags: ["idle", "ambient"] },
  { name: "Idle_LookAround", duration_sec: 5.5, loop: true, category: "Idle", tags: ["idle", "ambient"] },
  { name: "Wave_Friendly", duration_sec: 2.1, loop: false, category: "Greet", tags: ["gesture", "social"] },
  { name: "Bow_Formal", duration_sec: 2.8, loop: false, category: "Greet", tags: ["gesture", "social"] },
  { name: "Dance_BeatSync", duration_sec: 8.0, loop: true, category: "Dance", tags: ["dance", "social"] },
  { name: "Dance_Sway", duration_sec: 4.0, loop: true, category: "Dance", tags: ["dance", "ambient"] },
  { name: "Think_HeadTilt", duration_sec: 3.2, loop: false, category: "Emote", tags: ["emote"] },
  { name: "Victory_Pose", duration_sec: 2.0, loop: false, category: "Emote", tags: ["emote", "social"] },
  { name: "Point_Forward", duration_sec: 1.5, loop: false, category: "Gesture", tags: ["gesture"] },
  { name: "Clap_Enthusiastic", duration_sec: 2.5, loop: true, category: "Gesture", tags: ["gesture", "social"] },
  { name: "Walk_Cycle", duration_sec: 1.0, loop: true, category: "Locomotion", tags: ["loco"] },
  { name: "Run_Cycle", duration_sec: 0.7, loop: true, category: "Locomotion", tags: ["loco"] },
];

const CATEGORIES = ["All", "Idle", "Greet", "Dance", "Emote", "Gesture", "Locomotion"];

const categoryColors: Record<string, string> = {
  Idle: "text-slate-400 border-slate-700",
  Greet: "text-emerald-400 border-emerald-500/30",
  Dance: "text-pink-400 border-pink-500/30",
  Emote: "text-purple-400 border-purple-500/30",
  Gesture: "text-blue-400 border-blue-500/30",
  Locomotion: "text-orange-400 border-orange-500/30",
};

function fmtDur(sec: number) {
  const s = Math.floor(sec);
  const ms = Math.round((sec - s) * 10);
  return `${s}.${ms}s`;
}

export function Animation() {
  const [clips, setClips] = useState<AnimationClip[]>(MOCK_CLIPS);
  const [playback, setPlayback] = useState<PlaybackState>({
    current_clip: null,
    playing: false,
    progress: 0,
    speed: 1.0,
    loop: false,
  });
  const [category, setCategory] = useState("All");
  const [search, setSearch] = useState("");

  useEffect(() => {
    // Try to fetch real clip list from backend
    fetch("http://127.0.0.1:10793/api/v1/animation/clips")
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.clips) setClips(d.clips); })
      .catch(() => { }); // falls back to mock data

    fetch("http://127.0.0.1:10793/api/v1/animation/playback")
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d) setPlayback(d); })
      .catch(() => { });

    const iv = setInterval(() => {
      fetch("http://127.0.0.1:10793/api/v1/animation/playback")
        .then(r => r.ok ? r.json() : null)
        .then(d => { if (d) setPlayback(d); })
        .catch(() => { });
    }, 1000);
    return () => clearInterval(iv);
  }, []);

  const sendCmd = (action: string, payload: Record<string, unknown> = {}) => {
    fetch("http://127.0.0.1:10793/api/v1/call", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "animation_manager",
        arguments: { operation: action, ...payload }
      }),
    }).catch(() => { });
  };

  const playClip = (name: string) => {
    setPlayback(p => ({ ...p, current_clip: name, playing: true, progress: 0 }));
    sendCmd("play", { clip: name });
  };

  const stop = () => {
    setPlayback(p => ({ ...p, playing: false, progress: 0 }));
    sendCmd("stop");
  };

  const filtered = clips.filter(c => {
    const catOk = category === "All" || c.category === category;
    const searchOk = !search || c.name.toLowerCase().includes(search.toLowerCase());
    return catOk && searchOk;
  });

  const current = clips.find(c => c.name === playback.current_clip);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-pink-400 to-orange-500 bg-clip-text text-transparent">
            Animation Controller
          </h2>
          <p className="text-slate-400">Clip library · Playback · State machine</p>
        </div>
        <Badge variant="outline" className="border-slate-700 text-slate-400 font-mono">
          {clips.length} clips
        </Badge>
      </div>

      {/* Playback Bar */}
      <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl">
        <CardContent className="pt-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-300 font-mono font-bold">
                {playback.current_clip ?? "No clip selected"}
              </span>
              <div className="flex items-center gap-2">
                {current && (
                  <Badge variant="outline" className={`text-xs ${categoryColors[current.category]}`}>
                    {current.category}
                  </Badge>
                )}
                <Badge variant="outline" className={`text-xs ${playback.playing ? "text-emerald-400 border-emerald-500/20" : "text-slate-500 border-slate-700"}`}>
                  {playback.playing ? "PLAYING" : "STOPPED"}
                </Badge>
              </div>
            </div>

            {/* Progress */}
            <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-pink-500 to-orange-500 transition-all duration-200"
                style={{ width: `${Math.round(playback.progress * 100)}%` }}
              />
            </div>

            {/* Controls */}
            <div className="flex items-center gap-3">
              <button onClick={() => sendCmd("prev")} className="p-2 text-slate-400 hover:text-white transition-colors">
                <SkipBack className="h-4 w-4" />
              </button>
              {playback.playing ? (
                <button onClick={stop} className="p-2 text-red-400 hover:text-red-300 transition-colors">
                  <Square className="h-4 w-4" />
                </button>
              ) : (
                <button
                  onClick={() => playback.current_clip && playClip(playback.current_clip)}
                  className="p-2 text-emerald-400 hover:text-emerald-300 transition-colors"
                >
                  <Play className="h-4 w-4" />
                </button>
              )}
              <button onClick={() => sendCmd("next")} className="p-2 text-slate-400 hover:text-white transition-colors">
                <SkipForward className="h-4 w-4" />
              </button>
              <button
                onClick={() => { const l = !playback.loop; setPlayback(p => ({ ...p, loop: l })); sendCmd("loop", { loop: l }); }}
                className={`p-2 transition-colors ${playback.loop ? "text-pink-400" : "text-slate-600"}`}
              >
                <Repeat className="h-4 w-4" />
              </button>
              <div className="ml-auto flex items-center gap-2 text-xs text-slate-500">
                <span>Speed</span>
                {[0.5, 1.0, 1.5, 2.0].map(s => (
                  <button
                    key={s}
                    onClick={() => { setPlayback(p => ({ ...p, speed: s })); sendCmd("speed", { speed: s }); }}
                    className={`px-2 py-0.5 rounded font-mono transition-all ${playback.speed === s ? "bg-pink-500/20 text-pink-400" : "text-slate-600 hover:text-slate-400"}`}
                  >
                    {s}x
                  </button>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Filter / Search */}
      <div className="flex items-center gap-3 flex-wrap">
        {CATEGORIES.map(cat => (
          <button
            key={cat}
            onClick={() => setCategory(cat)}
            className={`px-3 py-1 rounded text-sm font-mono transition-all border ${category === cat
                ? "bg-pink-500/20 border-pink-500/40 text-pink-300"
                : "border-slate-700 text-slate-500 hover:text-slate-300"
              }`}
          >
            {cat}
          </button>
        ))}
        <input
          type="text"
          placeholder="Search clips..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="ml-auto bg-slate-900 border border-slate-700 rounded-md px-3 py-1 text-sm text-slate-300 placeholder-slate-600 focus:outline-none focus:border-slate-500"
        />
      </div>

      {/* Clip Library */}
      <Card className="border-slate-800 bg-slate-950/40 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Layers className="h-4 w-4 text-pink-400" />
            Clip Library
            <span className="ml-auto text-xs text-slate-500 font-mono">{filtered.length} clips</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-2 md:grid-cols-2 lg:grid-cols-3">
            {filtered.map(clip => {
              const isActive = playback.current_clip === clip.name;
              return (
                <div
                  key={clip.name}
                  onClick={() => playClip(clip.name)}
                  className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-all group ${isActive
                      ? "border-pink-500/40 bg-pink-500/10"
                      : "border-slate-800 hover:border-slate-700 hover:bg-slate-900/50"
                    }`}
                >
                  <Play className={`h-3 w-3 flex-shrink-0 transition-colors ${isActive ? "text-pink-400" : "text-slate-700 group-hover:text-slate-400"}`} />
                  <div className="flex-1 min-w-0">
                    <div className={`text-sm font-mono truncate ${isActive ? "text-pink-300" : "text-slate-300"}`}>
                      {clip.name}
                    </div>
                    <div className="flex items-center gap-2 mt-0.5">
                      <Clock className="h-2.5 w-2.5 text-slate-600" />
                      <span className="text-xs text-slate-600">{fmtDur(clip.duration_sec)}</span>
                      {clip.loop && <span className="text-xs text-slate-700">loop</span>}
                    </div>
                  </div>
                  <Badge variant="outline" className={`text-xs flex-shrink-0 ${categoryColors[clip.category] ?? ""}`}>
                    {clip.category}
                  </Badge>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
