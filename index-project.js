/**
 * Indexa ./output: imports internos/externos, llamadas, pesos y grafo.
 * Genera: PROJECT_INDEX.json, PROJECT_TREE.md, DEPENDENCY_GRAPH.md
 * Uso: node index-project.js
 */
"use strict";

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const OUTPUT_ROOT = path.resolve(__dirname, "output");
const JSON_OUT = path.join(__dirname, "PROJECT_INDEX.json");
const TREE_OUT = path.join(__dirname, "PROJECT_TREE.md");
const GRAPH_OUT = path.join(__dirname, "DEPENDENCY_GRAPH.md");

const EXT_OK = new Set([".js", ".ts", ".tsx"]);

/** Keywords de flujo para SYSTEM_BRAIN (presencia en texto) */
const FLOW_KEYWORD_RE =
  /\bplan\b|\bplanner\b|\btool\b|\bvalidate\b|\bvalidator\b/i;

/** Bonificación de score (+2 c/u si aparece) */
const SCORE_KEYWORD_RES = [
  [/\bplan\b/i, "plan"],
  [/\bexecute\b/i, "execute"],
  [/\btool\b/i, "tool"],
  [/\bvalidate\b/i, "validate"],
];

const CALL_GENERIC_RES = [
  [/\brun\s*\(/i, "run("],
  [/\bexecute\s*\(/i, "execute("],
  [/\bhandle\s*\(/i, "handle("],
  [/\bdispatch\s*\(/i, "dispatch("],
];

function isInsideRoot(candidate, root) {
  const rel = path.relative(path.resolve(root), path.resolve(candidate));
  return rel === "" || (!rel.startsWith("..") && !path.isAbsolute(rel));
}

function walkFiles(dir, acc) {
  let entries;
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return;
  }
  for (const e of entries) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) walkFiles(full, acc);
    else if (e.isFile()) acc.push(full);
  }
}

function relPosix(fromRootAbs) {
  return path.relative(OUTPUT_ROOT, fromRootAbs).split(path.sep).join("/");
}

function categorize(content) {
  const text = String(content);

  const rules = [
    ["prompts", /prompt|system_prompt|\bsystem\b/i],
    [
      "tools",
      /\btool\b|\bexecute\b|\bcommand\b|child_process|execSync|spawn/i,
    ],
    ["agents", /\bagent\b|\bplanner\b|\bexecutor\b/i],
    ["policy", /\bpolicy\b|\bconstraint\b|\bsecurity\b/i],
    ["cli/ui", /\bink\b|\breact\b|\bcli\b/i],
  ];

  for (const [cat, re] of rules) {
    if (re.test(text)) return cat;
  }
  return "otros";
}

function tryResolveInternal(fromAbs, specifier) {
  const spec = String(specifier).trim();
  if (!spec.startsWith(".") && !spec.startsWith("/")) return null;
  const clean = spec.startsWith("/") ? spec.slice(1) : spec;
  const base = path.resolve(path.dirname(fromAbs), clean);

  const candidates = [
    base,
    base + ".ts",
    base + ".tsx",
    base + ".js",
    path.join(base, "index.ts"),
    path.join(base, "index.tsx"),
    path.join(base, "index.js"),
  ];

  for (const cand of candidates) {
    const norm = path.normalize(cand);
    if (!isInsideRoot(norm, OUTPUT_ROOT)) continue;
    try {
      const st = fs.statSync(norm);
      if (st.isFile()) return relPosix(norm);
    } catch {
      /* omitir */
    }
  }
  return null;
}

function extractImportsSplit(content, fromAbs) {
  const internal = new Set();
  const external = new Set();
  const patterns = [
    /(?:import|export)\s+[^'";]*?from\s+['"]([^'"]+)['"]/g,
    /import\s+['"]([^'"]+)['"]\s*;/g,
    /export\s+[^'";]*?from\s+['"]([^'"]+)['"]/g,
    /require\s*\(\s*['"]([^'"]+)['"]\s*\)/g,
    /import\s*\(\s*['"]([^'"]+)['"]\s*\)/g,
  ];

  for (const re of patterns) {
    re.lastIndex = 0;
    let m;
    while ((m = re.exec(content)) !== null) {
      const spec = m[1];
      const resolved = tryResolveInternal(fromAbs, spec);
      if (resolved) internal.add(resolved);
      else external.add(spec);
    }
  }
  return { internal: [...internal], external: [...external] };
}

/** Identificadores importados (heurística por líneas import) */
function extractImportedIdentifiers(content) {
  const ids = new Set();
  const lines = content.split(/\r?\n/);
  for (const line of lines) {
    const t = line.trim();
    if (!t.startsWith("import") && !t.startsWith("export")) continue;
    if (/\bfrom\s+['"]/.test(t) && /\bexport\s+\{/.test(t)) continue;

    let m = t.match(
      /^\s*import\s+(?:type\s+)?([A-Za-z_$][\w$]*)\s+from\s+['"]/
    );
    if (m) {
      ids.add(m[1]);
      continue;
    }
    m = t.match(/^\s*import\s+\*\s+as\s+([A-Za-z_$][\w$]*)\s+from\s+['"]/);
    if (m) {
      ids.add(m[1]);
      continue;
    }
    m = t.match(/^\s*import\s+(?:type\s+)?\{([^}]+)\}\s+from\s+['"]/);
    if (m) {
      for (const part of m[1].split(",")) {
        const p = part.trim();
        if (!p) continue;
        const asM = p.match(/^(\w+)\s+as\s+(\w+)$/);
        if (asM) ids.add(asM[2]);
        else if (/^[A-Za-z_$][\w$]*$/.test(p)) ids.add(p);
      }
    }
  }
  return ids;
}

function detectCalls(content) {
  const lines = content.split(/\r?\n/);
  const seen = new Set();
  const out = [];

  const push = (lineNum, snippet, kind) => {
    const key = `${lineNum}:${kind}:${snippet.slice(0, 120)}`;
    if (seen.has(key)) return;
    seen.add(key);
    out.push(`L${lineNum}: [${kind}] ${snippet.trim()}`);
  };

  const importedIds = extractImportedIdentifiers(content);

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const n = i + 1;

    for (const [re, label] of CALL_GENERIC_RES) {
      re.lastIndex = 0;
      if (re.test(line)) push(n, line, label.replace(/\s*\(.*$/, "("));
    }

    for (const id of importedIds) {
      const re = new RegExp(`\\b${id}\\s*\\(`);
      if (re.test(line)) push(n, line, `call:${id}(`);
    }
  }

  return out;
}

function hasFlowKeywords(content) {
  return FLOW_KEYWORD_RE.test(content);
}

function keywordBonusScore(content) {
  let b = 0;
  for (const [re] of SCORE_KEYWORD_RES) {
    re.lastIndex = 0;
    if (re.test(content)) b += 2;
  }
  return b;
}

function computeWeightScore(f) {
  const ib = f.imported_by.length;
  const ni = f.internal_imports.length;
  const nc = f.calls_detected_total ?? f.calls_detected.length;
  const kw = f.keyword_bonus_score;
  return (
    ib * 2 +
    ni * 1.5 +
    nc * 2 +
    (f.imports_to_tools || 0) * 3 +
    (f.imports_to_policy || 0) * 3 +
    kw
  );
}

function buildTreeLines(relPaths) {
  const root = { __type: "dir", children: new Map() };
  for (const rp of relPaths.sort()) {
    const parts = rp.split("/");
    let node = root;
    for (let i = 0; i < parts.length; i++) {
      const p = parts[i];
      const isLast = i === parts.length - 1;
      if (!node.children.has(p)) {
        node.children.set(p, {
          __type: isLast ? "file" : "dir",
          children: isLast ? null : new Map(),
        });
      }
      const next = node.children.get(p);
      if (!isLast) node = next;
    }
  }

  const lines = ["# Árbol del proyecto (`./output`)", "", "```"];
  function emit(node, prefix) {
    const entries = [...node.children.entries()].sort((a, b) => {
      const ad = a[1].__type === "dir" ? 0 : 1;
      const bd = b[1].__type === "dir" ? 0 : 1;
      if (ad !== bd) return ad - bd;
      return a[0].localeCompare(b[0]);
    });
    entries.forEach(([name, child], i) => {
      const last = i === entries.length - 1;
      const branch = last ? "└── " : "├── ";
      const nextPrefix = prefix + (last ? "    " : "│   ");
      lines.push(prefix + branch + name + (child.__type === "dir" ? "/" : ""));
      if (child.__type === "dir") emit(child, nextPrefix);
    });
  }
  emit(root, "");
  lines.push("```");
  return lines.join("\n");
}

function main() {
  if (!fs.existsSync(OUTPUT_ROOT)) {
    console.error("No existe ./output. Ejecuta extract.js antes.");
    process.exit(1);
  }

  const absFiles = [];
  walkFiles(OUTPUT_ROOT, absFiles);
  const targets = absFiles.filter((a) =>
    EXT_OK.has(path.extname(a).toLowerCase())
  );

  const pathSet = new Set(targets.map(relPosix));

  const files = [];

  for (const abs of targets) {
    const rp = relPosix(abs);
    let buf;
    try {
      buf = fs.readFileSync(abs);
    } catch (e) {
      console.error("No se pudo leer:", rp, e.message);
      continue;
    }

    const hash = crypto.createHash("sha256").update(buf).digest("hex");
    const content = buf.toString("utf-8");
    const category = categorize(content);
    const { internal, external } = extractImportsSplit(content, abs);
    const calls_all = detectCalls(content);
    const calls_detected_total = calls_all.length;
    const calls_detected = calls_all.slice(0, 500);
    const has_orchestration_call = calls_all.some((s) =>
      /\[run\(|\[execute\(|\[handle\(|\[dispatch\(/.test(s)
    );
    const has_flow_keywords = hasFlowKeywords(content);
    const keyword_bonus_score = keywordBonusScore(content);

    const imports = [
      ...internal.sort(),
      ...external.sort().map((e) => `external:${e}`),
    ];

    files.push({
      path: rp,
      size: buf.length,
      extension: path.extname(abs).replace(/^\./, ""),
      hash,
      category,
      imports,
      internal_imports: internal.sort(),
      external_imports: external.sort(),
      internal_imports_count: internal.length,
      external_imports_count: external.length,
      imports_to_tools: 0,
      imports_to_agents: 0,
      imports_to_policy: 0,
      imports_to_prompts: 0,
      calls_detected,
      calls_detected_total,
      has_orchestration_call,
      has_flow_keywords,
      keyword_bonus_score,
      imported_by: [],
      weight_score: 0,
    });
  }

  const byPath = new Map(files.map((f) => [f.path, f]));

  for (const f of files) {
    for (const imp of f.internal_imports) {
      if (!pathSet.has(imp)) continue;
      const target = byPath.get(imp);
      if (target && !target.imported_by.includes(f.path)) {
        target.imported_by.push(f.path);
      }
    }
  }

  const catMap = {
    tools: "imports_to_tools",
    agents: "imports_to_agents",
    policy: "imports_to_policy",
    prompts: "imports_to_prompts",
  };

  for (const f of files) {
    for (const imp of f.internal_imports) {
      const t = byPath.get(imp);
      if (!t) continue;
      const key = catMap[t.category];
      if (key) f[key] += 1;
    }
  }

  for (const f of files) {
    f.imported_by.sort();
    f.weight_score = Math.round(computeWeightScore(f) * 100) / 100;
  }

  const payload = { files };

  fs.writeFileSync(JSON_OUT, JSON.stringify(payload, null, 2), "utf-8");

  const relPaths = files.map((f) => f.path);
  fs.writeFileSync(TREE_OUT, buildTreeLines(relPaths), "utf-8");

  const internalImportsOnly = (f) => f.internal_imports.filter((i) => pathSet.has(i));

  const rankedByImports = [...files].sort(
    (a, b) => b.imported_by.length - a.imported_by.length
  );
  const rankedByWeight = [...files].sort((a, b) => b.weight_score - a.weight_score);

  const topN = rankedByImports.slice(0, 25);
  const zeroIn = files.filter((f) => f.imported_by.length === 0);

  const extCounts = new Map();
  for (const f of files) {
    for (const e of f.external_imports) {
      extCounts.set(e, (extCounts.get(e) || 0) + 1);
    }
  }
  const topExt = [...extCounts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 30);

  const chains = [];
  for (let i = 0; i < Math.min(15, rankedByWeight.length); i++) {
    const start = rankedByWeight[i];
    const chain = [start.path];
    const firstImports = internalImportsOnly(start);
    if (firstImports.length > 0) {
      chain.push(firstImports[0]);
      const second = byPath.get(firstImports[0]);
      if (second) {
        const nxt = internalImportsOnly(second);
        if (nxt.length > 0) chain.push(nxt[0]);
      }
    }
    if (chain.length >= 2) chains.push(chain.join(" → "));
  }

  const graphMd = [
    "# Grafo de dependencias (`./output`)",
    "",
    "## Resumen: lógica propia vs externos",
    "",
    `- **Imports internos** ( aristas resueltas en \`./output\`): se usan para \`imported_by\`, cadena de dependencias y peso hacia categorías (\`imports_to_*\`).`,
    "- **Imports externos** (paquetes / URLs): listados en \`external_imports\`; no enlazan a archivos del mapa.",
    "",
    "### Paquetes externos más referenciados (top 30)",
    "",
    ...topExt.map(([pkg, c], i) => `${i + 1}. \`${pkg}\` — ${c} archivos`),
    "",
    "## Archivos más referenciados internamente (top 25)",
    "",
    ...topN.map(
      (f, i) =>
        `${i + 1}. \`${f.path}\` — ${f.imported_by.length} importadores, \`weight_score\` **${f.weight_score}**, categoría \`${f.category}\``
    ),
    "",
    "## Posibles entrypoints (sin importadores internos)",
    "",
    ...zeroIn.map(
      (f) =>
        `- \`${f.path}\` (${f.size} b, ${f.category}, ext:${f.external_imports_count}, int:${f.internal_imports_count})`
    ),
    "",
    "## Cadenas ejemplo (desde hubs por score)",
    "",
    chains.length
      ? chains.map((c) => `- ${c}`).join("\n")
      : "_Sin suficientes enlaces internos resueltos._",
    "",
    "## Notas",
    "",
    "- `calls_detected`: heurística estática (\`run\`/\`execute\`/\`handle\`/\`dispatch\` y llamadas \`identificador(\` para bindings de \`import\`).",
    "- `weight_score`: ver fórmula en \`index-project.js\`.",
  ].join("\n");

  fs.writeFileSync(GRAPH_OUT, graphMd, "utf-8");

  console.log("Archivos indexados:", files.length);
  console.log("Escrito:", JSON_OUT);
  console.log("Escrito:", TREE_OUT);
  console.log("Escrito:", GRAPH_OUT);
}

main();
