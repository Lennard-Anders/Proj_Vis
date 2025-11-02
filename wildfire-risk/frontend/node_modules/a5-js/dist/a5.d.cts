import { quat } from 'gl-matrix';

type Degrees = number & {
    __brand: 'Degrees';
};
type Radians = number & {
    __brand: 'Radians';
};
/**
 * 3D spherical coordinate system centered on unit sphere/dodecahedron
 */
type Spherical = [theta: Radians, phi: Radians] & {
    __brand: 'Spherical';
};
/**
 * Geographic longitude & latitude
 */
type LonLat = [longitude: Degrees, latitude: Degrees] & {
    __brand: 'LonLat';
};

/**
 * Orientation of the Hilbert curve. The curve fills a space defined by the triangle with vertices
 * u, v & w. The orientation describes which corner the curve starts and ends at, e.g. wv is a
 * curve that starts at w and ends at v.
 */
type Orientation = 'uv' | 'vu' | 'uw' | 'wu' | 'vw' | 'wv';

type OriginId = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11;
type Origin = {
    id: OriginId;
    axis: Spherical;
    quat: quat;
    inverseQuat: quat;
    angle: Radians;
    orientation: Orientation[];
    firstQuintant: number;
};
type A5Cell = {
    /**
     * Origin representing one of pentagon face of the dodecahedron
     */
    origin: Origin;
    /**
     * Index (0-4) of triangular segment within pentagonal dodecahedron face
     */
    segment: number;
    /**
     * Position along Hilbert curve within triangular segment
     */
    S: bigint;
    /**
     * Resolution of the cell
     */
    resolution: number;
};

declare function lonLatToCell(lonLat: LonLat, resolution: number): bigint;
declare function cellToLonLat(cell: bigint): LonLat;
type CellToBoundaryOptions = {
    /**
     * Pass true to close the ring with the first point
     * @default true
     */
    closedRing?: boolean;
    /**
     * Number of segments to use for each edge. Pass 'auto' to use the resolution of the cell.
     * @default 'auto'
     */
    segments?: number | 'auto';
};
declare function cellToBoundary(cellId: bigint, { closedRing, segments }?: CellToBoundaryOptions): LonLat[];

declare function hexToU64(hex: string): bigint;
declare function u64ToHex(index: bigint): string;

declare function getResolution(index: bigint): number;
declare function cellToChildren(index: bigint, childResolution?: number): bigint[];
declare function cellToParent(index: bigint, parentResolution?: number): bigint;
/**
 * Returns resolution 0 cells of the A5 system, which serve as a starting point
 * for all higher-resolution subdivisions in the hierarchy.
 *
 * @returns Array of 12 cell indices
 */
declare function getRes0Cells(): bigint[];

/**
 * Returns the number of cells at a given resolution.
 *
 * @param resolution The resolution level (use BigInt for exact value for high resolutions, 28+)
 * @returns Number of cells at the given resolution
 */
declare function getNumCells(resolution: number): number;
declare function getNumCells(resolution: bigint): bigint;
/**
 * Returns the area of a cell at a given resolution in square kilometers.
 *
 * @param resolution The resolution level
 * @returns Area of a cell in square meters
 */
declare function cellArea(resolution: number): number;

export { type A5Cell, type Degrees, type Radians, cellArea, cellToBoundary, cellToChildren, cellToLonLat, cellToParent, getNumCells, getRes0Cells, getResolution, hexToU64, lonLatToCell, u64ToHex };
