/**
 * FASE 6: copia núcleo funcional a ./CODIGO_FUENTE_RECONSTRUIDO/
 * Basado en PROJECT_INDEX.json + misma lógica de validación que detect-brain.js
 */
"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = __dirname;
const OUTPUT = path.join(ROOT, "output");
const INDEX_PATH = path.join(ROOT, "PROJECT_INDEX.json");
const DEST_ROOT = path.join(ROOT, "CODIGO_FUENTE_RECONSTRUIDO");

const TARGET_CATEGORIES = new Set(["agents", "tools", "policy", "prompts"]);
const TOP_SCORE_COUNT = 28;
const MAX_FILES_CAP = 90;

/** Excluir dependencias vendor del bundle (no es “código propio” para auditoría) */
function isProjectOwnSource(relPosix) {
  return !relPosix.includes("node_modules/");
}

function hasOrchestrationCall(f) {
  if (typeof f.has_orchestration_call === "boolean") {
    return f.has_orchestration_call;
  }
  return (f.calls_detected || []).some((s) =>
    /\[run\(|\[execute\(|\[handle\(|\[dispatch\(/.test(s)
  );
}

function validateBrainCandidate(f) {
  const reasons = [];
  if ((f.imports_to_tools ?? 0) < 1) reasons.push("imports_to_tools");
  if (!hasOrchestrationCall(f)) reasons.push("orchestration");
  if (!f.has_flow_keywords) reasons.push("flow_keywords");
  return { ok: reasons.length === 0, reasons };
}

function pickBrain(files) {
  const sorted = [...files].sort(
    (a, b) => (b.weight_score || 0) - (a.weight_score || 0)
  );
  for (const f of sorted) {
    if (validateBrainCandidate(f).ok) {
      return { file: f, validated: true };
    }
  }
  return {
    file: sorted[0] || null,
    validated: false,
  };
}

function isNonEmptyFile(relPosix) {
  const abs = path.join(OUTPUT, ...relPosix.split("/"));
  try {
    return fs.statSync(abs).size > 0;
  } catch {
    return false;
  }
}

function copyOne(relPosix) {
  const from = path.join(OUTPUT, ...relPosix.split("/"));
  const to = path.join(DEST_ROOT, ...relPosix.split("/"));
  fs.mkdirSync(path.dirname(to), { recursive: true });
  fs.copyFileSync(from, to);
}

function main() {
  if (!fs.existsSync(INDEX_PATH)) {
    console.error("Falta PROJECT_INDEX.json. Ejecuta index-project.js antes.");
    process.exit(1);
  }
  if (!fs.existsSync(OUTPUT)) {
    console.error("Falta ./output.");
    process.exit(1);
  }

  const data = JSON.parse(fs.readFileSync(INDEX_PATH, "utf-8"));
  const files = data.files || [];
  const byPath = new Map(files.map((f) => [f.path, f]));

  const { file: brain, validated: brainValidated } = pickBrain(files);
  const brainPath = brain?.path || null;

  const selected = new Set();

  for (const f of files) {
    if (
      TARGET_CATEGORIES.has(f.category) &&
      isNonEmptyFile(f.path) &&
      isProjectOwnSource(f.path)
    ) {
      selected.add(f.path);
    }
  }

  const byScore = [...files]
    .filter(
      (f) =>
        isNonEmptyFile(f.path) && isProjectOwnSource(f.path)
    )
    .sort((a, b) => (b.weight_score || 0) - (a.weight_score || 0));
  for (let i = 0; i < Math.min(TOP_SCORE_COUNT, byScore.length); i++) {
    selected.add(byScore[i].path);
  }

  if (
    brainPath &&
    isNonEmptyFile(brainPath) &&
    isProjectOwnSource(brainPath)
  ) {
    selected.add(brainPath);
  }

  /** Expansión por imports internos (1 pasada + propagación acotada) */
  function expandImports(paths, maxNodes) {
    const acc = new Set(paths);
    let frontier = [...acc];
    while (frontier.length > 0 && acc.size < maxNodes) {
      const next = [];
      for (const p of frontier) {
        const e = byPath.get(p);
        if (!e || !Array.isArray(e.internal_imports)) continue;
        for (const imp of e.internal_imports) {
          if (
            !byPath.has(imp) ||
            !isNonEmptyFile(imp) ||
            !isProjectOwnSource(imp)
          ) {
            continue;
          }
          if (!acc.has(imp)) {
            acc.add(imp);
            next.push(imp);
            if (acc.size >= maxNodes) break;
          }
        }
        if (acc.size >= maxNodes) break;
      }
      frontier = next;
    }
    return acc;
  }

  let expanded = expandImports(selected, MAX_FILES_CAP * 4);

  function priority(p) {
    const f = byPath.get(p);
    if (!f) return 0;
    let s = f.weight_score || 0;
    if (brainPath && p === brainPath) s += 1e9;
    if (TARGET_CATEGORIES.has(f.category)) s += 1e6;
    if ((f.imports_to_tools || 0) > 0) s += 5000 * f.imports_to_tools;
    if ((f.imports_to_policy || 0) > 0) s += 3000 * f.imports_to_policy;
    return s;
  }

  const finalList = [...expanded]
    .filter((p) => isNonEmptyFile(p))
    .sort((a, b) => priority(b) - priority(a))
    .slice(0, MAX_FILES_CAP);

  if (fs.existsSync(DEST_ROOT)) {
    fs.rmSync(DEST_ROOT, { recursive: true, force: true });
  }
  fs.mkdirSync(DEST_ROOT, { recursive: true });

  const manifest = {
    generatedAt: new Date().toISOString(),
    brain_path: brainPath,
    brain_validated_strict: brainValidated,
    max_files: MAX_FILES_CAP,
    copied: [],
  };

  for (const p of finalList) {
    try {
      copyOne(p);
      const f = byPath.get(p);
      manifest.copied.push({
        path: p,
        category: f?.category,
        weight_score: f?.weight_score,
        reason: describeReason(p, f, brainPath),
      });
    } catch (e) {
      console.error("No copiado:", p, e.message);
    }
  }

  fs.writeFileSync(
    path.join(DEST_ROOT, "_MANIFEST.json"),
    JSON.stringify(manifest, null, 2),
    "utf-8"
  );

  console.log("Consolidación OK:", finalList.length, "archivos →", DEST_ROOT);
  console.log("SYSTEM_BRAIN:", brainPath, brainValidated ? "(validado)" : "(hipótesis)");
}

function describeReason(p, f, brainPath) {
  if (p === brainPath) return "SYSTEM_BRAIN";
  if (f && TARGET_CATEGORIES.has(f.category)) return `categoría:${f.category}`;
  if (f && (f.weight_score || 0) > 0) return "score/alto";
  return "import_relacionado";
}

main();
