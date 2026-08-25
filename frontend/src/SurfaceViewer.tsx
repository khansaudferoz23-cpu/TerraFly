import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { PointerLockControls } from "three/examples/jsm/controls/PointerLockControls.js";
import { createSurface, sampleSurfacePoint } from "./surfaceGeometry";
import type { InspectedPoint, SurfaceGrid } from "./surfaceGeometry";

type Props = {
  gridUrl: string;
  textureUrl: string;
  onPointsChange?: (points: InspectedPoint[]) => void;
};

export function SurfaceViewer({ gridUrl, textureUrl, onPointsChange }: Props) {
  const hostRef = useRef<HTMLDivElement>(null);
  const materialRef = useRef<THREE.MeshStandardMaterial | null>(null);
  const textureRef = useRef<THREE.Texture | null>(null);
  const meshRef = useRef<THREE.Mesh | null>(null);
  const gridRef = useRef<SurfaceGrid | null>(null);
  const orbitRef = useRef<OrbitControls | null>(null);
  const walkRef = useRef<PointerLockControls | null>(null);
  const resetViewRef = useRef<(() => void) | null>(null);
  const markerGroupRef = useRef<THREE.Group | null>(null);
  const pointsRef = useRef<InspectedPoint[]>([]);
  const navigationModeRef = useRef<"orbit" | "first-person">("orbit");
  const [wireframe, setWireframe] = useState(false);
  const [textureEnabled, setTextureEnabled] = useState(true);
  const [exaggeration, setExaggeration] = useState(2.2);
  const [navigationMode, setNavigationMode] = useState<"orbit" | "first-person">("orbit");
  const [viewerStatus, setViewerStatus] = useState<"loading" | "ready" | "error">("loading");

  function chooseNavigation(mode: "orbit" | "first-person") {
    navigationModeRef.current = mode;
    setNavigationMode(mode);
  }

  function clearPoints() {
    pointsRef.current = [];
    const group = markerGroupRef.current;
    if (group) {
      for (const child of [...group.children]) {
        group.remove(child);
        const marker = child as THREE.Mesh;
        marker.geometry?.dispose();
        if (marker.material instanceof THREE.Material) marker.material.dispose();
      }
    }
    onPointsChange?.([]);
  }

  useEffect(() => {
    navigationModeRef.current = navigationMode;
    if (orbitRef.current) orbitRef.current.enabled = navigationMode === "orbit";
    if (navigationMode === "orbit" && walkRef.current?.isLocked) walkRef.current.unlock();
  }, [navigationMode]);

  useEffect(() => {
    if (!materialRef.current) return;
    materialRef.current.wireframe = wireframe;
    materialRef.current.needsUpdate = true;
  }, [wireframe]);

  useEffect(() => {
    if (!materialRef.current) return;
    materialRef.current.map = textureEnabled ? textureRef.current : null;
    materialRef.current.color.set(textureEnabled ? 0xffffff : 0x7d9c92);
    materialRef.current.needsUpdate = true;
  }, [textureEnabled]);

  useEffect(() => {
    const mesh = meshRef.current;
    const grid = gridRef.current;
    if (!mesh || !grid) return;
    const position = mesh.geometry.getAttribute("position") as THREE.BufferAttribute;
    for (let index = 0; index < grid.values.length; index += 1) {
      position.setY(index, grid.values[index] * exaggeration);
    }
    position.needsUpdate = true;
    mesh.geometry.computeVertexNormals();
  }, [exaggeration]);

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return undefined;
    setViewerStatus("loading");
    pointsRef.current = [];
    onPointsChange?.([]);
    let disposed = false;
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x121918);
    const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 150);
    const resetView = () => {
      camera.position.set(8, 7, 9);
      if (orbitRef.current) {
        orbitRef.current.target.set(0, 0.8, 0);
        orbitRef.current.update();
      }
    };
    resetViewRef.current = resetView;
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.domElement.tabIndex = 0;
    host.appendChild(renderer.domElement);

    const orbit = new OrbitControls(camera, renderer.domElement);
    orbit.enableDamping = true;
    orbit.target.set(0, 0.8, 0);
    orbitRef.current = orbit;
    const walk = new PointerLockControls(camera, renderer.domElement);
    walkRef.current = walk;
    resetView();

    scene.add(new THREE.HemisphereLight(0xf4f7f5, 0x26312e, 2.3));
    const sun = new THREE.DirectionalLight(0xffffff, 2.2);
    sun.position.set(4, 10, 3);
    scene.add(sun);
    const gridHelper = new THREE.GridHelper(14, 14, 0x52625d, 0x2c3835);
    gridHelper.position.y = -0.04;
    scene.add(gridHelper);
    const markerGroup = new THREE.Group();
    markerGroupRef.current = markerGroup;
    scene.add(markerGroup);

    const material = new THREE.MeshStandardMaterial({
      color: textureEnabled ? 0xffffff : 0x7d9c92,
      roughness: 0.92,
      metalness: 0,
      side: THREE.DoubleSide,
      wireframe,
    });
    materialRef.current = material;
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
        gridRef.current = grid;
        textureRef.current = loadedTexture;
        loadedTexture.colorSpace = THREE.SRGBColorSpace;
        material.map = textureEnabled ? loadedTexture : null;
        material.needsUpdate = true;
        const mesh = new THREE.Mesh(createSurface(grid, exaggeration), material);
        meshRef.current = mesh;
        scene.add(mesh);
        setViewerStatus("ready");
      })
      .catch(() => {
        if (!disposed) setViewerStatus("error");
      });

    const resize = () => {
      const width = Math.max(host.clientWidth, 1);
      const height = Math.max(host.clientHeight, 360);
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
    };
    const observer = new ResizeObserver(resize);
    observer.observe(host);
    resize();

    const keys = new Set<string>();
    const onKeyDown = (event: KeyboardEvent) => keys.add(event.code);
    const onKeyUp = (event: KeyboardEvent) => keys.delete(event.code);
    window.addEventListener("keydown", onKeyDown);
    window.addEventListener("keyup", onKeyUp);
    const pointerStart = new THREE.Vector2();
    const onPointerDown = (event: PointerEvent) => pointerStart.set(event.clientX, event.clientY);
    const onPointerUp = (event: PointerEvent) => {
      if (navigationModeRef.current !== "orbit" || !meshRef.current || !gridRef.current) return;
      if (pointerStart.distanceTo(new THREE.Vector2(event.clientX, event.clientY)) > 6) return;
      const rectangle = renderer.domElement.getBoundingClientRect();
      const mouse = new THREE.Vector2(
        ((event.clientX - rectangle.left) / rectangle.width) * 2 - 1,
        -((event.clientY - rectangle.top) / rectangle.height) * 2 + 1,
      );
      const raycaster = new THREE.Raycaster();
      raycaster.setFromCamera(mouse, camera);
      const hit = raycaster.intersectObject(meshRef.current)[0];
      if (!hit?.uv) return;
      const current = pointsRef.current;
      const label: "A" | "B" = current.length === 0 ? "A" : "B";
      const point = sampleSurfacePoint(gridRef.current, hit.uv.x, 1 - hit.uv.y, label);
      const next = current.length === 0 ? [point] : current.length === 1 ? [current[0], point] : [current[0], point];
      pointsRef.current = next;
      if (markerGroup.children.length === 2) {
        const old = markerGroup.children[1] as THREE.Mesh;
        markerGroup.remove(old);
        old.geometry.dispose();
        if (old.material instanceof THREE.Material) old.material.dispose();
      }
      const marker = new THREE.Mesh(
        new THREE.SphereGeometry(0.11, 16, 12),
        new THREE.MeshBasicMaterial({ color: label === "A" ? 0x70d7bb : 0xf1bd62 }),
      );
      marker.position.copy(hit.point).add(new THREE.Vector3(0, 0.12, 0));
      markerGroup.add(marker);
      onPointsChange?.(next);
    };
    const onCanvasClick = () => {
      if (navigationModeRef.current === "first-person" && !walk.isLocked) walk.lock();
    };
    renderer.domElement.addEventListener("pointerdown", onPointerDown);
    renderer.domElement.addEventListener("pointerup", onPointerUp);
    renderer.domElement.addEventListener("click", onCanvasClick);

    let previousFrameTime = performance.now();
    let frame = 0;
    const animate = (frameTime = performance.now()) => {
      const delta = Math.min((frameTime - previousFrameTime) / 1000, 0.05);
      previousFrameTime = frameTime;
      if (navigationModeRef.current === "orbit") {
        orbit.update();
      } else if (walk.isLocked) {
        const speed = (keys.has("ShiftLeft") || keys.has("ShiftRight") ? 10 : 4.2) * delta;
        if (keys.has("KeyW") || keys.has("ArrowUp")) walk.moveForward(speed);
        if (keys.has("KeyS") || keys.has("ArrowDown")) walk.moveForward(-speed);
        if (keys.has("KeyA") || keys.has("ArrowLeft")) walk.moveRight(-speed);
        if (keys.has("KeyD") || keys.has("ArrowRight")) walk.moveRight(speed);
        if (keys.has("KeyQ")) camera.position.y -= speed;
        if (keys.has("KeyE")) camera.position.y += speed;
      }
      renderer.render(scene, camera);
      frame = requestAnimationFrame(animate);
    };
    animate();
    return () => {
      disposed = true;
      cancelAnimationFrame(frame);
      observer.disconnect();
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("keyup", onKeyUp);
      renderer.domElement.removeEventListener("pointerdown", onPointerDown);
      renderer.domElement.removeEventListener("pointerup", onPointerUp);
      renderer.domElement.removeEventListener("click", onCanvasClick);
      if (walk.isLocked) walk.unlock();
      walk.dispose();
      orbit.dispose();
      meshRef.current?.geometry.dispose();
      for (const child of [...markerGroup.children]) {
        const marker = child as THREE.Mesh;
        marker.geometry.dispose();
        if (marker.material instanceof THREE.Material) marker.material.dispose();
      }
      material.dispose();
      textureRef.current?.dispose();
      renderer.dispose();
      renderer.domElement.remove();
      materialRef.current = null;
      textureRef.current = null;
      meshRef.current = null;
      gridRef.current = null;
      orbitRef.current = null;
      walkRef.current = null;
      markerGroupRef.current = null;
      resetViewRef.current = null;
    };
  }, [gridUrl, textureUrl]);

  return (
    <div className="viewer-shell">
      <div className="viewer-toolbar" aria-label="3D viewer controls">
        <div className="mode-switch" aria-label="Navigation mode">
          <button type="button" aria-pressed={navigationMode === "orbit"} className={navigationMode === "orbit" ? "active" : ""} onClick={() => chooseNavigation("orbit")}>Orbit</button>
          <button type="button" aria-pressed={navigationMode === "first-person"} className={navigationMode === "first-person" ? "active" : ""} onClick={() => chooseNavigation("first-person")}>First-person</button>
        </div>
        <button type="button" aria-pressed={textureEnabled} className={textureEnabled ? "active" : ""} onClick={() => setTextureEnabled(!textureEnabled)}>Texture</button>
        <button type="button" aria-pressed={wireframe} className={wireframe ? "active" : ""} onClick={() => setWireframe(!wireframe)}>Wireframe</button>
        <label>
          Vertical display <strong>{exaggeration.toFixed(1)}×</strong>
          <input aria-label="Display vertical exaggeration" type="range" min="0.2" max="6" step="0.1" value={exaggeration} onChange={(event) => setExaggeration(Number(event.target.value))} />
        </label>
        <button type="button" onClick={clearPoints}>Clear points</button>
        <button type="button" onClick={() => resetViewRef.current?.()}>Reset</button>
      </div>
      <div ref={hostRef} className="viewer" aria-label="Interactive textured relative surface">
        {viewerStatus === "loading" && <div className="viewer-status">Preparing 3D surface…</div>}
        {viewerStatus === "error" && <div className="viewer-status error" role="alert">The 3D surface could not be loaded.</div>}
      </div>
      <p className="viewer-help">
        {navigationMode === "orbit"
          ? "Drag to orbit · right-drag to pan · scroll to zoom · click the surface to compare points"
          : "Click to enter · mouse to look · W/A/S/D move · Q/E down/up · hold Shift for boost · Esc exits"}
      </p>
    </div>
  );
}
