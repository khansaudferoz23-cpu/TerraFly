import { useEffect, useMemo, useState } from "react";
import { artifactUrl, createJob, getJob } from "./api";
import { SurfaceViewer } from "./SurfaceViewer";
import type { Job } from "./types";
import "./styles.css";

const stages = ["validation", "preprocessing", "inference", "meshing", "complete"];

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const localPreview = useMemo(() => (file ? URL.createObjectURL(file) : null), [file]);

  useEffect(() => () => { if (localPreview) URL.revokeObjectURL(localPreview); }, [localPreview]);

  useEffect(() => {
    if (!job || job.status === "complete" || job.status === "failed") return undefined;
    const timer = window.setInterval(async () => {
      try {
        const current = await getJob(job.job_id);
        setJob(current);
        if (current.status === "complete" || current.status === "failed") setBusy(false);
      } catch (reason) {
        setError(reason instanceof Error ? reason.message : "Progress check failed.");
        setBusy(false);
      }
    }, 550);
    return () => window.clearInterval(timer);
  }, [job]);

  async function generate() {
    if (!file) return;
    setBusy(true);
    setError(null);
    setJob(null);
    try {
      const queued = await createJob(file);
      setJob(queued);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Generation failed.");
      setBusy(false);
    }
  }

  const complete = job?.status === "complete";
  const artifact = (name: string) => complete ? artifactUrl(job.job_id, name) : "#";

  return (
    <main>
      <header className="hero">
        <div className="brand-mark" aria-hidden="true">TF</div>
        <div>
          <p className="eyebrow">SIH 2026 · PS 26175</p>
          <h1>TerraFly</h1>
          <p className="lede">Turn one optical image into an honest relative surface and explore it in 3D.</p>
        </div>
        <div className="truth-chip"><span /> Relative by default</div>
      </header>

      <section className="truth-banner">
        <strong>Scientific promise</strong>
        <span>A PNG or JPG cannot reveal elevation in metres. Metric outputs stay locked until valid vertical calibration succeeds.</span>
      </section>

      <section className="workspace-grid">
        <div className="panel upload-panel">
          <div className="panel-heading"><span>01</span><div><h2>Choose a scene</h2><p>PNG, JPG/JPEG, or GeoTIFF · up to 25 MB</p></div></div>
          <label className="drop-zone">
            <input
              aria-label="Choose an image"
              type="file"
              accept=".png,.jpg,.jpeg,.tif,.tiff,image/png,image/jpeg,image/tiff"
              onChange={(event) => {
                setFile(event.target.files?.[0] ?? null);
                setJob(null);
                setError(null);
              }}
            />
            <span className="drop-icon">↥</span>
            <strong>{file ? file.name : "Drop an optical image here"}</strong>
            <small>{file ? `${(file.size / 1024 / 1024).toFixed(2)} MB ready` : "or click to browse your computer"}</small>
          </label>
          <button className="generate" type="button" disabled={!file || busy} onClick={generate}>
            {busy ? "Generating surface…" : "Generate relative surface"}
          </button>
          {error && <div className="error" role="alert">{error}</div>}
        </div>

        <div className="panel progress-panel">
          <div className="panel-heading"><span>02</span><div><h2>Real progress</h2><p>{job ? `${job.progress}% · ${job.stage}` : "Waiting for an image"}</p></div></div>
          <div className="progress-track"><span style={{ width: `${job?.progress ?? 0}%` }} /></div>
          <ol className="stages">
            {stages.map((stage) => {
              const currentIndex = stages.indexOf(job?.stage ?? "");
              const stageIndex = stages.indexOf(stage);
              return <li key={stage} className={currentIndex >= stageIndex ? "done" : ""}><span>{currentIndex > stageIndex || job?.stage === "complete" ? "✓" : stageIndex + 1}</span>{stage}</li>;
            })}
          </ol>
          {job?.status === "failed" && <div className="error" role="alert">{job.error}</div>}
          {job && <div className={`state-card ${job.scientific_state === "Metric Calibrated" ? "metric" : "relative"}`}>
            <small>Result state</small><strong>{job.scientific_state}</strong><p>{job.calibration.reason}</p>
          </div>}
        </div>
      </section>

      {complete && localPreview && <>
        <section className="results-heading"><div><p className="eyebrow">Generated evidence</p><h2>Relative surface result</h2></div><span className="unit-pill">Units: relative 0–1</span></section>
        <section className="comparison-grid">
          <figure className="panel image-card"><figcaption>Original optical image</figcaption><img src={localPreview} alt="Uploaded optical scene" /></figure>
          <figure className="panel image-card"><figcaption>2D relative surface preview</figcaption><img src={artifact("preview")} alt="Colourized relative surface" /></figure>
        </section>
        <section className="panel viewer-panel">
          <div className="panel-heading"><span>03</span><div><h2>Textured 3D surface</h2><p>Interactive orbit, pan, zoom, reset, wireframe, texture, and display-only exaggeration</p></div></div>
          <SurfaceViewer gridUrl={artifact("surface_grid")} textureUrl={artifact("texture")} />
        </section>
        <section className="lower-grid">
          <div className="panel metadata-panel"><h3>Provenance</h3><dl>
            <div><dt>Model</dt><dd>{String(job.model.checkpoint ?? "Unavailable")}</dd></div>
            <div><dt>Device</dt><dd>{String(job.model.device ?? "Unavailable")}</dd></div>
            <div><dt>Input SHA-256</dt><dd className="hash">{String(job.input.sha256)}</dd></div>
            <div><dt>CRS</dt><dd>{String(job.geospatial?.crs ?? "Not supplied")}</dd></div>
          </dl></div>
          <div className="panel exports-panel"><h3>Exports</h3><div className="export-list">
            <a href={artifact("preview")} download>Preview PNG <span>available</span></a>
            <a href={artifact("numeric_surface")} download>Numeric .npy <span>available</span></a>
            <a href={artifact("manifest")} download>Job manifest <span>available</span></a>
            <button type="button" disabled title="A metric GeoTIFF requires valid vertical calibration.">Metric GeoTIFF <span>needs calibration</span></button>
            <button type="button" disabled title="Mesh export is scheduled after the stable Day 1 path.">GLB mesh <span>coming next</span></button>
          </div></div>
        </section>
        {job.warnings.length > 0 && <section className="warnings"><h3>What this result does not claim</h3>{job.warnings.map((warning) => <p key={warning}>{warning}</p>)}</section>}
      </>}
    </main>
  );
}
\n