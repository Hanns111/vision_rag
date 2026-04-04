/**
 * Extrae fuentes desde un Source Map (proyecto.map) hacia ./output
 * Uso: node extract.js
 */
"use strict";

const fs = require("fs");
const path = require("path");

const MAP_CANDIDATES = [
  path.join(__dirname, "proyecto.map"),
  path.join(__dirname, "CLAUDE_SOURCE_FINAL_60MB.map"),
].filter((p) => fs.existsSync(p));
const MAP_FILE = MAP_CANDIDATES[0];
const OUTPUT_ROOT = path.resolve(__dirname, "output");
const PROGRESS_EVERY = 100;

function ensureInsideOutput(resolvedPath, outputRoot) {
  const rel = path.relative(outputRoot, resolvedPath);
  if (rel === "" || (!rel.startsWith("..") && !path.isAbsolute(rel))) {
    return true;
  }
  return false;
}

/**
 * Normaliza la ruta del source map: sin absolutos, sin salir de la raíz virtual.
 */
function normalizeSourcePath(rawPath) {
  if (rawPath == null || typeof rawPath !== "string") {
    return "_invalid_path";
  }

  let p = String(rawPath).replace(/\\/g, "/").trim();

  // Quitar prefijos habituales de source maps (no modifica contenido de archivos)
  p = p.replace(/^webpack:\/\/\//i, "");
  p = p.replace(/^webpack:\/\//i, "");
  p = p.replace(/^file:\/\//i, "");

  // Quitar letra de unidad Windows (C:, D:, etc.)
  p = p.replace(/^[a-zA-Z]:\/?/, "");

  // Quitar raíz absoluta tipo /usr, /home — dejar segmentos relativos
  while (p.startsWith("/")) {
    p = p.slice(1);
  }

  const segments = p.split("/").filter((s) => s.length > 0);
  const stack = [];

  for (const seg of segments) {
    if (seg === "." || seg === "") continue;
    if (seg === "..") {
      if (stack.length > 0) stack.pop();
      // ".." en la raíz virtual se ignora (no sale del árbol)
      continue;
    }
    stack.push(seg);
  }

  if (stack.length === 0) {
    return "_empty_path_placeholder";
  }

  return stack.join(path.sep);
}

function main() {
  if (!MAP_FILE) {
    console.error(
      "No se encontró ningún .map. Coloca proyecto.map o CLAUDE_SOURCE_FINAL_60MB.map en esta carpeta."
    );
    process.exit(1);
  }
  console.log("Leyendo map:", MAP_FILE);

  let data;
  try {
    const raw = fs.readFileSync(MAP_FILE, "utf-8");
    data = JSON.parse(raw);
  } catch (e) {
    console.error("Error leyendo o parseando el archivo .map:", e.message);
    process.exit(1);
  }

  if (!data || typeof data !== "object") {
    console.error("El JSON del map no es un objeto válido.");
    process.exit(1);
  }

  if (!Array.isArray(data.sources)) {
    console.error('Falta o no es array: propiedad "sources"');
    process.exit(1);
  }

  if (!Array.isArray(data.sourcesContent)) {
    console.error('Falta o no es array: propiedad "sourcesContent"');
    process.exit(1);
  }

  const n = data.sources.length;
  if (data.sourcesContent.length !== n) {
    console.warn(
      `Advertencia: sources (${n}) y sourcesContent (${data.sourcesContent.length}) tienen longitudes distintas. Se usará el mínimo.`
    );
  }

  const count = Math.min(n, data.sourcesContent.length);
  let written = 0;
  let failed = 0;
  let skippedUnsafe = 0;

  // Referencias directas a arrays — sin copiar estructuras grandes a memoria extra
  const sources = data.sources;
  const sourcesContent = data.sourcesContent;

  for (let i = 0; i < count; i++) {
    const rel = normalizeSourcePath(sources[i]);
    const target = path.join(OUTPUT_ROOT, rel);

    if (!ensureInsideOutput(path.resolve(target), OUTPUT_ROOT)) {
      skippedUnsafe++;
      console.error(
        "Ruta fuera de output ignorada:",
        sources[i],
        "→",
        target
      );
      continue;
    }

    let body;
    const chunk = sourcesContent[i];
    if (chunk === null || chunk === undefined) {
      body = "";
    } else {
      body = typeof chunk === "string" ? chunk : String(chunk);
    }

    try {
      const dir = path.dirname(target);
      fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(target, body, { encoding: "utf-8" });
      written++;
    } catch (err) {
      failed++;
      console.error(
        `Error escribiendo archivo (índice ${i}):`,
        target,
        "-",
        err.message
      );
    }

    if ((i + 1) % PROGRESS_EVERY === 0 || i + 1 === count) {
      console.log(
        "Progreso:",
        i + 1,
        "/",
        count,
        "entradas revisadas —",
        written,
        "OK,",
        failed,
        "fallos,",
        skippedUnsafe,
        "rutas inseguras"
      );
    }
  }

  console.log("---");
  console.log("Total procesado:", count);
  console.log("Escritos:", written);
  console.log("Fallos:", failed);
  console.log("Rutas inseguras omitidas:", skippedUnsafe);
  console.log("Salida:", OUTPUT_ROOT);
}

main();
