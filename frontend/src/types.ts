export type ScientificState = "Relative" | "Georeferenced Relative" | "Metric Calibrated";

export type Artifact = {
  name: string;
  filename: string;
  media_type: string;
  sha256: string;
  bytes: number;
};

export type Calibration = {
  method?: string | null;
  status: "not_requested" | "passed" | "rejected" | string;
  metric_output_allowed: boolean;
  reason: string;
  evidence?: {
    source_description?: string;
    vertical_datum?: string;
    reference_filename?: string;
  };
  fit?: {
    scale_m_per_relative_unit?: number;
    offset_m?: number;
    training_inlier_ratio?: number;
  };
  evaluation?: {
    count?: number;
    rmse_m?: number;
    mae_m?: number;
    bias_m?: number;
    r_squared?: number;
  };
  quality_gate?: {
    declared_max_rmse_m?: number;
    failures?: string[];
  };
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
  calibration: Calibration;
  model: Record<string, unknown>;
  configuration: Record<string, unknown>;
  warnings: string[];
  error: string | null;
  artifacts: Artifact[];
};
