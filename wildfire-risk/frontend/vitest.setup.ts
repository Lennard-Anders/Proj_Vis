import "@testing-library/jest-dom";
// Ensure Vitest's expect picks up the jest-dom matchers in TypeScript as well
// by augmenting the namespace when necessary. This import is sufficient at runtime,
// but the tsconfig also includes @testing-library/jest-dom types for editor IntelliSense.
