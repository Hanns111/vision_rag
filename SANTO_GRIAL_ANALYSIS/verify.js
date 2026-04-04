/**
 * FASE 5: verificación del pipeline + checklist
 */
"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = __dirname;
const OUTPUT = path.join(ROOT, "output");

function walkExt(dir, acc, exts) {
  let list;
  try {
    list = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return;
  }
  for (const e of list) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) walkExt(full, acc, exts);
    else if (exts.has(path.extname(e.name).toLowerCase())) acc.push(full);
  }
}

function main() {
  const items = [
    {
      key: "output generado",
      ok: fs.existsSync(OUTPUT) && fs.statSync(OUTPUT).isDirectory(),
    },
    {
      key: "código fuente extraído (.js/.ts/.tsx en output)",
      ok: false,
    },
    {
      key: "indexación completa (PROJECT_INDEX.json)",
      ok: fs.existsSync(path.join(ROOT, "PROJECT_INDEX.json")),
    },
    {
      key: "árbol (PROJECT_TREE.md)",
      ok: fs.existsSync(path.join(ROOT, "PROJECT_TREE.md")),
    },
    {
      key: "grafo generado (DEPENDENCY_GRAPH.md)",
      ok: fs.existsSync(path.join(ROOT, "DEPENDENCY_GRAPH.md")),
    },
    {
      key: "cerebro detectado (SYSTEM_BRAIN.md)",
      ok: fs.existsSync(path.join(ROOT, "SYSTEM_BRAIN.md")),
    },
    {
      key: "consolidación (CODIGO_FUENTE_RECONSTRUIDO/)",
      ok: fs.existsSync(path.join(ROOT, "CODIGO_FUENTE_RECONSTRUIDO")),
    },
  ];

  const exts = new Set([".js", ".ts", ".tsx"]);
  const srcFiles = [];
  if (items[0].ok) walkExt(OUTPUT, srcFiles, exts);
  items[1].ok = srcFiles.length > 0;

  console.log("\n=== CHECKLIST ===\n");
  let allOk = true;
  for (const it of items) {
    const mark = it.ok ? "[OK]" : "[FALTA]";
    if (!it.ok) allOk = false;
    console.log(mark, it.key);
  }
  console.log("\n=================\n");

  if (!allOk) {
    process.exitCode = 1;
  }

  let totalOutput = 0;
  function countAll(d) {
    for (const e of fs.readdirSync(d, { withFileTypes: true })) {
      const full = path.join(d, e.name);
      if (e.isDirectory()) countAll(full);
      else totalOutput++;
    }
  }
  if (items[0].ok) countAll(OUTPUT);

  let consolidated = 0;
  const consDir = path.join(ROOT, "CODIGO_FUENTE_RECONSTRUIDO");
  if (fs.existsSync(consDir)) {
    function countNoManifest(d) {
      for (const e of fs.readdirSync(d, { withFileTypes: true })) {
        const full = path.join(d, e.name);
        if (e.isDirectory()) countNoManifest(full);
        else if (e.name !== "_MANIFEST.json") consolidated++;
      }
    }
    countNoManifest(consDir);
  }

  console.log("Archivos totales en ./output (cualquier extensión):", totalOutput);
  console.log("Archivos .js/.ts/.tsx en ./output:", srcFiles.length);
  console.log("Archivos en CODIGO_FUENTE_RECONSTRUIDO (sin manifest):", consolidated);
}

main();
