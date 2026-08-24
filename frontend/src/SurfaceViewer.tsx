import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

type SurfaceGrid = { shape: [number, number]; values: number[] };

type Props = {
  gridUrl: string;
  textureUrl: string;
};

function createSurface(grid: SurfaceGrid, exaggeration: number): THREE.BufferGeometry {
  const [rows, columns] = grid.shape;
  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array(rows * columns * 3);
  const uvs = new Float32Array(rows * columns * 2);
  const indices: number[] = [];
  const aspect = rows / columns;
  for (let row = 0; row < rows; row += 1) {
    for (let column = 0; column < columns; column += 1) {
      const index = row * columns + column;
      positions[index * 3] = (column / Math.max(1, columns - 1) - 0.5) * 10;
      positions[index * 3 + 1] = grid.values[index] * exaggeration;
      positions[index * 3 + 2] = (row / Math.max(1, rows - 1) - 0.5) * 10 * aspect;
      uvs[index * 2] = column / Math.max(1, columns - 1);
      uvs[index * 2 + 1] = 1 - row / Math.max(1, rows - 1);
      if (row < rows - 1 && column < columns - 1) {
        const right = index + 1;
        const below = index + columns;
        indices.push(index, below, right, right, below, below + 1);
      }
    }
  }
  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute("uv", new THREE.BufferAttribute(uvs, 2));
  geometry.setIndex(indices);
  geometry.computeVertexNormals();
  return geometry;
}

export function SurfaceViewer({ gridUrl, textureUrl }: Props) {
  const hostRef = useRef<HTMLDivElement>(null);
  const [wireframe, setWireframe] = useState(false);
  const [textureEnabled, setTextureEnabled] = useState(true);
  const [exaggeration, setExaggeration] = useState(2.2);
  const [resetSignal, setResetSignal] = useState(0);

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return undefined;
    let disposed = false;
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x07110f);
    const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
    camera.position.set(8, 7, 9);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    host.appendChild(renderer.domElement);
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.target.set(0, 0.8, 0);
    controls.update();
    scene.add(new THREE.HemisphereLight(0xe4fff4, 0x183128, 2.3));
    const sun = new THREE.DirectionalLight(0xffffff, 2.2);
    sun.position.set(4, 10, 3);
    scene.add(sun);
    const gridHelper = new THREE.GridHelper(14, 14, 0x276252, 0x15362f);
    gridHelper.position.y = -0.04;
    scene.add(gridHelper);
    let mesh: THREE.Mesh | undefined;
    let texture: THREE.Texture | undefined;
    const material = new THREE.MeshStandardMaterial({
      color: textureEnabled ? 0xffffff : 0x62c98f,
      roughness: 0.92,
      metalness: 0,
      side: THREE.DoubleSide,
      wireframe,
    });
    Promise.all([
      fetch(gridUrl).then((response) => {
        if (!response.ok) throw new Error("Surface grid is unavailable.");
        return response.json() as Promise<SurfaceGrid>;
      }),
      new THREE.TextureLoader().loadAsync(textureUrl),
    ])
      .then(([grid, loadedTexture]) => {
        if (disposed) {
          loadedTexture.dispose();
          return;
        }
        texture = loadedTexture;
        texture.colorSpace = THREE.SRGBColorSpace;
        material.map = textureEnabled ? texture : null;
        material.needsUpdate = true;
        mesh = new THREE.Mesh(createSurface(grid, exaggeration), material);
        scene.add(mesh);
      })
      .catch(() => undefined);

    const resize = () => {
      const width = Math.max(host.clientWidth, 320);
      const height = Math.max(host.clientHeight, 360);
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
    };
    const observer = new ResizeObserver(resize);
    observer.observe(host);
    resize();
    let frame = 0;
    const animate = () => {
      controls.update();
      renderer.render(scene, camera);
      frame = requestAnimationFrame(animate);
    };
    animate();
    return () => {
      disposed = true;
      cancelAnimationFrame(frame);
      observer.disconnect();
      controls.dispose();
      mesh?.geometry.dispose();
      material.dispose();
      texture?.dispose();
      renderer.dispose();
      renderer.domElement.remove();
    };
  }, [gridUrl, textureUrl, wireframe, textureEnabled, exaggeration, resetSignal]);

  return (
    <div className="viewer-shell">
      <div className="viewer-toolbar" aria-label="3D viewer controls">
        <button type="button" className={wireframe ? "active" : ""} onClick={() => setWireframe(!wireframe)}>
          Wireframe
        </button>
        <button type="button" className={textureEnabled ? "active" : ""} onClick={() => setTextureEnabled(!textureEnabled)}>
          Texture
        </button>
        <label>
          Display exaggeration <strong>{exaggeration.toFixed(1)}×</strong>
          <input
            aria-label="Display vertical exaggeration"
            type="range"
            min="0.2"
            max="6"
            step="0.1"
            value={exaggeration}
            onChange={(event) => setExaggeration(Number(event.target.value))}
          />
        </label>
        <button type="button" onClick={() => setResetSignal((value) => value + 1)}>Reset view</button>
      </div>
      <div ref={hostRef} className="viewer" aria-label="Interactive textured relative surface" />
      <p className="viewer-help">Drag to orbit · right-drag to pan · scroll to zoom. Exaggeration changes display only.</p>
    </div>
  );
}
