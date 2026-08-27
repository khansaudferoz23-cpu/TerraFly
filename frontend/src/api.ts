import type { Job } from "./types";

export async function createJob(file: File): Promise<Job> {
  const form = new FormData();
  form.append("upload", file);
  const response = await fetch("/api/jobs", { method: "POST", body: form });
  if (!response.ok) {
    const failure = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(failure.detail ?? "Upload failed.");
  }
  return response.json();
}

export async function createTerrainJob(
  imagery: File,
  dem: File,
  sourceDescription: string,
  verticalDatum: string,
): Promise<Job> {
  const form = new FormData();
  form.append("imagery", imagery);
  form.append("dem", dem);
  form.append("source_description", sourceDescription);
  form.append("vertical_datum", verticalDatum);
  form.append("vertical_units", "metre");
  const response = await fetch("/api/terrain-jobs", { method: "POST", body: form });
  if (!response.ok) {
    const failure = await response.json().catch(() => ({ detail: response.statusText }));
    const detail = Array.isArray(failure.detail)
      ? failure.detail.map((item: { msg?: string }) => item.msg ?? "Invalid terrain field.").join(" ")
      : failure.detail;
    throw new Error(detail ?? "Terrain generation failed.");
  }
  return response.json();
}

export async function getJob(jobId: string): Promise<Job> {
  const response = await fetch(`/api/jobs/${jobId}`);
  if (!response.ok) throw new Error("Could not read job progress.");
  return response.json();
}

export async function calibrateWithReference(
  jobId: string,
  reference: File,
  sourceDescription: string,
  verticalDatum: string,
  maxRmseM: number,
): Promise<Job> {
  const form = new FormData();
  form.append("reference", reference);
  form.append("source_description", sourceDescription);
  form.append("vertical_datum", verticalDatum);
  form.append("max_rmse_m", String(maxRmseM));
  const response = await fetch(`/api/jobs/${jobId}/calibrate/reference`, { method: "POST", body: form });
  if (!response.ok) {
    const failure = await response.json().catch(() => ({ detail: response.statusText }));
    const detail = Array.isArray(failure.detail)
      ? failure.detail.map((item: { msg?: string }) => item.msg ?? "Invalid calibration field.").join(" ")
      : failure.detail;
    throw new Error(detail ?? "Calibration could not be evaluated.");
  }
  return response.json();
}

export async function deleteJob(jobId: string): Promise<void> {
  const response = await fetch(`/api/jobs/${jobId}`, { method: "DELETE" });
  if (!response.ok) throw new Error("Could not clear this result.");
}

export function artifactUrl(jobId: string, artifactName: string): string {
  return `/api/jobs/${jobId}/artifacts/${artifactName}`;
}
