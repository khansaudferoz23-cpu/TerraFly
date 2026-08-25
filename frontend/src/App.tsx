import { useEffect, useMemo, useState } from "react";
import { artifactUrl, calibrateWithReference, createJob, deleteJob, getJob } from "./api";
import { SurfaceViewer } from "./SurfaceViewer";
import type { InspectedPoint } from "./surfaceGeometry";
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

function metric(value: number | undefined, digits = 3) {
  return typeof value === "number" && Number.isFinite(value) ? value.toFixed(digits) : "—";
}

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [busy, setBusy] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [points, setPoints] = useState<InspectedPoint[]>([]);
  const [referenceFile, setReferenceFile] = useState<File | null>(null);
  const [sourceDescription, setSourceDescription] = useState("");
  const [verticalDatum, setVerticalDatum] = useState("");
  const [maxRmse, setMaxRmse] = useState("2");
  const [calibrating, setCalibrating] = useState(false);
  const [calibrationError, setCalibrationError] = useState<string | null>(null);
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
    setPoints([]);
    setReferenceFile(null);
    setSourceDescription("");
    setVerticalDatum("");
    setMaxRmse("2");
    setCalibrationError(null);
  }

  async function clearResult() {
    if (!job || job.status !== "complete") return;
    setBusy(true);
    setError(null);
    try {
      await deleteJob(job.job_id);
      setJob(null);
      setPoints([]);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not clear this result.");
    } finally {
      setBusy(false);
    }
  }

  async function generate() {
    if (!file) return;
    setBusy(true);
    setError(null);
    setJob(null);
    setPoints([]);
    try {
      setJob(await createJob(file));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Generation failed.");
      setBusy(false);
    }
  }

  async function evaluateCalibration() {
    if (!job || !referenceFile || !sourceDescription.trim() || !verticalDatum.trim()) return;
    const threshold = Number(maxRmse);
    if (!Number.isFinite(threshold) || threshold <= 0) {
      setCalibrationError("Enter a positive held-out RMSE limit in metres.");
      return;
    }
    setCalibrating(true);
    setCalibrationError(null);
    try {
      setJob(await calibrateWithReference(
        job.job_id,
        referenceFile,
        sourceDescription.trim(),
        verticalDatum.trim(),
        threshold,
      ));
    } catch (reason) {
      setCalibrationError(reason instanceof Error ? reason.message : "Calibration could not be evaluated.");
    } finally {
      setCalibrating(false);
    }
  }

  const complete = job?.status === "complete";
  const artifact = (name: string) => complete ? artifactUrl(job.job_id, name) : "#";
  const artifactRecord = (name: string): Artifact | undefined => job?.artifacts.find((item) => item.name === name);
  const currentStage = stages.indexOf((job?.stage ?? "") as (typeof stages)[number]);
  const isSingleBand = job?.input.mode === "L" || job?.input.bands === 1;
  const isTiff = file ? /\.tiff?$/i.test(file.name) : false;
  const metricAllowed = job?.calibration.metric_output_allowed === true;
  const evaluation = job?.calibration.evaluation;

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
          <strong>{metricAllowed ? "Metric calibrated · metres" : "Relative surface · 0–1"}</strong>
          <p>{metricAllowed ? "Independent evidence passed the declared held-out quality gate. The viewer remains relative; metric files are separate." : "A normal image cannot establish elevation in metres. Metric export remains locked until valid vertical calibration exists."}</p>
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
            {file && localPreview && !isTiff ? <img src={localPreview} alt="Selected scene preview" /> : <ContourMark />}
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

      {complete && <>
        <section className="result-section" aria-labelledby="result-title">
          <div className="section-heading result-heading">
            <div><p className="section-label">Completed run</p><h2 id="result-title">Relative surface analysis</h2></div>
            <div className="result-actions">
              <div className="result-state"><strong>{job.scientific_state}</strong><span>3D viewer values remain relative</span></div>
              <button className="quiet-action" type="button" disabled={busy} onClick={clearResult}>Clear result</button>
            </div>
          </div>

          {isSingleBand && <div className="domain-note" role="note">
            <strong>Single-band input detected</strong>
            <span>This file was repeated into RGB for compatibility. Thermal/TIR imagery is outside this pretrained model's validated optical-image domain, so treat this run as a software demonstration—not scientific validation.</span>
          </div>}

          <div className="analysis-layout">
            <div className="viewer-column">
              <SurfaceViewer gridUrl={artifact("surface_grid")} textureUrl={artifact("texture")} onPointsChange={setPoints} />
            </div>
            <aside className="result-inspector">
              <div className="comparison-pair">
                <figure><img src={artifact("texture")} alt="Uploaded scene" /><figcaption>Input scene</figcaption></figure>
                <figure><img src={artifact("preview")} alt="Colourized relative surface" /><figcaption>Relative map</figcaption></figure>
              </div>
              <div className="interpretation">
                <h3>How to read this</h3>
                <p>The colour map and 3D shape show ordering and local structure. They do not provide absolute terrain height, building height, or elevation.</p>
              </div>
              <div className="point-inspection" aria-live="polite">
                <div><h3>Point comparison</h3><span>relative units</span></div>
                {points.length === 0 ? <p>Click the 3D surface to set point A, then point B.</p> : <>
                  <ol>
                    {points.map((point) => <li key={point.label} className={`point-${point.label.toLowerCase()}`}>
                      <strong>{point.label}</strong>
                      <span>{point.relativeValue.toFixed(3)}</span>
                      <small>pixel {point.column}, {point.row} · x {(point.xFraction * 100).toFixed(1)}% · y {(point.yFraction * 100).toFixed(1)}%</small>
                    </li>)}
                  </ol>
                  {points.length === 2 && <p className="point-difference">Absolute difference <strong>{Math.abs(points[1].relativeValue - points[0].relativeValue).toFixed(3)}</strong></p>}
                </>}
              </div>
              <details className="run-details">
                <summary>Inspect run provenance</summary>
                <dl>
                  <div><dt>Model</dt><dd>{String(job.model.checkpoint ?? "Unavailable")}</dd></div>
                  <div><dt>Revision</dt><dd className="hash">{String(job.model.revision ?? "Unavailable")}</dd></div>
                  <div><dt>Device</dt><dd>{String(job.model.device ?? "Unavailable")}</dd></div>
                  <div><dt>Inference</dt><dd>{String(job.configuration.inference_mode ?? "single_pass").replace("_", " ")}{Number(job.configuration.tile_count ?? 1) > 1 ? ` · ${String(job.configuration.tile_count)} tiles` : ""}</dd></div>
                  <div><dt>Input hash</dt><dd className="hash">{String(job.input.sha256)}</dd></div>
                  <div><dt>CRS</dt><dd>{String(job.geospatial?.crs ?? "Not supplied")}</dd></div>
                </dl>
              </details>
            </aside>
          </div>
        </section>

        {job.geospatial && <section className="calibration-section" aria-labelledby="calibration-title">
          <div className="section-heading calibration-heading">
            <div><p className="section-label">Vertical evidence gate</p><h2 id="calibration-title">Metric calibration</h2></div>
            <span className={`gate-status gate-${job.calibration.status}`}>
              {job.calibration.status === "passed" ? "Passed" : job.calibration.status === "rejected" ? "Rejected" : "Locked"}
            </span>
          </div>
          <div className="calibration-layout">
            <div className="calibration-copy">
              <h3>Use an independently sourced, pixel-aligned DSM</h3>
              <p>It must have the exact same CRS, dimensions, and pixel grid as this input. TerraFly fits scale and offset on one spatial set, then judges the result on separate held-out pixels.</p>
              <dl className="alignment-facts">
                <div><dt>Input CRS</dt><dd>{String(job.geospatial.crs)}</dd></div>
                <div><dt>Input grid</dt><dd>{String(job.input.width)} × {String(job.input.height)} pixels</dd></div>
                <div><dt>Viewer</dt><dd>Remains relative for honest visual comparison</dd></div>
              </dl>
            </div>
            <div className="calibration-form">
              <label className="reference-picker">
                <span>Reference DSM · GeoTIFF</span>
                <input aria-label="Reference DSM" type="file" accept=".tif,.tiff,image/tiff" onChange={(event) => { setReferenceFile(event.target.files?.[0] ?? null); setCalibrationError(null); }} />
                <strong>{referenceFile?.name ?? "Choose aligned DSM"}</strong>
              </label>
              <label><span>Evidence source</span><input aria-label="Evidence source" value={sourceDescription} onChange={(event) => setSourceDescription(event.target.value)} placeholder="Agency, survey, product, and date" /></label>
              <div className="calibration-fields">
                <label><span>Vertical datum</span><input aria-label="Vertical datum" value={verticalDatum} onChange={(event) => setVerticalDatum(event.target.value)} placeholder="e.g. EGM96 orthometric" /></label>
                <label><span>Maximum held-out RMSE · m</span><input aria-label="Maximum held-out RMSE" type="number" min="0.001" step="0.1" value={maxRmse} onChange={(event) => setMaxRmse(event.target.value)} /></label>
              </div>
              <button className="primary-action" type="button" disabled={calibrating || !referenceFile || !sourceDescription.trim() || !verticalDatum.trim()} onClick={evaluateCalibration}>
                {calibrating ? "Evaluating evidence…" : "Evaluate and calibrate"}
              </button>
              {calibrationError && <div className="error" role="alert">{calibrationError}</div>}
            </div>
          </div>

          {job.calibration.status !== "not_requested" && <div className={`gate-result ${metricAllowed ? "gate-pass" : "gate-fail"}`} aria-live="polite">
            <div><span>Decision</span><strong>{metricAllowed ? "Metric export unlocked" : "Metric export remains locked"}</strong><p>{job.calibration.reason}</p></div>
            {evaluation && <dl>
              <div><dt>Held-out RMSE</dt><dd>{metric(evaluation.rmse_m)} m</dd></div>
              <div><dt>MAE</dt><dd>{metric(evaluation.mae_m)} m</dd></div>
              <div><dt>Bias</dt><dd>{metric(evaluation.bias_m)} m</dd></div>
              <div><dt>R²</dt><dd>{metric(evaluation.r_squared)}</dd></div>
              <div><dt>Fit scale</dt><dd>{metric(job.calibration.fit?.scale_m_per_relative_unit)} m / relative unit</dd></div>
              <div><dt>Vertical datum</dt><dd>{job.calibration.evidence?.vertical_datum ?? "—"}</dd></div>
            </dl>}
          </div>}
        </section>}

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
            <a href={artifact("glb_mesh")} download>
              <span><strong>{artifactRecord("glb_mesh")?.filename ?? "relative_surface.glb"}</strong><small>Portable 3D mesh with embedded scene colours and relative—not metric—vertical values.</small></span>
              <b>Download · {fileSize(artifactRecord("glb_mesh")?.bytes ?? 0)}</b>
            </a>
            <a href={artifact("manifest")} download>
              <span><strong>{artifactRecord("manifest")?.filename ?? "job_manifest.json"}</strong><small>Audit record containing input hash, model revision, device, warnings, and artifact hashes.</small></span>
              <b>Download · {fileSize(artifactRecord("manifest")?.bytes ?? 0)}</b>
            </a>
            {artifactRecord("calibration_report") && <a href={artifact("calibration_report")} download>
              <span><strong>{artifactRecord("calibration_report")?.filename}</strong><small>Calibration evidence, fitted scale and offset, held-out metrics, gate thresholds, and final decision.</small></span>
              <b>Download · {fileSize(artifactRecord("calibration_report")?.bytes ?? 0)}</b>
            </a>}
            {artifactRecord("metric_geotiff") && <a href={artifact("metric_geotiff")} download>
              <span><strong>{artifactRecord("metric_geotiff")?.filename}</strong><small>Float32 calibrated elevation with the source CRS, affine transform, vertical datum, and metre units.</small></span>
              <b>Download · {fileSize(artifactRecord("metric_geotiff")?.bytes ?? 0)}</b>
            </a>}
            {artifactRecord("metric_surface") && <a href={artifact("metric_surface")} download>
              <span><strong>{artifactRecord("metric_surface")?.filename}</strong><small>Lossless float32 calibrated elevation array in metres; separate from the relative viewer grid.</small></span>
              <b>Download · {fileSize(artifactRecord("metric_surface")?.bytes ?? 0)}</b>
            </a>}
            {artifactRecord("error_geotiff") && <a href={artifact("error_geotiff")} download>
              <span><strong>{artifactRecord("error_geotiff")?.filename}</strong><small>Spatial residual map: calibrated estimate minus aligned reference DSM, in metres.</small></span>
              <b>Download · {fileSize(artifactRecord("error_geotiff")?.bytes ?? 0)}</b>
            </a>}
          </div>
          <p className={`metric-lock ${metricAllowed ? "metric-open" : ""}`}>{metricAllowed ? "Metric GeoTIFF is available because the documented held-out gate passed. The 3D viewer remains relative by design." : job.calibration.status === "rejected" ? "The submitted evidence was retained with its rejection report; no metric elevation file was produced." : "Metric GeoTIFF is intentionally absent. Submit valid vertical evidence above to evaluate the gate."}</p>
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
          <p><strong>2. Infer.</strong> Depth Anything V2 estimates relative monocular depth; large images use bounded overlapping tiles.</p>
          <p><strong>3. Inspect.</strong> TerraFly builds a 0–1 surface for orbit, first-person navigation, and two-point comparison.</p>
          <p><strong>4. Calibrate only with evidence.</strong> An aligned DSM or independent control/check points must pass held-out error gates before metric export exists.</p>
        </div>
      </details>

      <footer><span>TerraFly · Day 3 calibration and evaluation</span><span>Local processing · held-out quality gates · reproducible outputs</span></footer>
    </main>
  );
}
