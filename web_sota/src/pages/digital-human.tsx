import { useState, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Sparkles, Loader2, Video, CheckCircle2, Music, UserCheck, RefreshCw } from 'lucide-react';

export function DigitalHumanStudio() {
  const [audioPath, setAudioPath] = useState('sample_speech.wav');
  const [referenceImage, setReferenceImage] = useState('portrait_avatar.png');
  const [prompt, setPrompt] = useState('Photorealistic talking digital human avatar, smooth expressions');
  const [numFrames, setNumFrames] = useState(81);
  const [guidanceScale, setGuidanceScale] = useState(4.5);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [outputVideoUrl, setOutputVideoUrl] = useState<string | null>(null);
  const [engineStatus, setEngineStatus] = useState<Record<string, unknown> | null>(null);

  const checkStatus = useCallback(async () => {
    try {
      const res = await fetch('/api/v1/tools/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool_name: 'digital_human_avatar',
          arguments: { operation: 'longcat_status' },
        }),
      });
      const data = await res.json();
      setEngineStatus(data.result ?? data);
    } catch {
      setEngineStatus({ status: 'offline', message: 'Could not connect to MCP engine' });
    }
  }, []);

  const generate = async () => {
    setLoading(true);
    setMessage(null);
    try {
      const res = await fetch('/api/v1/tools/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool_name: 'digital_human_avatar',
          arguments: {
            operation: 'longcat_generate',
            audio_path: audioPath,
            reference_image_path: referenceImage,
            prompt,
            num_frames: numFrames,
            guidance_scale: guidanceScale,
          },
        }),
      });
      const data = await res.json();
      const result = data.result ?? data;
      if (result.success !== false && result.status !== 'error') {
        setMessage('Digital Human synthesis completed!');
        if (result.output_path) setOutputVideoUrl(result.output_path);
      } else {
        setMessage(result.error ?? 'Generation failed');
      }
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'Generation error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 p-6 max-w-5xl">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-100">Digital Human Studio</h1>
            <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
              LongCat-Video-Avatar 1.5
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Audio-driven photorealistic digital human video synthesis engine for AvatarMCP.
          </p>
        </div>

        <Button onClick={checkStatus} variant="outline" size="sm" className="gap-2 border-slate-700">
          <RefreshCw className="h-4 w-4" />
          Check Engine
        </Button>
      </div>

      {engineStatus && (
        <Card className="border-slate-800 bg-slate-900/60">
          <CardContent className="p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="h-5 w-5 text-emerald-400" />
              <div>
                <div className="text-sm font-semibold text-slate-200">
                  Engine: LongCat-Video-Avatar 1.5 (Dense DiT)
                </div>
                <div className="text-xs text-slate-400">
                  {String(engineStatus.hint ?? 'Ready for audio-driven synthesis')}
                </div>
              </div>
            </div>
            <div className="text-xs font-mono text-slate-400">30 FPS · CUDA Active</div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <Card className="lg:col-span-7 border-slate-800 bg-slate-900/50">
          <CardHeader>
            <CardTitle className="text-base font-medium text-slate-200 flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-purple-400" />
              Audio & Avatar Conditioning
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label className="text-xs text-slate-300 flex items-center gap-1.5 mb-1.5">
                <Music className="h-3.5 w-3.5 text-blue-400" /> Audio Track Path (.wav / .mp3)
              </Label>
              <Input
                value={audioPath}
                onChange={(e) => setAudioPath(e.target.value)}
                className="bg-slate-950 border-slate-800 text-sm font-mono"
                placeholder="Path to audio file..."
              />
            </div>

            <div>
              <Label className="text-xs text-slate-300 flex items-center gap-1.5 mb-1.5">
                <UserCheck className="h-3.5 w-3.5 text-purple-400" /> Reference Avatar Image (.png / .jpg)
              </Label>
              <Input
                value={referenceImage}
                onChange={(e) => setReferenceImage(e.target.value)}
                className="bg-slate-950 border-slate-800 text-sm font-mono"
                placeholder="Path to portrait or VRM reference image..."
              />
            </div>

            <div>
              <Label className="text-xs text-slate-300 mb-1.5 block">Expression & Style Prompt</Label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={3}
                className="w-full rounded-md bg-slate-950 border border-slate-800 p-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-purple-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="flex justify-between text-xs mb-1 text-slate-400">
                  <span>Frames</span>
                  <span className="font-mono text-slate-200">{numFrames}</span>
                </div>
                <input
                  type="range"
                  min={16}
                  max={121}
                  step={8}
                  value={numFrames}
                  onChange={(e) => setNumFrames(Number(e.target.value))}
                  className="w-full accent-purple-500 bg-slate-800"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1 text-slate-400">
                  <span>Guidance Scale</span>
                  <span className="font-mono text-slate-200">{guidanceScale.toFixed(1)}</span>
                </div>
                <input
                  type="range"
                  min={1.0}
                  max={15.0}
                  step={0.5}
                  value={guidanceScale}
                  onChange={(e) => setGuidanceScale(Number(e.target.value))}
                  className="w-full accent-purple-500 bg-slate-800"
                />
              </div>
            </div>

            <Button
              onClick={generate}
              disabled={loading || !audioPath}
              className="w-full bg-purple-600 hover:bg-purple-500 text-white font-semibold flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" /> Synthesizing Digital Human...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" /> Synthesize LongCat Digital Human
                </>
              )}
            </Button>

            {message && <div className="p-3 text-xs rounded bg-slate-800 text-purple-300 font-mono">{message}</div>}
          </CardContent>
        </Card>

        <div className="lg:col-span-5 space-y-4">
          <Card className="border-slate-800 bg-slate-950 aspect-video flex flex-col items-center justify-center p-4">
            {outputVideoUrl ? (
              <video src={outputVideoUrl} controls autoPlay loop className="w-full h-full object-contain rounded" />
            ) : (
              <div className="text-center space-y-2">
                <Video className="h-10 w-10 text-slate-700 mx-auto" />
                <p className="text-xs text-slate-500">Rendered talking avatar video preview</p>
              </div>
            )}
          </Card>

          <Card className="border-slate-800 bg-slate-900/40 p-4">
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Model Specs
            </h4>
            <div className="space-y-1.5 text-xs text-slate-400">
              <div className="flex justify-between">
                <span>Model Architecture</span>
                <span className="font-mono text-purple-300">LongCat-Video-Avatar 1.5</span>
              </div>
              <div className="flex justify-between">
                <span>Task</span>
                <span className="font-mono text-slate-200">Audio-Driven Lip Sync & Expression</span>
              </div>
              <div className="flex justify-between">
                <span>Resolution</span>
                <span className="font-mono text-slate-200">720p @ 30 FPS</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
