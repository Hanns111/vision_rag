/**
 * Analiza ./output en busca de patrones en .js / .ts / .tsx y genera ANALISIS.md
 * Uso: node analyze.js
 */
"use strict";

const fs = require("fs");
const path = require("path");

const OUTPUT_ROOT = path.resolve(__dirname, "output");
const REPORT_FILE = path.join(__dirname, "ANALISIS.md");
const MAX_FILE_BYTES = 2 * 1024 * 1024; // 2 MB — omitir archivos más grandes
const CONTEXT_BEFORE = 3;
const CONTEXT_AFTER = 3;

/** Palabras/frases a buscar (case-insensitive vía regex) */
const PATTERN_STRINGS = [
  "prompt",
  "system_prompt",
  "tool",
  "agent",
  "policy",
  "constraint",
  "security",
  "filesystem",
  "execute",
  "command",
  "Cairos",
  "Ultra Plan",
];

function buildCombinedRegex() {
  const escaped = PATTERN_STRINGS.map((s) =>
    s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
  );
  return new RegExp(escaped.join("|"), "i");
}

const COMBINED_REGEX = buildCombinedRegex();

const EXT_OK = new Set([".js", ".ts", ".tsx"]);

function* walkDir(dir) {
  let entries;
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch (e) {
    console.error("No se pudo leer directorio:", dir, e.message);
    return;
  }
  for (const ent of entries) {
    const full = path.join(dir, ent.name);
    if (ent.isDirectory()) {
      yield* walkDir(full);
    } else if (ent.isFile()) {
      yield full;
    }
  }
}

function relFromRoot(absPath) {
  return path.relative(OUTPUT_ROOT, absPath).split(path.sep).join("/");
}

function analyzeFile(absPath, seenSnippets) {
  let stat;
  try {
    stat = fs.statSync(absPath);
  } catch (e) {
    return [];
  }

  if (stat.size > MAX_FILE_BYTES) {
    return [];
  }

  const ext = path.extname(absPath).toLowerCase();
  if (!EXT_OK.has(ext)) {
    return [];
  }

  let content;
  try {
    content = fs.readFileSync(absPath, { encoding: "utf-8" });
  } catch (e) {
    console.error("Lectura fallida:", absPath, e.message);
    return [];
  }

  const lines = content.split(/\r?\n/);
  const blocks = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!COMBINED_REGEX.test(line)) {
      COMBINED_REGEX.lastIndex = 0;
      continue;
    }
    COMBINED_REGEX.lastIndex = 0;

    const start = Math.max(0, i - CONTEXT_BEFORE);
    const end = Math.min(lines.length, i + CONTEXT_AFTER + 1);
    const fragmentLines = lines.slice(start, end);
    const fragment = fragmentLines.join("\n");

    const key = relFromRoot(absPath) + "\0" + start + "\0" + end + "\0" + fragment;
    if (seenSnippets.has(key)) {
      continue;
    }
    seenSnippets.add(key);
    blocks.push({ startLine: start + 1, endLine: end, fragment });
  }

  return blocks;
}

function fenceLang(ext) {
  if (ext === ".tsx" || ext === ".ts") return "ts";
  if (ext === ".js") return "js";
  return "text";
}

function main() {
  if (!fs.existsSync(OUTPUT_ROOT)) {
    console.error('No existe la carpeta "./output". Ejecuta primero extract.js.');
    process.exit(1);
  }

  const seenSnippets = new Set();
  const sections = [];

  let filesScanned = 0;
  let filesWithHits = 0;

  for (const absPath of walkDir(OUTPUT_ROOT)) {
    filesScanned++;
    const blocks = analyzeFile(absPath, seenSnippets);
    if (blocks.length === 0) continue;

    filesWithHits++;
    const rel = relFromRoot(absPath);
    const lang = fenceLang(path.extname(absPath).toLowerCase());

    let md = `## Archivo: ${rel}\n\n`;
    for (const b of blocks) {
      md += `Líneas aprox. ${b.startLine}-${b.endLine}\n\n`;
      md += "```" + lang + "\n";
      md += b.fragment;
      md += "\n```\n\n";
    }
    sections.push(md);
  }

  const header = `# Análisis de patrones\n\n- Raíz: \`./output\`\n- Extensiones: .js, .ts, .tsx\n- Archivos > ${MAX_FILE_BYTES} bytes ignorados\n- Patrones (case-insensitive): ${PATTERN_STRINGS.join(", ")}\n\n`;

  const out = header + sections.join("\n");

  try {
    fs.writeFileSync(REPORT_FILE, out, { encoding: "utf-8" });
  } catch (e) {
    console.error("No se pudo escribir ANALISIS.md:", e.message);
    process.exit(1);
  }

  console.log("Archivos recorridos:", filesScanned);
  console.log("Archivos con coincidencias:", filesWithHits);
  console.log("Informe:", REPORT_FILE);
}

main();
