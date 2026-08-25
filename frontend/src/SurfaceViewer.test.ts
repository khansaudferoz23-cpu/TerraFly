import { describe, expect, it } from "vitest";
import { createSurface, sampleSurfacePoint } from "./surfaceGeometry";
import type { SurfaceGrid } from "./surfaceGeometry";

const asymmetricGrid: SurfaceGrid = {
  schema_version: "1.0",
  shape: [2, 3],
  source_shape: [5, 9],
  row_indices: [0, 4],
  column_indices: [0, 4, 8],
  orientation: { row_zero: "image_top", column_zero: "image_left" },
  values: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
};

describe("surface orientation contract", () => {
  it("maps image top-left and bottom-right to distinct geometry and UV corners", () => {
    const geometry = createSurface(asymmetricGrid, 2);
    const positions = geometry.getAttribute("position");
    const uvs = geometry.getAttribute("uv");
    expect(positions.getX(0)).toBe(-5);
    expect(positions.getY(0)).toBeCloseTo(0.2);
    expect(positions.getZ(0)).toBeCloseTo(-10 / 3);
    expect([uvs.getX(0), uvs.getY(0)]).toEqual([0, 1]);
    expect(positions.getX(5)).toBe(5);
    expect(positions.getY(5)).toBeCloseTo(1.2);
    expect(positions.getZ(5)).toBeCloseTo(10 / 3);
    expect([uvs.getX(5), uvs.getY(5)]).toEqual([1, 0]);
    geometry.dispose();
  });

  it("bilinearly samples relative values and reports source-image pixels", () => {
    const topLeft = sampleSurfacePoint(asymmetricGrid, 0, 0, "A");
    const bottomRight = sampleSurfacePoint(asymmetricGrid, 1, 1, "B");
    const centre = sampleSurfacePoint(asymmetricGrid, 0.5, 0.5);
    expect(topLeft).toMatchObject({ relativeValue: 0.1, row: 0, column: 0 });
    expect(bottomRight).toMatchObject({ relativeValue: 0.6, row: 4, column: 8 });
    expect(centre.relativeValue).toBeCloseTo(0.35);
    expect(centre).toMatchObject({ row: 2, column: 4 });
  });
});
