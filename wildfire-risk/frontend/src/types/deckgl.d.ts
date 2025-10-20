declare module "@deck.gl/react" {
  const DeckGL: any;
  export default DeckGL;
}

declare module "@deck.gl/core" {
  export type PickingInfo = any;
}

declare module "@deck.gl/layers" {
  export const ScatterplotLayer: any;
}
