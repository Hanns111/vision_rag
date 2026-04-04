/**
 * FASE 4: ejecuta extract → index → detect-brain → consolidate → verify
 */
"use strict";

const { spawnSync } = require("child_process");
const path = require("path");

const steps = [
  "extract.js",
  "index-project.js",
  "detect-brain.js",
  "consolidate.js",
  "verify.js",
];

for (const s of steps) {
  console.log("\n>>> node", s, "\n");
  const r = spawnSync(process.execPath, [path.join(__dirname, s)], {
    cwd: __dirname,
    stdio: "inherit",
  });
  if (r.status !== 0) {
    console.error("Falló:", s, "código", r.status);
    process.exit(r.status ?? 1);
  }
}
console.log("\nPipeline completo.\n");
