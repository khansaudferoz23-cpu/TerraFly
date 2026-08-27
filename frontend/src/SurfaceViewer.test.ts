import { describe, expect, it } from "vitest";
import { createStructureGeometry, createSurface, heightColours, projectedDistanceMetres, sampleMeasurementValue, sampleSurfacePoint } from "./surfaceGeometry";
import type { MeasurementGrid, ReconstructedStructure, SurfaceGrid } from "./surfaceGeometry";

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

  it("separates steep faces into a neutral-wall material group", () => {
    const displayGrid: SurfaceGrid = {
      shape: [3, 3],
      values: [
        0.1, 0.1, 0.1,
        0.1, 0.8, 0.8,
        0.1, 0.8, 0.8,
      ],
    };
    const geometry = createSurface(displayGrid, 1.4);
    expect(geometry.groups.some((group) => group.materialIndex === 0)).toBe(true);
    expect(geometry.groups.some((group) => group.materialIndex === 1)).toBe(true);
    expect(geometry.userData.neutralWallTriangleCount).toBeGreaterThan(0);
    expect(geometry.userData.texturedTriangleCount).toBeGreaterThan(0);
    expect(geometry.userData.neutralWallTriangleCount + geometry.userData.texturedTriangleCount).toBe(8);
    geometry.dispose();
  });

  it("builds truthful relative and metric height colour scales", () => {
    const relative = heightColours(asymmetricGrid);
    expect(relative.legend).toEqual({
      minimum: 0.1,
      midpoint: 0.35,
      maximum: 0.6,
      units: "relative — not metres",
    });
    expect(relative.colours).toHaveLength(asymmetricGrid.values.length * 3);
    expect(relative.colours[0]).toBeLessThan(relative.colours.at(-3) ?? 0);

    const metricGrid: MeasurementGrid = {
      ...asymmetricGrid,
      units: "metre",
      values: [100, 110, 120, null, 140, 150],
    };
    const metric = heightColours(metricGrid);
    expect(metric.legend).toEqual({
      minimum: 100,
      midpoint: 125,
      maximum: 150,
      units: "metres",
    });
    expect(Array.from(metric.colours).every(Number.isFinite)).toBe(true);
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

  it("samples calibrated metre elevations and refuses NoData neighbourhoods", () => {
    const metricGrid: MeasurementGrid = {
      ...asymmetricGrid,
      units: "metre",
      values: [101, 102, 103, 104, 105, 106],
    };
    expect(sampleMeasurementValue(metricGrid, 0.5, 0.5)).toBeCloseTo(103.5);
    metricGrid.values[1] = null;
    expect(sampleMeasurementValue(metricGrid, 0.5, 0)).toBeNull();
  });

  it("extrudes a visual structure upward from its separate base plane", () => {
    const structure: ReconstructedStructure = {
      id: "candidate-test",
      footprint: [
        { x_fraction: 0.4, y_fraction: 0.4 },
        { x_fraction: 0.6, y_fraction: 0.4 },
        { x_fraction: 0.6, y_fraction: 0.6 },
        { x_fraction: 0.4, y_fraction: 0.6 },
      ],
      base_relative: 0.2,
      roof_relative: 0.5,
      relative_height: 0.3,
      visual_score: 0.7,
    };
    const geometry = createStructureGeometry(structure, 1);
    geometry.computeBoundingBox();
    expect(geometry.boundingBox?.min.y).toBeCloseTo(0);
    expect(geometry.boundingBox?.max.y).toBeCloseTo(0.3);
    expect(geometry.boundingBox?.min.x).toBeCloseTo(-1);
    expect(geometry.boundingBox?.max.x).toBeCloseTo(1);
    geometry.dispose();
  });

  it("uses fractional source pixels and a projected affine transform for distance", () => {
    const first = { xFraction: 0, yFraction: 0 };
    const second = { xFraction: 0.5, yFraction: 0.5 };
    expect(projectedDistanceMetres(
      [2, 0, 500000, 0, -2, 2000000],
      "metre",
      [5, 9],
      first,
      second,
    )).toBeCloseTo(Math.sqrt(80));
    expect(projectedDistanceMetres(
      [0.0001, 0, 70, 0, -0.0001, 20],
      "degree",
      [5, 9],
      first,
      second,
    )).toBeNull();
  });
});
