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

export async function getJob(jobId: string): Promise<Job> {
  const response = await fetch(`/api/jobs/${jobId}`);
  if (!response.ok) throw new Error("Could not read job progress.");
  return response.json();
}

export function artifactUrl(jobId: string, artifactName: string): string {
  return `/api/jobs/${jobId}/artifacts/${artifactName}`;
}

\n