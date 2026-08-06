import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { VRMLoaderPlugin, VRMUtils } from "@pixiv/three-vrm";
import { Eye, RotateCw } from "lucide-react";

const API = "/api/vrm/view";

export default function Viewer() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [model, setModel] = useState("Nekomimi-chan");
  const [spinning, setSpinning] = useState(true);
  const [status, setStatus] = useState("");

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f1419);

    const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 20);
    camera.position.set(0, 1.1, 2.5);

    const renderer = new THREE.WebGLRenderer({ canvas, alpha: false });
    renderer.setSize(400, 400);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    const light = new THREE.DirectionalLight(0xffffff, 1.4);
    light.position.set(1, 2, 3);
    scene.add(light);
    scene.add(new THREE.AmbientLight(0xffffff, 0.5));

    const loader = new GLTFLoader();
    loader.register((parser) => new VRMLoaderPlugin(parser));

    setStatus("Loading...");
    loader.load(
      `${API}?model=${encodeURIComponent(model)}`,
      (gltf) => {
        const vrm = gltf.userData.vrm;
        if (!vrm) { setStatus("No VRM data"); return; }
        VRMUtils.rotateVRM0(vrm);
        scene.add(vrm.scene);
        vrm.scene.position.y = -0.2;
        setStatus("");

        const clock = new THREE.Clock();
        let spin = spinning;
        const animate = () => {
          requestAnimationFrame(animate);
          const delta = clock.getDelta();
          if (spin) vrm.scene.rotation.y += delta * 0.3;
          vrm.update(delta);
          renderer.render(scene, camera);
        };
        animate();

        // Toggle spin on click
        canvas.onclick = () => { spin = !spin; setSpinning(spin); };
      },
      undefined,
      () => setStatus("Load failed"),
    );

    return () => renderer.dispose();
  }, [model]);

  const models = ["Nekomimi-chan", "AnimeGirl2", "test_avatar"];

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-xl font-bold mb-2">VRM Viewer</h1>
      <p className="text-sm text-zinc-500 mb-6">
        Three.js + @pixiv/three-vrm — click the model to toggle spin.
      </p>

      <div className="flex gap-2 mb-4 flex-wrap">
        {models.map((m) => (
          <button
            key={m}
            onClick={() => setModel(m)}
            className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
              model === m ? "bg-amber-600 text-white" : "bg-zinc-800 text-zinc-400 hover:text-zinc-200"
            }`}
          >
            {m}
          </button>
        ))}
      </div>

      <div className="flex justify-center">
        <canvas
          ref={canvasRef}
          width={400}
          height={400}
          className="rounded-xl border border-zinc-800"
        />
      </div>

      {status && <p className="text-sm text-zinc-500 text-center mt-4">{status}</p>}

      <div className="flex items-center justify-center gap-4 mt-4 text-xs text-zinc-600">
        <button onClick={() => setSpinning(!spinning)} className="flex items-center gap-1 hover:text-zinc-400">
          <RotateCw className={`w-3 h-3 ${spinning ? "text-amber-500" : ""}`} />
          {spinning ? "Spinning" : "Paused"}
        </button>
        <span className="flex items-center gap-1">
          <Eye className="w-3 h-3" />
          Click model to toggle
        </span>
      </div>
    </div>
  );
}
