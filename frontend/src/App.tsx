import { useEffect, useMemo, useState } from "react";
import { artifactUrl, createJob, getJob } from "./api";
import { SurfaceViewer } from "./SurfaceViewer";
import type { Artifact, Job } from "./types";
import "./styles.css";

const stages = ["validation", "preprocessing", "inference", "meshing", "complete"] as const;

const stageLabels: Record<string, string> = {
  queued: "Queued",
  validation: "Checking file",
  preprocessing: "Preparing image",
  inference: "Estimating structure",
  meshing: "Building viewer",
  complete: "Complete",
  failed: "Stopped",
};

function ContourMark() {
  return (
    <svg className="contour-mark" viewBox="0 0 38 38" aria-hidden="true">
      <path d="M5 20c1-7 6-12 13-13 8-1 15 4 15 12 0 7-5 13-13 14-7 1-14-5-15-13Z" />
      <path d="M10 20c1-4 4-8 9-8 5-1 10 2 10 7 0 5-4 9-9 9s-9-3-10-8Z" />
      <path d="M15 20c0-2 2-4 5-4 2 0 4 1 4 4 0 2-2 4-4 4-3 0-5-2-5-4Z" />
    </svg>
  );
}

function fileSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [busy, setBusy] = useState(false);
  const [dragging, setDragging] = useState(false);
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

  function selectFile(nextFile: File | null) {
    setFile(nextFile);
    setJob(null);
    setError(null);
  }

  async function generate() {
    if (!file) return;
    setBusy(true);
    setError(null);
    setJob(null);
    try {
      setJob(await createJob(file));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Generation failed.");
      setBusy(false);
    }
  }

  const complete = job?.status === "complete";
  const artifact = (name: string) => complete ? artifactUrl(job.job_id, name) : "#";
  const artifactRecord = (name: string): Artifact | undefined => job?.artifacts.find((item) => item.name === name);
  const currentStage = stages.indexOf((job?.stage ?? "") as (typeof stages)[number]);
  const isSingleBand = job?.input.mode === "L" || job?.input.bands === 1;

  return (
    <main className="app-shell">
      <nav className="topbar" aria-label="TerraFly project">
        <div className="wordmark"><ContourMark /><span>TerraFly</span></div>
        <span className="project-id">SIH 2026 / PS 26175</span>
      </nav>

      <header className="intro">
        <div className="intro-copy">
          <p className="kicker">Surface analysis workbench</p>
          <h1>Explore scene structure from one optical image.</h1>
          <p>TerraFly estimates relative monocular depth, converts it into a display surface, and keeps every run traceable.</p>
        </div>
        <aside className="scope-note" aria-label="Scientific output scope">
          <span>Output scope</span>
          <strong>Relative surface · 0–1</strong>
          <p>A normal image cannot establish elevation in metres. Metric export remains locked until valid vertical calibration exists.</p>
        </aside>
      </header>

      <div className="process-line" aria-label="Processing method">
        <span>Optical image</span><i>→</i><span>Depth Anything V2</span><i>→</i><span>Relative surface</span><i>→</i><span>3D inspection</span>
      </div>

      <section className="workbench" aria-labelledby="input-title">
        <div className="section-heading">
          <div><p className="section-label">New analysis</p><h2 id="input-title">Select an input scene</h2></div>
          <p>PNG, JPG/JPEG, or GeoTIFF · maximum 25 MB</p>
        </div>

        <div className="input-layout">
          <label
            className={`upload-area ${dragging ? "dragging" : ""} ${file ? "has-file" : ""}`}
            htmlFor="scene-upload"
            onDragEnter={(event) => { event.preventDefault(); setDragging(true); }}
            onDragOver={(event) => event.preventDefault()}
            onDragLeave={() => setDragging(false)}
            onDrop={(event) => {
              event.preventDefault();
              setDragging(false);
              selectFile(event.dataTransfer.files?.[0] ?? null);
            }}
          >
            <input
              id="scene-upload"
              aria-label="Choose an image"
              type="file"
              accept=".png,.jpg,.jpeg,.tif,.tiff,image/png,image/jpeg,image/tiff"
              onChange={(event) => selectFile(event.target.files?.[0] ?? null)}
            />
            {file && localPreview ? <img src={localPreview} alt="Selected scene preview" /> : <ContourMark />}
            <div>
              <strong>{file ? file.name : "Choose a file or drop it here"}</strong>
              <span>{file ? `${fileSize(file.size)} · ready to analyse` : "Your file stays on this computer."}</span>
            </div>
          </label>

          <div className="run-panel">
            <div className="run-summary">
              <span>{job ? stageLabels[job.stage] ?? job.stage : "Ready"}</span>
              <strong>{job ? `${job.progress}%` : "Relative mode"}</strong>
            </div>
            <div className="progress-track" aria-label="Analysis progress"><span style={{ width: `${job?.progress ?? 0}%` }} /></div>
            <ol className="stage-line">
              {stages.map((stage, index) => <li key={stage} className={currentStage >= index ? "done" : ""}>{stageLabels[stage]}</li>)}
            </ol>
            <button className="primary-action" type="button" disabled={!file || busy} onClick={generate}>
              {busy ? "Analysing scene…" : "Generate surface"}
            </button>
            <p className="action-note">The saved numeric result remains relative. Viewer exaggeration never changes the source data.</p>
            {error && <div className="error" role="alert">{error}</div>}
            {job?.status === "failed" && <div className="error" role="alert">{job.error}</div>}
          </div>
        </div>
      </section>

      {complete && localPreview && <>
        <section className="result-section" aria-labelledby="result-title">
          <div className="section-heading result-heading">
            <div><p className="section-label">Completed run</p><h2 id="result-title">Relative surface analysis</h2></div>
            <div className="result-state"><strong>{job.scientific_state}</strong><span>Values are relative, not metres</span></div>
          </div>

          {isSingleBand && <div className="domain-note" role="note">
            <strong>Single-band input detected</strong>
            <span>This file was repeated into RGB for compatibility. Thermal/TIR imagery is outside this pretrained model's validated optical-image domain, so treat this run as a software demonstration—not scientific validation.</span>
          </div>}

          <div className="analysis-layout">
            <div className="viewer-column">
              <SurfaceViewer gridUrl={artifact("surface_grid")} textureUrl={artifact("texture")} />
            </div>
            <aside className="result-inspector">
              <div className="comparison-pair">
                <figure><img src={localPreview} alt="Uploaded scene" /><figcaption>Input scene</figcaption></figure>
                <figure><img src={artifact("preview")} alt="Colourized relative surface" /><figcaption>Relative map</figcaption></figure>
              </div>
              <div className="interpretation">
                <h3>How to read this</h3>
                <p>The colour map and 3D shape show ordering and local structure. They do not provide absolute terrain height, building height, or elevation.</p>
              </div>
              <details className="run-details">
                <summary>Inspect run provenance</summary>
                <dl>
                  <div><dt>Model</dt><dd>{String(job.model.checkpoint ?? "Unavailable")}</dd></div>
                  <div><dt>Revision</dt><dd className="hash">{String(job.model.revision ?? "Unavailable")}</dd></div>
                  <div><dt>Device</dt><dd>{String(job.model.device ?? "Unavailable")}</dd></div>
                  <div><dt>Input hash</dt><dd className="hash">{String(job.input.sha256)}</dd></div>
                  <div><dt>CRS</dt><dd>{String(job.geospatial?.crs ?? "Not supplied")}</dd></div>
                </dl>
              </details>
            </aside>
          </div>
        </section>

        <section className="evidence-section" aria-labelledby="evidence-title">
          <div className="section-heading">
            <div><p className="section-label">Reproducible outputs</p><h2 id="evidence-title">Evidence bundle</h2></div>
            <p>Only working outputs are shown. Each file has one defined purpose.</p>
          </div>
          <div className="evidence-list">
            <a href={artifact("preview")} download>
              <span><strong>{artifactRecord("preview")?.filename ?? "relative_preview.png"}</strong><small>Human-readable quality check; never used as numeric ground truth.</small></span>
              <b>Download · {fileSize(artifactRecord("preview")?.bytes ?? 0)}</b>
            </a>
            <a href={artifact("numeric_surface")} download>
              <span><strong>{artifactRecord("numeric_surface")?.filename ?? "relative_surface.npy"}</strong><small>Lossless float32 relative values used for analysis and later calibration.</small></span>
              <b>Download · {fileSize(artifactRecord("numeric_surface")?.bytes ?? 0)}</b>
            </a>
            <a href={artifact("manifest")} download>
              <span><strong>{artifactRecord("manifest")?.filename ?? "job_manifest.json"}</strong><small>Audit record containing input hash, model revision, device, warnings, and artifact hashes.</small></span>
              <b>Download · {fileSize(artifactRecord("manifest")?.bytes ?? 0)}</b>
            </a>
          </div>
          <p className="metric-lock">Metric GeoTIFF is intentionally absent: TerraFly will add it only after a documented calibration passes.</p>
        </section>

        {job.warnings.length > 0 && <section className="warning-section">
          <h3>Scientific notes for this run</h3>
          <ul>{job.warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul>
        </section>}
      </>}

      <details className="method-section">
        <summary>What happens inside TerraFly?</summary>
        <div>
          <p><strong>1. Validate.</strong> Check filename, format, size, pixel count, and geospatial metadata before decoding.</p>
          <p><strong>2. Infer.</strong> Depth Anything V2 estimates relative monocular depth from visual structure.</p>
          <p><strong>3. Convert.</strong> TerraFly normalizes and inverts depth into a 0–1 display surface; this is not metric height.</p>
          <p><strong>4. Preserve evidence.</strong> Numeric data, previews, hashes, model identity, and warnings are stored per run.</p>
        </div>
      </details>

      <footer><span>TerraFly · Day 1 baseline</span><span>Local processing · explicit scientific limits · reproducible outputs</span></footer>
    </main>
  );
}
