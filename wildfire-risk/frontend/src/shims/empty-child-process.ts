// Browser shim for node:child_process used by loaders.gl worker-utils (spawn import)
export const spawn = (..._args: any[]) => {
  throw new Error("child_process.spawn is not available in the browser build");
};
export default { spawn };
