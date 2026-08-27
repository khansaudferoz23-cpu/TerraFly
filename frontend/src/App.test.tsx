import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "./App";

Object.defineProperty(URL, "createObjectURL", { value: vi.fn(() => "blob:test-scene") });
Object.defineProperty(URL, "revokeObjectURL", { value: vi.fn() });

afterEach(cleanup);

describe("TerraFly scientific contract", () => {
  it("defaults to the measured terrain workflow and keeps photo AI explicitly relative", () => {
    render(<App />);
    expect(screen.getByText(/recommended for mountains/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /build measured terrain/i })).toBeDisabled();
    fireEvent.click(screen.getByRole("button", { name: /photo ai/i }));
    expect(screen.getByText(/cannot establish elevation in metres/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /generate relative surface/i })).toBeDisabled();
    expect(screen.queryByText(/coming next/i)).not.toBeInTheDocument();
  });

  it("previews a selected photo-only file and enables the relative action", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /photo ai/i }));
    const file = new File([new Uint8Array([1, 2, 3])], "scene.png", { type: "image/png" });
    fireEvent.change(screen.getByLabelText(/choose an image/i), { target: { files: [file] } });
    expect(screen.getByText("scene.png")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /generate relative surface/i })).toBeEnabled();
  });

  it("requires both GeoTIFFs, a source, and a datum before measured terrain can run", () => {
    render(<App />);
    const imagery = new File([new Uint8Array([1])], "mountain-rgb.tif", { type: "image/tiff" });
    const dem = new File([new Uint8Array([2])], "mountain-dem.tif", { type: "image/tiff" });
    fireEvent.change(screen.getByLabelText(/choose optical geotiff/i), { target: { files: [imagery] } });
    fireEvent.change(screen.getByLabelText(/choose source dem/i), { target: { files: [dem] } });
    expect(screen.getByRole("button", { name: /build measured terrain/i })).toBeDisabled();
    fireEvent.change(screen.getByLabelText(/^dem source$/i), { target: { value: "NASA SRTMGL1 v3" } });
    fireEvent.change(screen.getByLabelText(/terrain vertical datum/i), { target: { value: "EGM96 orthometric" } });
    expect(screen.getByRole("button", { name: /build measured terrain/i })).toBeEnabled();
  });
});
