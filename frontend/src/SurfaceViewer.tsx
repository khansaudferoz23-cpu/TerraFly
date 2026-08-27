import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { PointerLockControls } from "three/examples/jsm/controls/PointerLockControls.js";
import { createStructureGeometry, createSurface, heightColours, sampleMeasurementValue, sampleSurfacePoint } from "./surfaceGeometry";
import type { HeightLegend, InspectedPoint, MeasurementGrid, StructureLayer, SurfaceGrid } from "./surfaceGeometry";

type Props = {
  gridUrl: string;
  analysisGridUrl: string;
  textureUrl: string;
  measurementGridUrl?: string;
  structureLayerUrl?: string;
  onPointsChange?: (points: InspectedPoint[]) => void;
};

export function SurfaceViewer({ gridUrl, analysisGridUrl, textureUrl, measurementGridUrl, structureLayerUrl, onPointsChange }: Props) {
  const hostRef = useRef<HTMLDivElement>(null);
  const surfaceMaterialRef = useRef<THREE.MeshStandardMaterial | null>(null);
  const wallMaterialRef = useRef<THREE.MeshStandardMaterial | null>(null);
  const textureRef = useRef<THREE.Texture | null>(null);
  const meshRef = useRef<THREE.Mesh | null>(null);
  const gridRef = useRef<SurfaceGrid | null>(null);
  const analysisGridRef = useRef<SurfaceGrid | null>(null);
  const measurementGridRef = useRef<MeasurementGrid | null>(null);
  const orbitRef = useRef<OrbitControls | null>(null);
  const walkRef = useRef<PointerLockControls | null>(null);
  const resetViewRef = useRef<(() => void) | null>(null);
  const markerGroupRef = useRef<THREE.Group | null>(null);
  const structureGroupRef = useRef<THREE.Group | null>(null);
  const sunRef = useRef<THREE.DirectionalLight | null>(null);
  const pointsRef = useRef<InspectedPoint[]>([]);
  const navigationModeRef = useRef<"orbit" | "first-person">("orbit");
  const surfaceModeRef = useRef<"photo" | "height">("photo");
  const [wireframe, setWireframe] = useState(false);
  const [surfaceMode, setSurfaceMode] = useState<"photo" | "height">("photo");
  const [exaggeration, setExaggeration] = useState(1.4);
  const [sunAzimuth, setSunAzimuth] = useState(35);
  const [navigationMode, setNavigationMode] = useState<"orbit" | "first-person">("orbit");
  const [structuresEnabled, setStructuresEnabled] = useState(false);
  const [heightLegend, setHeightLegend] = useState<HeightLegend | null>(null);
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
    for (const material of [surfaceMaterialRef.current, wallMaterialRef.current]) {
      if (!material) continue;
      material.wireframe = wireframe;
      material.needsUpdate = true;
    }
  }, [wireframe]);

  useEffect(() => {
    surfaceModeRef.current = surfaceMode;
    if (!surfaceMaterialRef.current) return;
    const heightMode = surfaceMode === "height";
    surfaceMaterialRef.current.map = heightMode ? null : textureRef.current;
    surfaceMaterialRef.current.vertexColors = heightMode;
    surfaceMaterialRef.current.color.set(0xffffff);
    surfaceMaterialRef.current.needsUpdate = true;
  }, [surfaceMode]);

  useEffect(() => {
    const sun = sunRef.current;
    if (!sun) return;
    const radians = THREE.MathUtils.degToRad(sunAzimuth);
    sun.position.set(Math.cos(radians) * 9, 10, Math.sin(radians) * 9);
  }, [sunAzimuth]);

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
    if (structureGroupRef.current) structureGroupRef.current.scale.y = exaggeration;
  }, [exaggeration]);

  useEffect(() => {
    if (structureGroupRef.current) structureGroupRef.current.visible = structuresEnabled;
  }, [structuresEnabled]);

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return undefined;
    setViewerStatus("loading");
    setHeightLegend(null);
    setStructuresEnabled(false);
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
    const initialSunRadians = THREE.MathUtils.degToRad(sunAzimuth);
    sun.position.set(Math.cos(initialSunRadians) * 9, 10, Math.sin(initialSunRadians) * 9);
    sunRef.current = sun;
    scene.add(sun);
    const gridHelper = new THREE.GridHelper(14, 14, 0x52625d, 0x2c3835);
    gridHelper.position.y = -0.04;
    scene.add(gridHelper);
    const markerGroup = new THREE.Group();
    markerGroupRef.current = markerGroup;
    scene.add(markerGroup);

    const surfaceMaterial = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      roughness: 0.92,
      metalness: 0,
      side: THREE.DoubleSide,
      wireframe,
    });
    const wallMaterial = new THREE.MeshStandardMaterial({
      color: 0x586460,
      roughness: 0.98,
      metalness: 0,
      side: THREE.DoubleSide,
      flatShading: true,
      wireframe,
    });
    surfaceMaterialRef.current = surfaceMaterial;
    wallMaterialRef.current = wallMaterial;
    Promise.all([
      fetch(gridUrl).then((response) => {
        if (!response.ok) throw new Error("Surface grid is unavailable.");
        return response.json() as Promise<SurfaceGrid>;
      }),
      fetch(analysisGridUrl).then((response) => {
        if (!response.ok) throw new Error("Canonical analysis grid is unavailable.");
        return response.json() as Promise<SurfaceGrid>;
      }),
      new THREE.TextureLoader().loadAsync(textureUrl),
      measurementGridUrl
        ? fetch(measurementGridUrl).then((response) => {
            if (!response.ok) throw new Error("Metric analysis grid is unavailable.");
            return response.json() as Promise<MeasurementGrid>;
          })
        : Promise.resolve(null),
      structureLayerUrl
        ? fetch(structureLayerUrl).then((response) => {
            if (!response.ok) throw new Error("Reconstructed structure layer is unavailable.");
            return response.json() as Promise<StructureLayer>;
          })
        : Promise.resolve(null),
    ])
      .then(([grid, analysisGrid, loadedTexture, measurementGrid, structureLayer]) => {
        if (disposed) {
          loadedTexture.dispose();
          return;
        }
        gridRef.current = grid;
        analysisGridRef.current = analysisGrid;
        measurementGridRef.current = measurementGrid;
        textureRef.current = loadedTexture;
        loadedTexture.colorSpace = THREE.SRGBColorSpace;
        const colourSource = measurementGrid ?? analysisGrid;
        const { colours, legend } = heightColours(colourSource);
        if (colours.length !== grid.values.length * 3) {
          throw new Error("Height colour grid does not match the display geometry.");
        }
        setHeightLegend(legend);
        const geometry = createSurface(grid, exaggeration);
        geometry.setAttribute("color", new THREE.BufferAttribute(colours, 3));
        const heightMode = surfaceModeRef.current === "height";
        surfaceMaterial.map = heightMode ? null : loadedTexture;
        surfaceMaterial.vertexColors = heightMode;
        surfaceMaterial.needsUpdate = true;
        const mesh = new THREE.Mesh(
          geometry,
          [surfaceMaterial, wallMaterial],
        );
        meshRef.current = mesh;
        scene.add(mesh);
        if (structureLayer) {
          const structureGroup = new THREE.Group();
          const aspect = grid.shape[0] / grid.shape[1];
          for (const structure of structureLayer.structures) {
            if (structure.footprint.length < 3 || structure.relative_height <= 0) continue;
            const geometry = createStructureGeometry(structure, aspect);
            const structureMaterial = new THREE.MeshStandardMaterial({
              color: 0x4f9f8a,
              emissive: 0x102c25,
              roughness: 0.8,
              metalness: 0,
              transparent: true,
              opacity: 0.72,
              side: THREE.DoubleSide,
            });
            const structureMesh = new THREE.Mesh(geometry, structureMaterial);
            structureMesh.position.y = structure.base_relative;
            structureMesh.userData = {
              id: structure.id,
              visualScore: structure.visual_score,
              reconstructed: true,
            };
            structureGroup.add(structureMesh);
          }
          structureGroup.scale.y = exaggeration;
          structureGroup.visible = false;
          structureGroupRef.current = structureGroup;
          scene.add(structureGroup);
        }
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
      if (navigationModeRef.current !== "orbit" || !meshRef.current || !analysisGridRef.current) return;
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
      const point = sampleSurfacePoint(analysisGridRef.current, hit.uv.x, 1 - hit.uv.y, label);
      if (measurementGridRef.current) {
        point.metricElevationM = sampleMeasurementValue(
          measurementGridRef.current,
          hit.uv.x,
          1 - hit.uv.y,
        );
      }
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
      for (const child of [...(structureGroupRef.current?.children ?? [])]) {
        const structure = child as THREE.Mesh;
        structure.geometry.dispose();
        if (structure.material instanceof THREE.Material) structure.material.dispose();
      }
      surfaceMaterial.dispose();
      wallMaterial.dispose();
      textureRef.current?.dispose();
      renderer.dispose();
      renderer.domElement.remove();
      surfaceMaterialRef.current = null;
      wallMaterialRef.current = null;
      textureRef.current = null;
      meshRef.current = null;
      gridRef.current = null;
      analysisGridRef.current = null;
      measurementGridRef.current = null;
      orbitRef.current = null;
      walkRef.current = null;
      markerGroupRef.current = null;
      structureGroupRef.current = null;
      sunRef.current = null;
      resetViewRef.current = null;
    };
  }, [gridUrl, analysisGridUrl, textureUrl, measurementGridUrl, structureLayerUrl]);

  return (
    <div className="viewer-shell">
      <div className="viewer-toolbar" aria-label="3D viewer controls">
        <div className="mode-switch" aria-label="Navigation mode">
          <button type="button" aria-pressed={navigationMode === "orbit"} className={navigationMode === "orbit" ? "active" : ""} onClick={() => chooseNavigation("orbit")}>Orbit</button>
          <button type="button" aria-pressed={navigationMode === "first-person"} className={navigationMode === "first-person" ? "active" : ""} onClick={() => chooseNavigation("first-person")}>First-person</button>
        </div>
        <div className="mode-switch" aria-label="Surface colour mode">
          <button type="button" aria-pressed={surfaceMode === "photo"} className={surfaceMode === "photo" ? "active" : ""} onClick={() => setSurfaceMode("photo")}>Photo</button>
          <button type="button" aria-pressed={surfaceMode === "height"} className={surfaceMode === "height" ? "active" : ""} onClick={() => setSurfaceMode("height")}>Height colours</button>
        </div>
        <button type="button" aria-pressed={wireframe} className={wireframe ? "active" : ""} onClick={() => setWireframe(!wireframe)}>Wireframe</button>
        {structureLayerUrl && <button type="button" aria-pressed={structuresEnabled} className={structuresEnabled ? "active" : ""} onClick={() => setStructuresEnabled(!structuresEnabled)}>Structures</button>}
        <label>
          Vertical display <strong>{exaggeration.toFixed(1)}×</strong>
          <input aria-label="Display vertical exaggeration" type="range" min="0.2" max="4" step="0.1" value={exaggeration} onInput={(event) => setExaggeration(Number(event.currentTarget.value))} />
        </label>
        <label>
          Sun direction <strong>{sunAzimuth}°</strong>
          <input aria-label="Simulated sun direction" type="range" min="0" max="360" step="5" value={sunAzimuth} onInput={(event) => setSunAzimuth(Number(event.currentTarget.value))} />
        </label>
        <button type="button" onClick={clearPoints}>Clear points</button>
        <button type="button" onClick={() => resetViewRef.current?.()}>Reset</button>
      </div>
      <div ref={hostRef} className="viewer" aria-label="Interactive textured elevation surface">
        {viewerStatus === "loading" && <div className="viewer-status">Preparing 3D surface…</div>}
        {viewerStatus === "error" && <div className="viewer-status error" role="alert">The 3D surface could not be loaded.</div>}
        {heightLegend && (
          <div className="height-legend" aria-label={`${heightLegend.units} height colour scale`}>
            <strong>{heightLegend.units === "metres" ? "Calibrated height" : "Relative height"}</strong>
            <span className="legend-mode">{heightLegend.units}</span>
            <div className="legend-body">
              <div className="legend-gradient" aria-hidden="true" />
              <div className="legend-ticks">
                <span>{heightLegend.maximum.toFixed(heightLegend.units === "metres" ? 1 : 2)}{heightLegend.units === "metres" ? " m" : ""}</span>
                <span>{heightLegend.midpoint.toFixed(heightLegend.units === "metres" ? 1 : 2)}{heightLegend.units === "metres" ? " m" : ""}</span>
                <span>{heightLegend.minimum.toFixed(heightLegend.units === "metres" ? 1 : 2)}{heightLegend.units === "metres" ? " m" : ""}</span>
              </div>
            </div>
            {surfaceMode === "photo" && <small>Select Height colours to apply this scale.</small>}
          </div>
        )}
      </div>
      <p className="viewer-help">
        {navigationMode === "orbit"
          ? "Drag to orbit · right-drag to pan · scroll to zoom · click the surface to compare points"
          : "Click to enter · mouse to look · W/A/S/D move · Q/E down/up · hold Shift for boost · Esc exits"}
      </p>
      <p className="viewer-help">Steep faces use neutral wall shading so the top-down image is never stretched into vertical drips. Display cleanup does not change measured values.</p>
    </div>
  );
}
