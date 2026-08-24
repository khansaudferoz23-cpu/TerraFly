export type ScientificState = "Relative" | "Georeferenced Relative" | "Metric Calibrated";

export type Artifact = {
  name: string;
  filename: string;
  media_type: string;
  sha256: string;
  bytes: number;
};

export type Job = {
  job_id: string;
  status: "queued" | "running" | "complete" | "failed";
  stage: string;
  progress: number;
  input: Record<string, unknown>;
  scientific_state: ScientificState;
  units: string;
  geospatial: Record<string, unknown> | null;
  calibration: { metric_output_allowed: boolean; reason: string; status: string };
  model: Record<string, unknown>;
  warnings: string[];
  error: string | null;
  artifacts: Artifact[];
};

\n