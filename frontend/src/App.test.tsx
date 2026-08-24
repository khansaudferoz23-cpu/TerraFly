import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import App from "./App";

describe("TerraFly scientific contract", () => {
  it("does not promise metric elevation for a normal image", () => {
    render(<App />);
    expect(screen.getByText(/cannot reveal elevation in metres/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /generate relative surface/i })).toBeDisabled();
  });
});
