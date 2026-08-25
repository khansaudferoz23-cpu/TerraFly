import * as THREE from "three";

export type SurfaceGrid = {
  schema_version?: string;
  shape: [number, number];
  source_shape?: [number, number];
  row_indices?: number[];
  column_indices?: number[];
  orientation?: { row_zero: string; column_zero: string };
  values: number[];
};

export type InspectedPoint = {
  label: "A" | "B";
  relativeValue: number;
  row: number;
  column: number;
  xFraction: number;
  yFraction: number;
};

function clamp01(value: number) {
  return Math.max(0, Math.min(1, value));
}

export function sampleSurfacePoint(
  grid: SurfaceGrid,
  xFraction: number,
  yFraction: number,
  label: "A" | "B" = "A",
): InspectedPoint {
  const [rows, columns] = grid.shape;
  const x = clamp01(xFraction) * Math.max(0, columns - 1);
  const y = clamp01(yFraction) * Math.max(0, rows - 1);
  const x0 = Math.floor(x);
  const y0 = Math.floor(y);
  const x1 = Math.min(x0 + 1, columns - 1);
  const y1 = Math.min(y0 + 1, rows - 1);
  const xWeight = x - x0;
  const yWeight = y - y0;
  const valueAt = (row: number, column: number) => grid.values[row * columns + column];
  const top = valueAt(y0, x0) * (1 - xWeight) + valueAt(y0, x1) * xWeight;
  const bottom = valueAt(y1, x0) * (1 - xWeight) + valueAt(y1, x1) * xWeight;
  const relativeValue = top * (1 - yWeight) + bottom * yWeight;
  const [sourceRows, sourceColumns] = grid.source_shape ?? grid.shape;
  return {
    label,
    relativeValue,
    row: Math.round(clamp01(yFraction) * Math.max(0, sourceRows - 1)),
    column: Math.round(clamp01(xFraction) * Math.max(0, sourceColumns - 1)),
    xFraction: clamp01(xFraction),
    yFraction: clamp01(yFraction),
  };
}

export function createSurface(grid: SurfaceGrid, exaggeration: number): THREE.BufferGeometry {
  const [rows, columns] = grid.shape;
  if (rows < 2 || columns < 2 || grid.values.length !== rows * columns) {
    throw new Error("Surface grid dimensions are invalid.");
  }
  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array(rows * columns * 3);
  const uvs = new Float32Array(rows * columns * 2);
  const indices: number[] = [];
  const aspect = rows / columns;
  for (let row = 0; row < rows; row += 1) {
    for (let column = 0; column < columns; column += 1) {
      const index = row * columns + column;
      positions[index * 3] = (column / (columns - 1) - 0.5) * 10;
      positions[index * 3 + 1] = grid.values[index] * exaggeration;
      positions[index * 3 + 2] = (row / (rows - 1) - 0.5) * 10 * aspect;
      uvs[index * 2] = column / (columns - 1);
      uvs[index * 2 + 1] = 1 - row / (rows - 1);
      if (row < rows - 1 && column < columns - 1) {
        const right = index + 1;
        const below = index + columns;
        indices.push(index, below, right, right, below, below + 1);
      }
    }
  }
  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute("uv", new THREE.BufferAttribute(uvs, 2));
  geometry.setIndex(indices);
  geometry.computeVertexNormals();
  return geometry;
}
