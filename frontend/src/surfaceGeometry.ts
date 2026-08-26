import * as THREE from "three";

export type SurfaceGrid = {
  schema_version?: string;
  shape: [number, number];
  source_shape?: [number, number];
  row_indices?: number[];
  column_indices?: number[];
  orientation?: { row_zero: string; column_zero: string };
  scientific_role?: string;
  numeric_source?: string;
  analysis_grid?: string;
  values: number[];
};

export const DISPLAY_WALL_DELTA_THRESHOLD = 0.055;

export type MeasurementGrid = Omit<SurfaceGrid, "values"> & {
  values: Array<number | null>;
  units: "metre";
  vertical_datum?: string;
};

export type ReconstructedStructure = {
  id: string;
  footprint: Array<{ x_fraction: number; y_fraction: number }>;
  base_relative: number;
  roof_relative: number;
  relative_height: number;
  visual_score: number;
};

export function createStructureGeometry(
  structure: ReconstructedStructure,
  aspect: number,
): THREE.ExtrudeGeometry {
  if (structure.footprint.length < 3 || structure.relative_height <= 0 || !Number.isFinite(aspect) || aspect <= 0) {
    throw new Error("Structure candidate geometry is invalid.");
  }
  const shape = new THREE.Shape();
  structure.footprint.forEach((point, index) => {
    const worldX = (point.x_fraction - 0.5) * 10;
    const worldZ = (point.y_fraction - 0.5) * 10 * aspect;
    if (index === 0) shape.moveTo(worldX, -worldZ);
    else shape.lineTo(worldX, -worldZ);
  });
  shape.closePath();
  const geometry = new THREE.ExtrudeGeometry(shape, {
    depth: Math.max(structure.relative_height, 0.02),
    bevelEnabled: false,
    steps: 1,
  });
  geometry.rotateX(-Math.PI / 2);
  return geometry;
}

export type StructureLayer = {
  schema_version: string;
  method: string;
  scientific_role: string;
  affects_numeric_dsm: false;
  warning: string;
  structures: ReconstructedStructure[];
};

export type InspectedPoint = {
  label: "A" | "B";
  relativeValue: number;
  metricElevationM?: number | null;
  row: number;
  column: number;
  xFraction: number;
  yFraction: number;
};

function clamp01(value: number) {
  return Math.max(0, Math.min(1, value));
}

export function projectedDistanceMetres(
  transform: number[],
  horizontalUnits: string,
  sourceShape: [number, number],
  first: Pick<InspectedPoint, "xFraction" | "yFraction">,
  second: Pick<InspectedPoint, "xFraction" | "yFraction">,
): number | null {
  if (
    !horizontalUnits.toLowerCase().startsWith("met")
    || transform.length < 6
    || !transform.slice(0, 6).every(Number.isFinite)
  ) return null;
  const [rows, columns] = sourceShape;
  if (rows < 1 || columns < 1) return null;
  const deltaColumn = (second.xFraction - first.xFraction) * Math.max(columns - 1, 0);
  const deltaRow = (second.yFraction - first.yFraction) * Math.max(rows - 1, 0);
  const deltaX = transform[0] * deltaColumn + transform[1] * deltaRow;
  const deltaY = transform[3] * deltaColumn + transform[4] * deltaRow;
  const distance = Math.hypot(deltaX, deltaY);
  return Number.isFinite(distance) ? distance : null;
}

export function sampleMeasurementValue(
  grid: MeasurementGrid,
  xFraction: number,
  yFraction: number,
): number | null {
  const [rows, columns] = grid.shape;
  if (rows < 1 || columns < 1 || grid.values.length !== rows * columns) return null;
  const x = clamp01(xFraction) * Math.max(0, columns - 1);
  const y = clamp01(yFraction) * Math.max(0, rows - 1);
  const x0 = Math.floor(x);
  const y0 = Math.floor(y);
  const x1 = Math.min(x0 + 1, columns - 1);
  const y1 = Math.min(y0 + 1, rows - 1);
  const values = [
    grid.values[y0 * columns + x0],
    grid.values[y0 * columns + x1],
    grid.values[y1 * columns + x0],
    grid.values[y1 * columns + x1],
  ];
  if (values.some((value) => typeof value !== "number" || !Number.isFinite(value))) return null;
  const [topLeft, topRight, bottomLeft, bottomRight] = values as number[];
  const xWeight = x - x0;
  const yWeight = y - y0;
  const top = topLeft * (1 - xWeight) + topRight * xWeight;
  const bottom = bottomLeft * (1 - xWeight) + bottomRight * xWeight;
  return top * (1 - yWeight) + bottom * yWeight;
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

export function createSurface(
  grid: SurfaceGrid,
  exaggeration: number,
  wallDeltaThreshold = DISPLAY_WALL_DELTA_THRESHOLD,
): THREE.BufferGeometry {
  const [rows, columns] = grid.shape;
  if (rows < 2 || columns < 2 || grid.values.length !== rows * columns) {
    throw new Error("Surface grid dimensions are invalid.");
  }
  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array(rows * columns * 3);
  const uvs = new Float32Array(rows * columns * 2);
  const texturedIndices: number[] = [];
  const wallIndices: number[] = [];
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
        const triangles = [
          [index, below, right],
          [right, below, below + 1],
        ];
        for (const triangle of triangles) {
          const heights = triangle.map((vertex) => grid.values[vertex]);
          const destination = Math.max(...heights) - Math.min(...heights) >= wallDeltaThreshold
            ? wallIndices
            : texturedIndices;
          destination.push(...triangle);
        }
      }
    }
  }
  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute("uv", new THREE.BufferAttribute(uvs, 2));
  geometry.setIndex([...texturedIndices, ...wallIndices]);
  if (texturedIndices.length > 0) geometry.addGroup(0, texturedIndices.length, 0);
  if (wallIndices.length > 0) geometry.addGroup(texturedIndices.length, wallIndices.length, 1);
  geometry.userData = {
    ...geometry.userData,
    texturedTriangleCount: texturedIndices.length / 3,
    neutralWallTriangleCount: wallIndices.length / 3,
    wallDeltaThreshold,
  };
  geometry.computeVertexNormals();
  return geometry;
}
