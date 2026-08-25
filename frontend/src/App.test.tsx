import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "./App";

Object.defineProperty(URL, "createObjectURL", { value: vi.fn(() => "blob:test-scene") });
Object.defineProperty(URL, "revokeObjectURL", { value: vi.fn() });

afterEach(cleanup);

describe("TerraFly scientific contract", () => {
  it("does not promise metric elevation for a normal image", () => {
    render(<App />);
    expect(screen.getByText(/cannot establish elevation in metres/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /generate surface/i })).toBeDisabled();
    expect(screen.queryByText(/coming next/i)).not.toBeInTheDocument();
  });

  it("previews a selected file and enables the real action", () => {
    render(<App />);
    const file = new File([new Uint8Array([1, 2, 3])], "scene.png", { type: "image/png" });
    fireEvent.change(screen.getByLabelText(/choose an image/i), { target: { files: [file] } });
    expect(screen.getByText("scene.png")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /generate surface/i })).toBeEnabled();
  });
});
