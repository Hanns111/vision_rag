/**
 * Lee PROJECT_INDEX.json + código en ./output → SYSTEM_BRAIN.md
 * Valida cerebro operativo (imports a tools + llamadas + flujo).
 * Uso: node detect-brain.js
 */
"use strict";

const fs = require("fs");
const path = require("path");

const OUTPUT_ROOT = path.resolve(__dirname, "output");
const INDEX_PATH = path.join(__dirname, "PROJECT_INDEX.json");
const REPORT = path.join(__dirname, "SYSTEM_BRAIN.md");

const LOOP_RE =
  /\bplan\b|\bplanner\b|\bexecute\b|\bexecutor\b|\bvalidate\b|\bvalidator\b|\btool\b|\bprompt\b|\bpolicy\b/gi;

const ENTRY_CONFIRM_RE = [
  [/require\.main\s*===\s*module/i, "CommonJS: require.main === module"],
  [/import\.meta\.main\b/i, "Bun/ESM: import.meta.main"],
  [/\bfunction\s+main\s*\(/i, "Declaración function main("],
  [/\basync\s+function\s+main\s*\(/i, "Declaración async function main("],
  [/\bvoid\s+main\s*\(/i, "Patrón void main("],
  [/process\.argv/i, "Uso de process.argv (CLI)"],
];

function readIndex() {
  if (!fs.existsSync(INDEX_PATH)) {
    console.error("Falta PROJECT_INDEX.json. Ejecuta: node index-project.js");
    process.exit(1);
  }
  const raw = fs.readFileSync(INDEX_PATH, "utf-8");
  const data = JSON.parse(raw);
  if (!data || !Array.isArray(data.files)) {
    console.error("PROJECT_INDEX.json inválido: se esperaba .files[]");
    process.exit(1);
  }
  return data;
}

function loadLines(relPath) {
  const abs = path.join(OUTPUT_ROOT, ...relPath.split("/"));
  try {
    return fs.readFileSync(abs, "utf-8").split(/\r?\n/);
  } catch {
    return null;
  }
}

function firstMatchLines(lines, regexList) {
  const hits = [];
  if (!lines) return hits;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    for (const [re, label] of regexList) {
      re.lastIndex = 0;
      if (re.test(line)) {
        hits.push({ line: i + 1, label, text: line.trim() });
        break;
      }
    }
  }
  return hits;
}

function loopEvidenceLines(lines, max = 12) {
  const out = [];
  if (!lines) return out;
  for (let i = 0; i < lines.length && out.length < max; i++) {
    LOOP_RE.lastIndex = 0;
    if (LOOP_RE.test(lines[i])) {
      const lo = Math.max(0, i - 2);
      const hi = Math.min(lines.length, i + 3);
      out.push({
        start: lo + 1,
        end: hi,
        text: lines.slice(lo, hi).join("\n"),
      });
    }
  }
  return out;
}

function internalImportCount(f) {
  if (Array.isArray(f.internal_imports)) return f.internal_imports.length;
  return (f.imports || []).filter((x) => !String(x).startsWith("external:"))
    .length;
}

/** Llamada tipo orquestación (índice nuevo usa flag; antiguo: muestra en calls_detected) */
function hasOrchestrationCall(f) {
  if (typeof f.has_orchestration_call === "boolean") {
    return f.has_orchestration_call;
  }
  return (f.calls_detected || []).some((s) =>
    /\[run\(|\[execute\(|\[handle\(|\[dispatch\(/.test(s)
  );
}

/**
 * Validación estricta SYSTEM_BRAIN (según especificación).
 * Devuelve { ok, reasons[] }
 */
function validateBrainCandidate(f) {
  const reasons = [];
  const tools = f.imports_to_tools ?? 0;
  if (tools < 1) {
    reasons.push(
      "No importa (resuelto) ningún módulo categorizado como `tools` (imports_to_tools === 0)."
    );
  }
  if (!hasOrchestrationCall(f)) {
    reasons.push(
      "Sin evidencia estática de llamadas `run(` / `execute(` / `handle(` / `dispatch(` en `calls_detected`."
    );
  }
  if (!f.has_flow_keywords) {
    reasons.push(
      "Sin palabras de flujo indexadas (plan/planner/tool/validate/validator)."
    );
  }
  return { ok: reasons.length === 0, reasons };
}

function pickBrain(files) {
  const sorted = [...files].sort((a, b) => b.weight_score - a.weight_score);
  for (const f of sorted) {
    const v = validateBrainCandidate(f);
    if (v.ok) return { file: f, validated: true, failureReasons: [] };
  }
  const top = sorted[0];
  const v = top ? validateBrainCandidate(top) : { reasons: ["índice vacío"] };
  return {
    file: top || null,
    validated: false,
    failureReasons: top ? v.reasons : ["índice vacío"],
  };
}

function mdFence(lang, body) {
  return "```" + lang + "\n" + body + "\n```\n";
}

function main() {
  if (!fs.existsSync(OUTPUT_ROOT)) {
    console.error("No existe ./output.");
    process.exit(1);
  }

  const { files } = readIndex();
  const rankedWeight = [...files].sort(
    (a, b) => (b.weight_score || 0) - (a.weight_score || 0)
  );
  const maxIn =
    rankedWeight.length > 0
      ? Math.max(...files.map((f) => f.imported_by.length))
      : 0;
  const threshold = maxIn > 0 ? Math.max(2, Math.floor(maxIn * 0.35)) : 0;

  const entryProbable = files.filter((f) => f.imported_by.length === 0);
  const confirmed = [];

  for (const f of files) {
    const lines = loadLines(f.path);
    if (!lines) continue;
    const hits = firstMatchLines(lines, ENTRY_CONFIRM_RE);
    if (hits.length) {
      confirmed.push({
        path: f.path,
        kind: "entrypoint_confirmado",
        reasons: hits,
      });
    }
  }

  const core = files.filter(
    (f) => f.imported_by.length >= threshold && threshold > 0
  );
  const supporting = files.filter((f) => !core.includes(f));

  const brainPick = pickBrain(files);
  const brain = brainPick.file;
  const brainPath = brain?.path;
  const brainLines = brainPath ? loadLines(brainPath) : null;
  const brainSnips = brainLines ? loopEvidenceLines(brainLines, 10) : [];

  const sections = [];

  sections.push("# SYSTEM BRAIN ANALYSIS\n");
  sections.push(
    "_Fuente: `./output` + `PROJECT_INDEX.json`. Evidencia estática; lo marcado como **hipótesis** incumple criterios estrictos de validación._\n"
  );

  sections.push("## 1. Entrypoints detectados\n");
  sections.push("### entrypoint_confirmado\n");
  if (confirmed.length === 0) {
    sections.push("_Ningún patrón explícito de arranque coincide._\n");
  } else {
    for (const c of confirmed) {
      sections.push(`- **\`${c.path}\`**\n`);
      for (const h of c.reasons) {
        sections.push(
          `  - Línea ${h.line}: ${h.label} — \`${h.text.slice(0, 220)}${h.text.length > 220 ? "…" : ""}\`\n`
        );
      }
    }
  }

  sections.push("\n### entrypoint_probable (sin importadores internos)\n");
  if (entryProbable.length === 0) {
    sections.push("_Ninguno o grafo completo._\n");
  } else {
    for (const f of entryProbable.slice(0, 80)) {
      sections.push(
        `- \`${f.path}\` — ext **${f.external_imports_count ?? "?"}** / int **${f.internal_imports_count ?? internalImportCount(f)}**, score **${f.weight_score ?? "n/a"}**\n`
      );
    }
  }

  sections.push("\n## 2. Ranking por `weight_score` (top 25)\n");
  sections.push(
    "Fórmula (ver `index-project.js`): `imported_by×2 + internal×1.5 + calls×2 + imports_to_tools×3 + imports_to_policy×3 + keywords(plan/execute/tool/validate)×2`.\n\n"
  );
  rankedWeight.slice(0, 25).forEach((f, i) => {
    const role =
      f.imported_by.length >= threshold && threshold > 0
        ? "core_module"
        : "supporting_module";
    const v = validateBrainCandidate(f);
    const tag = v.ok ? "✓ candidato válido cerebro" : "—";
    sections.push(
      `${i + 1}. \`${f.path}\` — **score ${f.weight_score ?? 0}** (${role}) | →tools ${f.imports_to_tools ?? 0} →policy ${f.imports_to_policy ?? 0} | calls ${(f.calls_detected || []).length} ${tag}\n`
    );
  });

  sections.push("\n### core_module (umbral importadores)\n");
  if (core.length === 0) {
    sections.push("_Ninguno._\n");
  } else {
    core
      .sort((a, b) => b.imported_by.length - a.imported_by.length)
      .forEach((f) =>
        sections.push(`- \`${f.path}\` — ${f.imported_by.length} importadores\n`)
      );
  }

  sections.push("\n### supporting_module (muestra)\n");
  supporting
    .sort((a, b) => a.path.localeCompare(b.path))
    .slice(0, 35)
    .forEach((f) =>
      sections.push(`- \`${f.path}\` — score ${f.weight_score ?? 0}\n`)
    );

  sections.push("\n## 3. SYSTEM_BRAIN\n");
  if (!brain || !brainPath) {
    sections.push("_No hay archivos en el índice._\n");
  } else {
    const v = validateBrainCandidate(brain);
    if (!brainPick.validated) {
      sections.push(
        "### Estado: **HIPÓTESIS** (ningún archivo pasó validación estricta)\n\n"
      );
      sections.push(
        "Ningún fichero cumple simultáneamente: `imports_to_tools ≥ 1`, llamadas `run`/`execute`/`handle`/`dispatch` en `calls_detected`, y `has_flow_keywords`. Se muestra el mayor `weight_score` como candidato débil.\n\n"
      );
      sections.push("**Motivos de rechazo (criterio global):**\n");
      for (const r of brainPick.failureReasons) {
        sections.push(`- ${r}\n`);
      }
      sections.push("\n");
    } else {
      sections.push(
        "### Estado: **VALIDADO** (evidencia mínima según reglas)\n\n"
      );
    }

    sections.push(`**Archivo:** \`${brainPath}\`\n\n`);
    sections.push(
      `- **weight_score:** ${brain.weight_score}\n- **imported_by:** ${brain.imported_by.length}\n- **internal_imports:** ${brain.internal_imports?.length ?? internalImportCount(brain)}\n- **external_imports:** ${brain.external_imports?.length ?? "n/a"}\n- **imports_to_tools / agents / policy / prompts:** ${brain.imports_to_tools} / ${brain.imports_to_agents} / ${brain.imports_to_policy} / ${brain.imports_to_prompts}\n- **calls_detected (muestra):** ${(brain.calls_detected || []).slice(0, 12).length} de ${(brain.calls_detected || []).length}\n\n`
    );

    sections.push("**Imports internos (muestra):**\n");
    (brain.internal_imports || [])
      .slice(0, 25)
      .forEach((p) => sections.push(`- \`${p}\`\n`));

    sections.push("\n**Paquetes externos (muestra):**\n");
    (brain.external_imports || [])
      .slice(0, 20)
      .forEach((p) => sections.push(`- \`${p}\`\n`));

    sections.push("\n**Evidencia: `calls_detected` (hasta 20)**\n\n");
    if (!(brain.calls_detected || []).length) {
      sections.push("_Vacío._\n");
    } else {
      sections.push(
        mdFence("text", (brain.calls_detected || []).slice(0, 20).join("\n"))
      );
    }

    sections.push("\n**Evidencia: fragmentos con vocabulario de loop**\n");
    if (brainSnips.length === 0) {
      sections.push("_Pocas coincidencias._\n");
    } else {
      for (const ev of brainSnips) {
        sections.push(`Líneas ${ev.start}-${ev.end}:\n`);
        sections.push(mdFence("ts", ev.text));
      }
    }
  }

  sections.push("\n## 4. Flujo reconstruido (llamadas, no solo imports)\n");
  sections.push(
    "_Ordén **no** inferido del runtime. Secuencia sugerida solo porque aparecen patrones de llamada en el código indexado._\n\n"
  );
  if (brain && (brain.calls_detected || []).length > 0) {
    const flowLines = (brain.calls_detected || [])
      .filter((s) =>
        /\[run\(|\[execute\(|\[handle\(|\[dispatch\(|\[call:/.test(s)
      )
      .slice(0, 15);
    sections.push(mdFence("text", flowLines.join("\n") || "(sin subconjunto)"));
  } else {
    sections.push("_Sin candidato o sin llamadas detectadas._\n");
  }

  sections.push("\n## 5. Cadena conceptual (imports por categoría)\n");
  sections.push(
    mdFence(
      "text",
      "prompts → agents → tools (imports_to_*) → policy / externos (framework)"
    )
  );

  sections.push("\n## 6. Limitaciones\n");
  sections.push(
    "- Análisis estático: sin CFG ni TypeScript real.\n- Imports dinámicos con variables no resueltos.\n- `call:foo(` puede ser falso positivo si `foo` no es el mismo binding.\n"
  );

  fs.writeFileSync(REPORT, sections.join("\n"), "utf-8");
  console.log("Escrito:", REPORT);
  if (brainPath) {
    console.log(
      "SYSTEM_BRAIN:",
      brainPath,
      brainPick.validated ? "(validado)" : "(hipótesis)"
    );
  }
}

main();
