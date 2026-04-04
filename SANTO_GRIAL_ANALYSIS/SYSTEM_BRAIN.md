# SYSTEM BRAIN ANALYSIS

_Fuente: `./output` + `PROJECT_INDEX.json`. Evidencia estática; lo marcado como **hipótesis** incumple criterios estrictos de validación._

## 1. Entrypoints detectados

### entrypoint_confirmado

- **`node_modules/@opentelemetry/resources/build/src/detectors/platform/node/ProcessDetector.js`**

  - Línea 33: Uso de process.argv (CLI) — `process.argv[0],`

  - Línea 35: Uso de process.argv (CLI) — `...process.argv.slice(1),`

  - Línea 41: Uso de process.argv (CLI) — `if (process.argv.length > 1) {`

  - Línea 42: Uso de process.argv (CLI) — `attributes[semconv_1.ATTR_PROCESS_COMMAND] = process.argv[1];`

- **`node_modules/@opentelemetry/resources/build/src/platform/node/default-service-name.js`**

  - Línea 20: Uso de process.argv (CLI) — `return `unknown_service:${process.argv0}`;`

- **`node_modules/chalk/source/vendor/supports-color/index.js`**

  - Línea 6: Uso de process.argv (CLI) — `/// function hasFlag(flag, argv = globalThis.Deno?.args ?? process.argv) {`

  - Línea 7: Uso de process.argv (CLI) — `function hasFlag(flag, argv = globalThis.Deno ? globalThis.Deno.args : process.argv) {`

- **`node_modules/commander/lib/command.js`**

  - Línea 996: Uso de process.argv (CLI) — `// default to using process.argv`

  - Línea 998: Uso de process.argv (CLI) — `argv = process.argv;`

  - Línea 1044: Uso de process.argv (CLI) — `* Call with no parameters to parse `process.argv`. Detects Electron and special node options like `node --eval`. Easy mode!`

  - Línea 1052: Uso de process.argv (CLI) — `* program.parse(); // parse process.argv and auto-detect electron and special node flags`

  - Línea 1053: Uso de process.argv (CLI) — `* program.parse(process.argv); // assume argv[0] is app and argv[1] is script`

  - Línea 1056: Uso de process.argv (CLI) — `* @param {string[]} [argv] - optional, defaults to process.argv`

  - Línea 1072: Uso de process.argv (CLI) — `* Call with no parameters to parse `process.argv`. Detects Electron and special node options like `node --eval`. Easy mode!`

  - Línea 1080: Uso de process.argv (CLI) — `* await program.parseAsync(); // parse process.argv and auto-detect electron and special node flags`

  - Línea 1081: Uso de process.argv (CLI) — `* await program.parseAsync(process.argv); // assume argv[0] is app and argv[1] is script`

  - Línea 1175: Uso de process.argv (CLI) — `proc = childProcess.spawn(process.argv[0], args, { stdio: 'inherit' });`

  - Línea 2212: Uso de process.argv (CLI) — `* Set the name of the command from script filename, such as process.argv[1],`

- **`node_modules/has-flag/index.js`**

  - Línea 3: Uso de process.argv (CLI) — `module.exports = (flag, argv = process.argv) => {`

- **`src/bridge/bridgeMain.ts`**

  - Línea 120: Uso de process.argv (CLI) — `if (isInBundledMode() || !process.argv[1]) {`

  - Línea 123: Uso de process.argv (CLI) — `return [process.argv[1]]`

- **`src/bridge/sessionRunner.ts`**

  - Línea 50: Uso de process.argv (CLI) — `* the script path (process.argv[1]) for npm installs where execPath is the`

- **`src/entrypoints/cli.tsx`**

  - Línea 33: Declaración function main( — `async function main(): Promise<void> {`

  - Línea 34: Uso de process.argv (CLI) — `const args = process.argv.slice(2);`

  - Línea 72: Uso de process.argv (CLI) — `if (process.argv[2] === '--claude-in-chrome-mcp') {`

  - Línea 79: Uso de process.argv (CLI) — `} else if (process.argv[2] === '--chrome-native-host') {`

  - Línea 86: Uso de process.argv (CLI) — `} else if (feature('CHICAGO_MCP') && process.argv[2] === '--computer-use-mcp') {`

  - Línea 278: Uso de process.argv (CLI) — `process.argv = [process.argv[0]!, process.argv[1]!, 'update'];`

  - Línea 302: Patrón void main( — `void main();`

- **`src/hooks/useChromeExtensionNotification.tsx`**

  - Línea 8: Uso de process.argv (CLI) — `if (process.argv.includes('--chrome')) {`

  - Línea 11: Uso de process.argv (CLI) — `if (process.argv.includes('--no-chrome')) {`

- **`src/main.tsx`**

  - Línea 239: Uso de process.argv (CLI) — `// from process.argv leak into process.execArgv (similar to https://github.com/oven-sh/bun/issues/11673)`

  - Línea 522: Uso de process.argv (CLI) — `const cliArgs = process.argv.slice(2);`

  - Línea 585: Declaración function main( — `export async function main() {`

  - Línea 602: Uso de process.argv (CLI) — `if (process.argv.includes('-p') || process.argv.includes('--print')) {`

  - Línea 613: Uso de process.argv (CLI) — `const rawCliArgs = process.argv.slice(2);`

  - Línea 629: Uso de process.argv (CLI) — `process.argv = [process.argv[0]!, process.argv[1]!, 'open', ccUrl, ...stripped];`

  - Línea 639: Uso de process.argv (CLI) — `process.argv = [process.argv[0]!, process.argv[1]!, ...stripped];`

  - Línea 648: Uso de process.argv (CLI) — `const handleUriIdx = process.argv.indexOf('--handle-uri');`

  - Línea 649: Uso de process.argv (CLI) — `if (handleUriIdx !== -1 && process.argv[handleUriIdx + 1]) {`

  - Línea 654: Uso de process.argv (CLI) — `const uri = process.argv[handleUriIdx + 1]!;`

  - Línea 686: Uso de process.argv (CLI) — `const rawArgs = process.argv.slice(2);`

  - Línea 692: Uso de process.argv (CLI) — `process.argv = [process.argv[0]!, process.argv[1]!, ...rawArgs];`

  - Línea 696: Uso de process.argv (CLI) — `process.argv = [process.argv[0]!, process.argv[1]!, ...rawArgs];`

  - Línea 707: Uso de process.argv (CLI) — `const rawCliArgs = process.argv.slice(2);`

  - Línea 793: Uso de process.argv (CLI) — `process.argv = [process.argv[0]!, process.argv[1]!, ...rest];`

  - Línea 799: Uso de process.argv (CLI) — `const cliArgs = process.argv.slice(2);`

  - Línea 860: Uso de process.argv (CLI) — `!process.argv.includes('mcp')) {`

  - Línea 974: Uso de process.argv (CLI) — `// The actual filtering is handled in debug.ts by parsing process.argv`

  - Línea 1488: Patrón void main( — `// rejection in stream-json mode (void main() in cli.tsx).`

  - Línea 3883: Uso de process.argv (CLI) — `const isPrintMode = process.argv.includes('-p') || process.argv.includes('--print');`

  - Línea 3884: Uso de process.argv (CLI) — `const isCcUrl = process.argv.some(a => a.startsWith('cc://') || a.startsWith('cc+unix://'));`

  - Línea 3887: Uso de process.argv (CLI) — `await program.parseAsync(process.argv);`

  - Línea 4331: Uso de process.argv (CLI) — `await bridgeMain(process.argv.slice(3));`

  - Línea 4504: Uso de process.argv (CLI) — `await program.parseAsync(process.argv);`

- **`src/services/api/logging.ts`**

  - Línea 454: Uso de process.argv (CLI) — `process.argv.includes('-p') || process.argv.includes('--print')`

- **`src/tools/shared/spawnMultiAgent.ts`**

  - Línea 191: Uso de process.argv (CLI) — `* For non-native (node/bun running a script), use process.argv[1].`

  - Línea 197: Uso de process.argv (CLI) — `return isInBundledMode() ? process.execPath : process.argv[1]!`

- **`src/utils/agentSwarmsEnabled.ts`**

  - Línea 6: Uso de process.argv (CLI) — `* Checks process.argv directly to avoid import cycles with bootstrap/state.`

  - Línea 11: Uso de process.argv (CLI) — `return process.argv.includes('--agent-teams')`

- **`src/utils/cliArgs.ts`**

  - Línea 10: Uso de process.argv (CLI) — `* @param argv Optional argv array to parse (defaults to process.argv)`

  - Línea 15: Uso de process.argv (CLI) — `argv: string[] = process.argv,`

- **`src/utils/completionCache.ts`**

  - Línea 92: Uso de process.argv (CLI) — `const claudeBin = process.argv[1] || 'claude'`

  - Línea 148: Uso de process.argv (CLI) — `const claudeBin = process.argv[1] || 'claude'`

- **`src/utils/debug.ts`**

  - Línea 49: Uso de process.argv (CLI) — `process.argv.includes('--debug') ||`

  - Línea 50: Uso de process.argv (CLI) — `process.argv.includes('-d') ||`

  - Línea 53: Uso de process.argv (CLI) — `process.argv.some(arg => arg.startsWith('--debug=')) ||`

  - Línea 75: Uso de process.argv (CLI) — `const debugArg = process.argv.find(arg => arg.startsWith('--debug='))`

  - Línea 87: Uso de process.argv (CLI) — `process.argv.includes('--debug-to-stderr') || process.argv.includes('-d2e')`

  - Línea 92: Uso de process.argv (CLI) — `for (let i = 0; i < process.argv.length; i++) {`

  - Línea 93: Uso de process.argv (CLI) — `const arg = process.argv[i]!`

  - Línea 97: Uso de process.argv (CLI) — `if (arg === '--debug-file' && i + 1 < process.argv.length) {`

  - Línea 98: Uso de process.argv (CLI) — `return process.argv[i + 1]!`

- **`src/utils/desktopDeepLink.ts`**

  - Línea 19: Uso de process.argv (CLI) — `const pathsToCheck = [process.argv[1] || '', process.execPath || '']`

- **`src/utils/doctorDiagnostic.ts`**

  - Línea 74: Uso de process.argv (CLI) — `let invokedPath = process.argv[1] || ''`

  - Línea 75: Uso de process.argv (CLI) — `let execPath = process.execPath || process.argv[0] || ''`

  - Línea 185: Uso de process.argv (CLI) — `return process.argv[0] || 'unknown'`

  - Línea 199: Uso de process.argv (CLI) — `return process.argv[1] || 'unknown'`

- **`src/utils/earlyInput.ts`**

  - Línea 36: Uso de process.argv (CLI) — `process.argv.includes('-p') ||`

  - Línea 37: Uso de process.argv (CLI) — `process.argv.includes('--print')`

- **`src/utils/envUtils.ts`**

  - Línea 63: Uso de process.argv (CLI) — `process.argv.includes('--bare')`

- **`src/utils/gracefulShutdown.ts`**

  - Línea 262: Uso de process.argv (CLI) — `if (process.argv.includes('-p') || process.argv.includes('--print')) {`

- **`src/utils/localInstaller.ts`**

  - Línea 30: Uso de process.argv (CLI) — `const execPath = process.argv[1] || ''`

- **`src/utils/log.ts`**

  - Línea 155: Uso de process.argv (CLI) — `return process.argv.includes('--hard-fail')`

- **`src/utils/nativeInstaller/packageManagers.ts`**

  - Línea 63: Uso de process.argv (CLI) — `const execPath = process.execPath || process.argv[0] || ''`

  - Línea 82: Uso de process.argv (CLI) — `const execPath = process.execPath || process.argv[0] || ''`

  - Línea 112: Uso de process.argv (CLI) — `const execPath = process.execPath || process.argv[0] || ''`

  - Línea 141: Uso de process.argv (CLI) — `const execPath = process.execPath || process.argv[0] || ''`

  - Línea 179: Uso de process.argv (CLI) — `const execPath = process.execPath || process.argv[0] || ''`

  - Línea 212: Uso de process.argv (CLI) — `const execPath = process.execPath || process.argv[0] || ''`

  - Línea 245: Uso de process.argv (CLI) — `const execPath = process.execPath || process.argv[0] || ''`

  - Línea 279: Uso de process.argv (CLI) — `const execPath = process.execPath || process.argv[0] || ''`

- **`src/utils/renderOptions.ts`**

  - Línea 34: Uso de process.argv (CLI) — `if (process.argv.includes('mcp')) {`

- **`src/utils/swarm/spawnUtils.ts`**

  - Línea 27: Uso de process.argv (CLI) — `return isInBundledMode() ? process.execPath : process.argv[1]!`

- **`src/utils/warningHandler.ts`**

  - Línea 17: Uso de process.argv (CLI) — `let invokedPath = process.argv[1] || ''`

  - Línea 18: Uso de process.argv (CLI) — `let execPath = process.execPath || process.argv[0] || ''`


### entrypoint_probable (sin importadores internos)

- `node_modules/@alcalzone/ansi-tokenize/build/index.js` — ext **0** / int **6**, score **9**

- `node_modules/@ant/claude-for-chrome-mcp/src/bridgeClient.ts` — ext **3** / int **0**, score **10**

- `node_modules/@ant/claude-for-chrome-mcp/src/browserTools.ts` — ext **0** / int **0**, score **8**

- `node_modules/@ant/claude-for-chrome-mcp/src/index.ts` — ext **4** / int **0**, score **0**

- `node_modules/@ant/claude-for-chrome-mcp/src/mcpServer.ts` — ext **8** / int **0**, score **12**

- `node_modules/@ant/claude-for-chrome-mcp/src/mcpSocketClient.ts` — ext **5** / int **0**, score **10**

- `node_modules/@ant/claude-for-chrome-mcp/src/mcpSocketPool.ts` — ext **2** / int **0**, score **2**

- `node_modules/@ant/claude-for-chrome-mcp/src/toolCalls.ts` — ext **3** / int **0**, score **4**

- `node_modules/@ant/claude-for-chrome-mcp/src/types.ts` — ext **0** / int **0**, score **2**

- `node_modules/@ant/computer-use-input/js/index.js` — ext **1** / int **0**, score **0**

- `node_modules/@ant/computer-use-mcp/src/deniedApps.ts` — ext **0** / int **0**, score **4**

- `node_modules/@ant/computer-use-mcp/src/imageResize.ts` — ext **0** / int **0**, score **0**

- `node_modules/@ant/computer-use-mcp/src/index.ts` — ext **11** / int **0**, score **0**

- `node_modules/@ant/computer-use-mcp/src/keyBlocklist.ts` — ext **0** / int **0**, score **2**

- `node_modules/@ant/computer-use-mcp/src/mcpServer.ts` — ext **6** / int **0**, score **8**

- `node_modules/@ant/computer-use-mcp/src/pixelCompare.ts` — ext **2** / int **0**, score **4**

- `node_modules/@ant/computer-use-mcp/src/sentinelApps.ts` — ext **0** / int **0**, score **2**

- `node_modules/@ant/computer-use-mcp/src/toolCalls.ts` — ext **8** / int **0**, score **42**

- `node_modules/@ant/computer-use-mcp/src/tools.ts` — ext **2** / int **0**, score **6**

- `node_modules/@ant/computer-use-mcp/src/types.ts` — ext **1** / int **0**, score **2**

- `node_modules/@ant/computer-use-swift/js/index.js` — ext **1** / int **0**, score **0**

- `node_modules/@anthropic-ai/mcpb/dist/index.js` — ext **1** / int **8**, score **17**

- `node_modules/@anthropic-ai/sandbox-runtime/dist/index.js` — ext **0** / int **5**, score **13.5**

- `node_modules/@aws/lambda-invoke-store/dist-cjs/invoke-store.js` — ext **1** / int **0**, score **6**

- `node_modules/@aws-crypto/crc32/node_modules/@aws-crypto/util/build/main/index.js` — ext **0** / int **4**, score **6**

- `node_modules/@aws-crypto/crc32/node_modules/@aws-crypto/util/node_modules/@smithy/util-utf8/dist-cjs/index.js` — ext **1** / int **0**, score **0**

- `node_modules/@aws-crypto/sha256-js/build/index.js` — ext **1** / int **1**, score **1.5**

- `node_modules/@aws-crypto/sha256-js/node_modules/tslib/tslib.js` — ext **0** / int **0**, score **0**

- `node_modules/@aws-crypto/util/build/index.js` — ext **0** / int **4**, score **6**

- `node_modules/@aws-sdk/client-bedrock/dist-cjs/index.js` — ext **13** / int **2**, score **3**

- `node_modules/@aws-sdk/client-bedrock/node_modules/@smithy/protocol-http/dist-cjs/index.js` — ext **1** / int **0**, score **0**

- `node_modules/@aws-sdk/client-bedrock/node_modules/@smithy/smithy-client/dist-cjs/index.js` — ext **5** / int **0**, score **2**

- `node_modules/@aws-sdk/client-bedrock/node_modules/@smithy/types/dist-cjs/index.js` — ext **0** / int **0**, score **0**

- `node_modules/@aws-sdk/client-bedrock/node_modules/@smithy/util-base64/dist-cjs/index.js` — ext **0** / int **2**, score **3**

- `node_modules/@aws-sdk/client-bedrock/node_modules/@smithy/util-base64/node_modules/@smithy/util-buffer-from/dist-cjs/index.js` — ext **2** / int **0**, score **0**

- `node_modules/@aws-sdk/client-bedrock/node_modules/@smithy/util-base64/node_modules/@smithy/util-buffer-from/node_modules/@smithy/is-array-buffer/dist-cjs/index.js` — ext **0** / int **0**, score **0**

- `node_modules/@aws-sdk/client-bedrock-runtime/dist-cjs/index.js` — ext **16** / int **2**, score **5**

- `node_modules/@aws-sdk/client-bedrock-runtime/node_modules/@smithy/eventstream-serde-node/dist-cjs/index.js` — ext **2** / int **0**, score **0**

- `node_modules/@aws-sdk/client-bedrock-runtime/node_modules/@smithy/eventstream-serde-node/node_modules/@smithy/eventstream-serde-universal/dist-cjs/index.js` — ext **1** / int **0**, score **0**

- `node_modules/@aws-sdk/client-bedrock-runtime/node_modules/@smithy/protocol-http/dist-cjs/index.js` — ext **1** / int **0**, score **0**

- `node_modules/@aws-sdk/client-bedrock-runtime/node_modules/@smithy/smithy-client/dist-cjs/index.js` — ext **5** / int **0**, score **2**

- `node_modules/@aws-sdk/client-bedrock-runtime/node_modules/@smithy/types/dist-cjs/index.js` — ext **0** / int **0**, score **0**

- `node_modules/@aws-sdk/client-bedrock-runtime/node_modules/@smithy/util-base64/dist-cjs/index.js` — ext **0** / int **2**, score **3**

- `node_modules/@aws-sdk/client-bedrock-runtime/node_modules/@smithy/util-base64/node_modules/@smithy/util-buffer-from/dist-cjs/index.js` — ext **2** / int **0**, score **0**

- `node_modules/@aws-sdk/client-bedrock-runtime/node_modules/@smithy/util-base64/node_modules/@smithy/util-buffer-from/node_modules/@smithy/is-array-buffer/dist-cjs/index.js` — ext **0** / int **0**, score **0**

- `node_modules/@aws-sdk/client-cognito-identity/dist-cjs/index.js` — ext **13** / int **2**, score **3**

- `node_modules/@aws-sdk/client-cognito-identity/node_modules/@smithy/protocol-http/dist-cjs/index.js` — ext **1** / int **0**, score **0**

- `node_modules/@aws-sdk/client-cognito-identity/node_modules/@smithy/smithy-client/dist-cjs/index.js` — ext **5** / int **0**, score **2**

- `node_modules/@aws-sdk/client-cognito-identity/node_modules/@smithy/types/dist-cjs/index.js` — ext **0** / int **0**, score **0**

- `node_modules/@aws-sdk/client-cognito-identity/node_modules/@smithy/util-base64/dist-cjs/index.js` — ext **0** / int **2**, score **3**

- `node_modules/@aws-sdk/client-cognito-identity/node_modules/@smithy/util-base64/node_modules/@smithy/util-buffer-from/dist-cjs/index.js` — ext **2** / int **0**, score **0**

- `node_modules/@aws-sdk/client-cognito-identity/node_modules/@smithy/util-base64/node_modules/@smithy/util-buffer-from/node_modules/@smithy/is-array-buffer/dist-cjs/index.js` — ext **0** / int **0**, score **0**

- `node_modules/@aws-sdk/client-sso/dist-cjs/index.js` — ext **13** / int **2**, score **3**

- `node_modules/@aws-sdk/client-sso/node_modules/@smithy/protocol-http/dist-cjs/index.js` — ext **1** / int **0**, score **0**

- `node_modules/@aws-sdk/client-sso/node_modules/@smithy/smithy-client/dist-cjs/index.js` — ext **5** / int **0**, score **2**

- `node_modules/@aws-sdk/client-sso/node_modules/@smithy/types/dist-cjs/index.js` — ext **0** / int **0**, score **0**

- `node_modules/@aws-sdk/client-sso/node_modules/@smithy/util-base64/dist-cjs/index.js` — ext **0** / int **2**, score **3**

- `node_modules/@aws-sdk/client-sso/node_modules/@smithy/util-base64/node_modules/@smithy/util-buffer-from/dist-cjs/index.js` — ext **2** / int **0**, score **0**

- `node_modules/@aws-sdk/client-sso/node_modules/@smithy/util-base64/node_modules/@smithy/util-buffer-from/node_modules/@smithy/is-array-buffer/dist-cjs/index.js` — ext **0** / int **0**, score **0**

- `node_modules/@aws-sdk/client-sts/dist-cjs/index.js` — ext **5** / int **2**, score **3**

- `node_modules/@aws-sdk/client-sts/node_modules/@smithy/protocol-http/dist-cjs/index.js` — ext **1** / int **0**, score **0**

- `node_modules/@aws-sdk/client-sts/node_modules/@smithy/smithy-client/dist-cjs/index.js` — ext **5** / int **0**, score **2**

- `node_modules/@aws-sdk/client-sts/node_modules/@smithy/types/dist-cjs/index.js` — ext **0** / int **0**, score **0**

- `node_modules/@aws-sdk/client-sts/node_modules/@smithy/util-base64/dist-cjs/index.js` — ext **0** / int **2**, score **3**

- `node_modules/@aws-sdk/client-sts/node_modules/@smithy/util-base64/node_modules/@smithy/util-buffer-from/dist-cjs/index.js` — ext **2** / int **0**, score **0**

- `node_modules/@aws-sdk/client-sts/node_modules/@smithy/util-base64/node_modules/@smithy/util-buffer-from/node_modules/@smithy/is-array-buffer/dist-cjs/index.js` — ext **0** / int **0**, score **0**

- `node_modules/@aws-sdk/core/dist-cjs/index.js` — ext **13** / int **0**, score **0**

- `node_modules/@aws-sdk/core/dist-cjs/submodules/client/index.js` — ext **0** / int **0**, score **0**

- `node_modules/@aws-sdk/core/dist-cjs/submodules/httpAuthSchemes/index.js` — ext **5** / int **0**, score **0**

- `node_modules/@aws-sdk/core/dist-cjs/submodules/protocols/index.js` — ext **8** / int **0**, score **0**

- `node_modules/@aws-sdk/core/node_modules/@smithy/protocol-http/dist-cjs/index.js` — ext **1** / int **0**, score **0**

- `node_modules/@aws-sdk/core/node_modules/@smithy/signature-v4/dist-cjs/index.js` — ext **6** / int **0**, score **0**

- `node_modules/@aws-sdk/core/node_modules/@smithy/signature-v4/node_modules/@smithy/is-array-buffer/dist-cjs/index.js` — ext **0** / int **0**, score **0**

- `node_modules/@aws-sdk/core/node_modules/@smithy/signature-v4/node_modules/@smithy/util-hex-encoding/dist-cjs/index.js` — ext **0** / int **0**, score **0**

- `node_modules/@aws-sdk/core/node_modules/@smithy/signature-v4/node_modules/@smithy/util-uri-escape/dist-cjs/index.js` — ext **0** / int **0**, score **0**

- `node_modules/@aws-sdk/core/node_modules/@smithy/smithy-client/dist-cjs/index.js` — ext **5** / int **0**, score **2**

- `node_modules/@aws-sdk/core/node_modules/@smithy/types/dist-cjs/index.js` — ext **0** / int **0**, score **0**

- `node_modules/@aws-sdk/core/node_modules/@smithy/util-base64/dist-cjs/index.js` — ext **0** / int **2**, score **3**

- `node_modules/@aws-sdk/core/node_modules/@smithy/util-base64/node_modules/@smithy/util-buffer-from/dist-cjs/index.js` — ext **2** / int **0**, score **0**

- `node_modules/@aws-sdk/core/node_modules/@smithy/util-base64/node_modules/@smithy/util-buffer-from/node_modules/@smithy/is-array-buffer/dist-cjs/index.js` — ext **0** / int **0**, score **0**


## 2. Ranking por `weight_score` (top 25)

Fórmula (ver `index-project.js`): `imported_by×2 + internal×1.5 + calls×2 + imports_to_tools×3 + imports_to_policy×3 + keywords(plan/execute/tool/validate)×2`.


1. `src/main.tsx` — **score 1426** (supporting_module) | →tools 0 →policy 0 | calls 500 —

2. `src/screens/REPL.tsx` — **score 1320** (supporting_module) | →tools 0 →policy 0 | calls 500 —

3. `src/components/PromptInput/PromptInput.tsx` — **score 602** (supporting_module) | →tools 0 →policy 0 | calls 298 —

4. `src/cli/print.ts` — **score 590** (supporting_module) | →tools 0 →policy 0 | calls 291 —

5. `src/utils/plugins/pluginLoader.ts` — **score 508** (supporting_module) | →tools 0 →policy 0 | calls 253 —

6. `src/components/Settings/Config.tsx` — **score 414** (supporting_module) | →tools 0 →policy 0 | calls 205 —

7. `src/bridge/bridgeMain.ts` — **score 388** (supporting_module) | →tools 0 →policy 0 | calls 192 —

8. `src/services/mcp/client.ts` — **score 376** (supporting_module) | →tools 0 →policy 0 | calls 186 —

9. `src/services/mcp/auth.ts` — **score 372** (supporting_module) | →tools 0 →policy 0 | calls 185 —

10. `node_modules/highlight.js/lib/index.js` — **score 354** (supporting_module) | →tools 16 →policy 6 | calls 0 —

11. `src/utils/hooks.ts` — **score 354** (supporting_module) | →tools 0 →policy 0 | calls 174 —

12. `src/utils/attachments.ts` — **score 330** (supporting_module) | →tools 0 →policy 0 | calls 161 —

13. `src/utils/teleport.tsx` — **score 322** (supporting_module) | →tools 0 →policy 0 | calls 160 —

14. `src/tools/AgentTool/AgentTool.tsx` — **score 318** (supporting_module) | →tools 0 →policy 0 | calls 157 —

15. `src/utils/plugins/marketplaceManager.ts` — **score 298** (supporting_module) | →tools 0 →policy 0 | calls 148 —

16. `src/utils/nativeInstaller/installer.ts` — **score 280** (supporting_module) | →tools 0 →policy 0 | calls 139 —

17. `src/bridge/replBridge.ts` — **score 274** (supporting_module) | →tools 0 →policy 0 | calls 136 —

18. `node_modules/zod/v3/types.js` — **score 273.5** (supporting_module) | →tools 0 →policy 0 | calls 131 —

19. `src/entrypoints/sdk/coreSchemas.ts` — **score 266** (supporting_module) | →tools 0 →policy 0 | calls 131 —

20. `src/commands/plugin/ManagePlugins.tsx` — **score 260** (supporting_module) | →tools 0 →policy 0 | calls 128 —

21. `src/services/api/claude.ts` — **score 248** (supporting_module) | →tools 0 →policy 0 | calls 123 —

22. `src/commands/insights.ts` — **score 242** (supporting_module) | →tools 0 →policy 0 | calls 120 —

23. `src/utils/sessionStorage.ts` — **score 240** (supporting_module) | →tools 0 →policy 0 | calls 117 —

24. `src/utils/config.ts` — **score 234** (supporting_module) | →tools 0 →policy 0 | calls 115 —

25. `src/utils/worktree.ts` — **score 230** (supporting_module) | →tools 0 →policy 0 | calls 113 —


### core_module (umbral importadores)

- `node_modules/zod/v4/core/util.js` — 46 importadores

- `node_modules/node-forge/lib/forge.js` — 39 importadores

- `node_modules/ajv/dist/compile/codegen/index.js` — 36 importadores

- `node_modules/undici/lib/core/util.js` — 36 importadores

- `node_modules/@grpc/grpc-js/build/src/constants.js` — 35 importadores

- `node_modules/yaml/dist/nodes/identity.js` — 33 importadores

- `node_modules/node-forge/lib/util.js` — 32 importadores

- `node_modules/ajv/dist/compile/util.js` — 31 importadores

- `node_modules/undici/lib/core/errors.js` — 30 importadores

- `node_modules/@azure/identity/dist/esm/util/logging.js` — 27 importadores

- `node_modules/@grpc/grpc-js/build/src/logging.js` — 25 importadores

- `node_modules/axios/lib/utils.js` — 25 importadores

- `node_modules/undici/lib/core/symbols.js` — 23 importadores

- `node_modules/@mixmark-io/domino/lib/utils.js` — 21 importadores

- `node_modules/xmlbuilder/lib/NodeType.js` — 20 importadores

- `node_modules/yaml/dist/nodes/Scalar.js` — 19 importadores

- `node_modules/zod-to-json-schema/dist/esm/parseDef.js` — 19 importadores

- `node_modules/@azure/identity/dist/esm/errors.js` — 18 importadores

- `node_modules/@grpc/grpc-js/build/src/metadata.js` — 17 importadores

- `node_modules/protobufjs/src/util.js` — 17 importadores

- `node_modules/@azure/identity/dist/esm/util/tenantIdUtils.js` — 16 importadores

- `node_modules/@azure/identity/dist/esm/util/tracing.js` — 16 importadores

- `node_modules/@mixmark-io/domino/lib/Node.js` — 16 importadores

- `node_modules/undici/lib/web/fetch/webidl.js` — 16 importadores


### supporting_module (muestra)

- `node_modules/@alcalzone/ansi-tokenize/build/ansiCodes.js` — score 8

- `node_modules/@alcalzone/ansi-tokenize/build/diff.js` — score 7.5

- `node_modules/@alcalzone/ansi-tokenize/build/index.js` — score 9

- `node_modules/@alcalzone/ansi-tokenize/build/reduce.js` — score 7.5

- `node_modules/@alcalzone/ansi-tokenize/build/styledChars.js` — score 18.5

- `node_modules/@alcalzone/ansi-tokenize/build/tokenize.js` — score 9.5

- `node_modules/@alcalzone/ansi-tokenize/build/undo.js` — score 7.5

- `node_modules/@ant/claude-for-chrome-mcp/src/bridgeClient.ts` — score 10

- `node_modules/@ant/claude-for-chrome-mcp/src/browserTools.ts` — score 8

- `node_modules/@ant/claude-for-chrome-mcp/src/index.ts` — score 0

- `node_modules/@ant/claude-for-chrome-mcp/src/mcpServer.ts` — score 12

- `node_modules/@ant/claude-for-chrome-mcp/src/mcpSocketClient.ts` — score 10

- `node_modules/@ant/claude-for-chrome-mcp/src/mcpSocketPool.ts` — score 2

- `node_modules/@ant/claude-for-chrome-mcp/src/toolCalls.ts` — score 4

- `node_modules/@ant/claude-for-chrome-mcp/src/types.ts` — score 2

- `node_modules/@ant/computer-use-input/js/index.js` — score 0

- `node_modules/@ant/computer-use-mcp/src/deniedApps.ts` — score 4

- `node_modules/@ant/computer-use-mcp/src/imageResize.ts` — score 0

- `node_modules/@ant/computer-use-mcp/src/index.ts` — score 0

- `node_modules/@ant/computer-use-mcp/src/keyBlocklist.ts` — score 2

- `node_modules/@ant/computer-use-mcp/src/mcpServer.ts` — score 8

- `node_modules/@ant/computer-use-mcp/src/pixelCompare.ts` — score 4

- `node_modules/@ant/computer-use-mcp/src/sentinelApps.ts` — score 2

- `node_modules/@ant/computer-use-mcp/src/toolCalls.ts` — score 42

- `node_modules/@ant/computer-use-mcp/src/tools.ts` — score 6

- `node_modules/@ant/computer-use-mcp/src/types.ts` — score 2

- `node_modules/@ant/computer-use-swift/js/index.js` — score 0

- `node_modules/@anthropic-ai/mcpb/dist/cli/init.js` — score 147.5

- `node_modules/@anthropic-ai/mcpb/dist/cli/pack.js` — score 57.5

- `node_modules/@anthropic-ai/mcpb/dist/cli/unpack.js` — score 41

- `node_modules/@anthropic-ai/mcpb/dist/index.js` — score 17

- `node_modules/@anthropic-ai/mcpb/dist/node/files.js` — score 36

- `node_modules/@anthropic-ai/mcpb/dist/node/sign.js` — score 38

- `node_modules/@anthropic-ai/mcpb/dist/node/validate.js` — score 52

- `node_modules/@anthropic-ai/mcpb/dist/schemas-loose.js` — score 2


## 3. SYSTEM_BRAIN

### Estado: **HIPÓTESIS** (ningún archivo pasó validación estricta)


Ningún fichero cumple simultáneamente: `imports_to_tools ≥ 1`, llamadas `run`/`execute`/`handle`/`dispatch` en `calls_detected`, y `has_flow_keywords`. Se muestra el mayor `weight_score` como candidato débil.


**Motivos de rechazo (criterio global):**

- No importa (resuelto) ningún módulo categorizado como `tools` (imports_to_tools === 0).



**Archivo:** `src/main.tsx`


- **weight_score:** 1426
- **imported_by:** 0
- **internal_imports:** 0
- **external_imports:** 215
- **imports_to_tools / agents / policy / prompts:** 0 / 0 / 0 / 0
- **calls_detected (muestra):** 12 de 500


**Imports internos (muestra):**


**Paquetes externos (muestra):**

- `./Tool.js`

- `./assistant/gate.js`

- `./assistant/index.js`

- `./assistant/sessionDiscovery.js`

- `./bootstrap/state.js`

- `./bridge/bridgeEnabled.js`

- `./bridge/bridgeMain.js`

- `./bridge/trustedDevice.js`

- `./cli/handlers/agents.js`

- `./cli/handlers/ant.js`

- `./cli/handlers/auth.js`

- `./cli/handlers/autoMode.js`

- `./cli/handlers/mcp.js`

- `./cli/handlers/plugins.js`

- `./cli/handlers/util.js`

- `./commands.js`

- `./commands/clear/caches.js`

- `./components/TeleportProgress.js`

- `./components/agents/SnapshotUpdateDialog.js`

- `./constants/oauth.js`


**Evidencia: `calls_detected` (hasta 20)**


```text
L12: [call:profileCheckpoint(] profileCheckpoint('main_tsx_entry');
L16: [call:startMdmRawRead(] startMdmRawRead();
L20: [call:startKeychainPrefetch(] startKeychainPrefetch();
L76: [call:feature(] const coordinatorModeModule = feature('COORDINATOR_MODE') ? require('./coordinator/coordinatorMode.js') as typeof import('./coordinator/coordinatorMode.js') : null;
L80: [call:feature(] const assistantModule = feature('KAIROS') ? require('./assistant/index.js') as typeof import('./assistant/index.js') : null;
L81: [call:feature(] const kairosGate = feature('KAIROS') ? require('./assistant/gate.js') as typeof import('./assistant/gate.js') : null;
L171: [call:feature(] const autoModeStateModule = feature('TRANSCRIPT_CLASSIFIER') ? require('./utils/permissions/autoModeState.js') as typeof import('./utils/permissions/autoModeState.js') : null;
L209: [call:profileCheckpoint(] profileCheckpoint('main_tsx_imports_loaded');
L213: [call:init(] * This is called after init() completes to ensure settings are loaded
L218: [call:getSettingsForSource(] const policySettings = getSettingsForSource('policySettings');
L220: [call:getManagedSettingsKeysForLogging(] const allKeys = getManagedSettingsKeysForLogging(policySettings);
L221: [call:logEvent(] logEvent('tengu_managed_settings_loaded', {
L233: [call:isRunningWithBun(] const isBun = isRunningWithBun();
L280: [call:getDefaultMainLoopModel(] const model = parseUserSpecifiedModel(getInitialMainLoopModel() ?? getDefaultMainLoopModel());
L280: [call:parseUserSpecifiedModel(] const model = parseUserSpecifiedModel(getInitialMainLoopModel() ?? getDefaultMainLoopModel());
L280: [call:getInitialMainLoopModel(] const model = parseUserSpecifiedModel(getInitialMainLoopModel() ?? getDefaultMainLoopModel());
L281: [call:getContextWindowForModel(] void logSkillsLoaded(getCwd(), getContextWindowForModel(model, getSdkBetas()));
L281: [call:logSkillsLoaded(] void logSkillsLoaded(getCwd(), getContextWindowForModel(model, getSdkBetas()));
L281: [call:getCwd(] void logSkillsLoaded(getCwd(), getContextWindowForModel(model, getSdkBetas()));
L281: [call:getSdkBetas(] void logSkillsLoaded(getCwd(), getContextWindowForModel(model, getSdkBetas()));
```


**Evidencia: fragmentos con vocabulario de loop**

Líneas 42-46:

```ts
import { isPolicyAllowed, loadPolicyLimits, refreshPolicyLimits, waitForPolicyLimitsToLoad } from './services/policyLimits/index.js';
import { loadRemoteManagedSettings, refreshRemoteManagedSettings } from './services/remoteManagedSettings/index.js';
import type { ToolInputJSONSchema } from './Tool.js';
import { createSyntheticOutputTool, isSyntheticOutputToolEnabled } from './tools/SyntheticOutputTool/SyntheticOutputTool.js';
import { getTools } from './tools.js';
```

Líneas 102-106:

```ts
import type { Message as MessageType } from './types/message.js';
import { assertMinVersion } from './utils/autoUpdater.js';
import { CLAUDE_IN_CHROME_SKILL_HINT, CLAUDE_IN_CHROME_SKILL_HINT_WITH_WEBBROWSER } from './utils/claudeInChrome/prompt.js';
import { setupClaudeInChrome, shouldAutoEnableClaudeInChrome, shouldEnableClaudeInChrome } from './utils/claudeInChrome/setup.js';
import { getContextWindowForModel } from './utils/context.js';
```

Líneas 354-358:

```ts
/**
 * Prefetch system context (including git status) only when it's safe to do so.
 * Git commands can execute arbitrary code via hooks and config (e.g., core.fsmonitor,
 * diff.external), so we must only run them after trust is established or in
 * non-interactive mode where trust is implicit.
```

Líneas 436-440:

```ts
    let settingsPath: string;
    if (looksLikeJson) {
      // It's a JSON string - validate and create temp file
      const parsedJson = safeParseJSON(trimmedSettings);
      if (!parsedJson) {
```

Líneas 445-449:

```ts
      // Create a temporary file and write the JSON to it.
      // Use a content-hash-based path instead of random UUID to avoid
      // busting the Anthropic API prompt cache. The settings path ends up
      // in the Bash tool's sandbox denyWithinAllow list, which is part of
      // the tool description sent to the API. A random UUID per subprocess
```

Líneas 446-450:

```ts
      // Use a content-hash-based path instead of random UUID to avoid
      // busting the Anthropic API prompt cache. The settings path ends up
      // in the Bash tool's sandbox denyWithinAllow list, which is part of
      // the tool description sent to the API. A random UUID per subprocess
      // changes the tool description on every query() call, invalidating
```

Líneas 447-451:

```ts
      // busting the Anthropic API prompt cache. The settings path ends up
      // in the Bash tool's sandbox denyWithinAllow list, which is part of
      // the tool description sent to the API. A random UUID per subprocess
      // changes the tool description on every query() call, invalidating
      // the cache prefix and causing a 12x input token cost penalty.
```

Líneas 448-452:

```ts
      // in the Bash tool's sandbox denyWithinAllow list, which is part of
      // the tool description sent to the API. A random UUID per subprocess
      // changes the tool description on every query() call, invalidating
      // the cache prefix and causing a 12x input token cost penalty.
      // The content hash ensures identical settings produce the same path
```

Líneas 457-461:

```ts
      writeFileSync_DEPRECATED(settingsPath, trimmedSettings, 'utf8');
    } else {
      // It's a file path - resolve and validate by attempting to read
      const {
        resolvedPath: resolvedSettingsPath
```

Líneas 855-859:

```ts
  profileCheckpoint('main_after_run');
}
async function getInputPrompt(prompt: string, inputFormat: 'text' | 'stream-json'): Promise<string | AsyncIterable<string>> {
  if (!process.stdin.isTTY &&
  // Input hijacking breaks MCP.
```


## 4. Flujo reconstruido (llamadas, no solo imports)

_Ordén **no** inferido del runtime. Secuencia sugerida solo porque aparecen patrones de llamada en el código indexado._


```text
L12: [call:profileCheckpoint(] profileCheckpoint('main_tsx_entry');
L16: [call:startMdmRawRead(] startMdmRawRead();
L20: [call:startKeychainPrefetch(] startKeychainPrefetch();
L76: [call:feature(] const coordinatorModeModule = feature('COORDINATOR_MODE') ? require('./coordinator/coordinatorMode.js') as typeof import('./coordinator/coordinatorMode.js') : null;
L80: [call:feature(] const assistantModule = feature('KAIROS') ? require('./assistant/index.js') as typeof import('./assistant/index.js') : null;
L81: [call:feature(] const kairosGate = feature('KAIROS') ? require('./assistant/gate.js') as typeof import('./assistant/gate.js') : null;
L171: [call:feature(] const autoModeStateModule = feature('TRANSCRIPT_CLASSIFIER') ? require('./utils/permissions/autoModeState.js') as typeof import('./utils/permissions/autoModeState.js') : null;
L209: [call:profileCheckpoint(] profileCheckpoint('main_tsx_imports_loaded');
L213: [call:init(] * This is called after init() completes to ensure settings are loaded
L218: [call:getSettingsForSource(] const policySettings = getSettingsForSource('policySettings');
L220: [call:getManagedSettingsKeysForLogging(] const allKeys = getManagedSettingsKeysForLogging(policySettings);
L221: [call:logEvent(] logEvent('tengu_managed_settings_loaded', {
L233: [call:isRunningWithBun(] const isBun = isRunningWithBun();
L280: [call:getDefaultMainLoopModel(] const model = parseUserSpecifiedModel(getInitialMainLoopModel() ?? getDefaultMainLoopModel());
L280: [call:parseUserSpecifiedModel(] const model = parseUserSpecifiedModel(getInitialMainLoopModel() ?? getDefaultMainLoopModel());
```


## 5. Cadena conceptual (imports por categoría)

```text
prompts → agents → tools (imports_to_*) → policy / externos (framework)
```


## 6. Limitaciones

- Análisis estático: sin CFG ni TypeScript real.
- Imports dinámicos con variables no resueltos.
- `call:foo(` puede ser falso positivo si `foo` no es el mismo binding.
