# Árbol del proyecto (`./output`)

```
├── node_modules/
│   ├── @alcalzone/
│   │   └── ansi-tokenize/
│   │       └── build/
│   │           ├── ansiCodes.js
│   │           ├── diff.js
│   │           ├── index.js
│   │           ├── reduce.js
│   │           ├── styledChars.js
│   │           ├── tokenize.js
│   │           └── undo.js
│   ├── @ant/
│   │   ├── claude-for-chrome-mcp/
│   │   │   └── src/
│   │   │       ├── bridgeClient.ts
│   │   │       ├── browserTools.ts
│   │   │       ├── index.ts
│   │   │       ├── mcpServer.ts
│   │   │       ├── mcpSocketClient.ts
│   │   │       ├── mcpSocketPool.ts
│   │   │       ├── toolCalls.ts
│   │   │       └── types.ts
│   │   ├── computer-use-input/
│   │   │   └── js/
│   │   │       └── index.js
│   │   ├── computer-use-mcp/
│   │   │   └── src/
│   │   │       ├── deniedApps.ts
│   │   │       ├── imageResize.ts
│   │   │       ├── index.ts
│   │   │       ├── keyBlocklist.ts
│   │   │       ├── mcpServer.ts
│   │   │       ├── pixelCompare.ts
│   │   │       ├── sentinelApps.ts
│   │   │       ├── toolCalls.ts
│   │   │       ├── tools.ts
│   │   │       └── types.ts
│   │   └── computer-use-swift/
│   │       └── js/
│   │           └── index.js
│   ├── @anthropic-ai/
│   │   ├── mcpb/
│   │   │   └── dist/
│   │   │       ├── cli/
│   │   │       │   ├── init.js
│   │   │       │   ├── pack.js
│   │   │       │   └── unpack.js
│   │   │       ├── node/
│   │   │       │   ├── files.js
│   │   │       │   ├── sign.js
│   │   │       │   └── validate.js
│   │   │       ├── shared/
│   │   │       │   ├── config.js
│   │   │       │   └── log.js
│   │   │       ├── index.js
│   │   │       ├── schemas-loose.js
│   │   │       └── schemas.js
│   │   └── sandbox-runtime/
│   │       └── dist/
│   │           ├── sandbox/
│   │           │   ├── generate-seccomp-filter.js
│   │           │   ├── http-proxy.js
│   │           │   ├── linux-sandbox-utils.js
│   │           │   ├── macos-sandbox-utils.js
│   │           │   ├── sandbox-config.js
│   │           │   ├── sandbox-manager.js
│   │           │   ├── sandbox-utils.js
│   │           │   ├── sandbox-violation-store.js
│   │           │   └── socks-proxy.js
│   │           ├── utils/
│   │           │   ├── debug.js
│   │           │   ├── platform.js
│   │           │   ├── ripgrep.js
│   │           │   └── which.js
│   │           └── index.js
│   ├── @aws/
│   │   └── lambda-invoke-store/
│   │       └── dist-cjs/
│   │           └── invoke-store.js
│   ├── @aws-crypto/
│   │   ├── crc32/
│   │   │   ├── build/
│   │   │   │   └── main/
│   │   │   │       ├── aws_crc32.js
│   │   │   │       └── index.js
│   │   │   └── node_modules/
│   │   │       └── @aws-crypto/
│   │   │           └── util/
│   │   │               ├── build/
│   │   │               │   └── main/
│   │   │               │       ├── convertToBuffer.js
│   │   │               │       ├── index.js
│   │   │               │       ├── isEmptyData.js
│   │   │               │       ├── numToUint8.js
│   │   │               │       └── uint32ArrayFrom.js
│   │   │               └── node_modules/
│   │   │                   └── @smithy/
│   │   │                       └── util-utf8/
│   │   │                           └── dist-cjs/
│   │   │                               └── index.js
│   │   ├── sha256-js/
│   │   │   ├── build/
│   │   │   │   ├── constants.js
│   │   │   │   ├── index.js
│   │   │   │   ├── jsSha256.js
│   │   │   │   └── RawSha256.js
│   │   │   └── node_modules/
│   │   │       └── tslib/
│   │   │           └── tslib.js
│   │   └── util/
│   │       └── build/
│   │           ├── convertToBuffer.js
│   │           ├── index.js
│   │           ├── isEmptyData.js
│   │           ├── numToUint8.js
│   │           └── uint32ArrayFrom.js
│   ├── @aws-sdk/
│   │   ├── client-bedrock/
│   │   │   ├── dist-cjs/
│   │   │   │   ├── auth/
│   │   │   │   │   └── httpAuthSchemeProvider.js
│   │   │   │   ├── endpoint/
│   │   │   │   │   ├── endpointResolver.js
│   │   │   │   │   └── ruleset.js
│   │   │   │   ├── index.js
│   │   │   │   ├── runtimeConfig.js
│   │   │   │   └── runtimeConfig.shared.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           ├── protocol-http/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           ├── smithy-client/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           ├── types/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           └── util-base64/
│   │   │               ├── dist-cjs/
│   │   │               │   ├── fromBase64.js
│   │   │               │   ├── index.js
│   │   │               │   └── toBase64.js
│   │   │               └── node_modules/
│   │   │                   └── @smithy/
│   │   │                       └── util-buffer-from/
│   │   │                           ├── dist-cjs/
│   │   │                           │   └── index.js
│   │   │                           └── node_modules/
│   │   │                               └── @smithy/
│   │   │                                   └── is-array-buffer/
│   │   │                                       └── dist-cjs/
│   │   │                                           └── index.js
│   │   ├── client-bedrock-runtime/
│   │   │   ├── dist-cjs/
│   │   │   │   ├── auth/
│   │   │   │   │   └── httpAuthSchemeProvider.js
│   │   │   │   ├── endpoint/
│   │   │   │   │   ├── endpointResolver.js
│   │   │   │   │   └── ruleset.js
│   │   │   │   ├── index.js
│   │   │   │   ├── runtimeConfig.js
│   │   │   │   └── runtimeConfig.shared.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           ├── eventstream-serde-node/
│   │   │           │   ├── dist-cjs/
│   │   │           │   │   └── index.js
│   │   │           │   └── node_modules/
│   │   │           │       └── @smithy/
│   │   │           │           └── eventstream-serde-universal/
│   │   │           │               └── dist-cjs/
│   │   │           │                   └── index.js
│   │   │           ├── protocol-http/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           ├── smithy-client/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           ├── types/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           └── util-base64/
│   │   │               ├── dist-cjs/
│   │   │               │   ├── fromBase64.js
│   │   │               │   ├── index.js
│   │   │               │   └── toBase64.js
│   │   │               └── node_modules/
│   │   │                   └── @smithy/
│   │   │                       └── util-buffer-from/
│   │   │                           ├── dist-cjs/
│   │   │                           │   └── index.js
│   │   │                           └── node_modules/
│   │   │                               └── @smithy/
│   │   │                                   └── is-array-buffer/
│   │   │                                       └── dist-cjs/
│   │   │                                           └── index.js
│   │   ├── client-cognito-identity/
│   │   │   ├── dist-cjs/
│   │   │   │   ├── auth/
│   │   │   │   │   └── httpAuthSchemeProvider.js
│   │   │   │   ├── endpoint/
│   │   │   │   │   ├── endpointResolver.js
│   │   │   │   │   └── ruleset.js
│   │   │   │   ├── index.js
│   │   │   │   ├── runtimeConfig.js
│   │   │   │   └── runtimeConfig.shared.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           ├── protocol-http/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           ├── smithy-client/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           ├── types/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           └── util-base64/
│   │   │               ├── dist-cjs/
│   │   │               │   ├── fromBase64.js
│   │   │               │   ├── index.js
│   │   │               │   └── toBase64.js
│   │   │               └── node_modules/
│   │   │                   └── @smithy/
│   │   │                       └── util-buffer-from/
│   │   │                           ├── dist-cjs/
│   │   │                           │   └── index.js
│   │   │                           └── node_modules/
│   │   │                               └── @smithy/
│   │   │                                   └── is-array-buffer/
│   │   │                                       └── dist-cjs/
│   │   │                                           └── index.js
│   │   ├── client-sso/
│   │   │   ├── dist-cjs/
│   │   │   │   ├── auth/
│   │   │   │   │   └── httpAuthSchemeProvider.js
│   │   │   │   ├── endpoint/
│   │   │   │   │   ├── endpointResolver.js
│   │   │   │   │   └── ruleset.js
│   │   │   │   ├── index.js
│   │   │   │   ├── runtimeConfig.js
│   │   │   │   └── runtimeConfig.shared.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           ├── protocol-http/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           ├── smithy-client/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           ├── types/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           └── util-base64/
│   │   │               ├── dist-cjs/
│   │   │               │   ├── fromBase64.js
│   │   │               │   ├── index.js
│   │   │               │   └── toBase64.js
│   │   │               └── node_modules/
│   │   │                   └── @smithy/
│   │   │                       └── util-buffer-from/
│   │   │                           ├── dist-cjs/
│   │   │                           │   └── index.js
│   │   │                           └── node_modules/
│   │   │                               └── @smithy/
│   │   │                                   └── is-array-buffer/
│   │   │                                       └── dist-cjs/
│   │   │                                           └── index.js
│   │   ├── client-sts/
│   │   │   ├── dist-cjs/
│   │   │   │   ├── auth/
│   │   │   │   │   ├── httpAuthExtensionConfiguration.js
│   │   │   │   │   └── httpAuthSchemeProvider.js
│   │   │   │   ├── endpoint/
│   │   │   │   │   ├── EndpointParameters.js
│   │   │   │   │   ├── endpointResolver.js
│   │   │   │   │   └── ruleset.js
│   │   │   │   ├── index.js
│   │   │   │   ├── runtimeConfig.js
│   │   │   │   ├── runtimeConfig.shared.js
│   │   │   │   ├── runtimeExtensions.js
│   │   │   │   └── STSClient.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           ├── protocol-http/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           ├── smithy-client/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           ├── types/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           └── util-base64/
│   │   │               ├── dist-cjs/
│   │   │               │   ├── fromBase64.js
│   │   │               │   ├── index.js
│   │   │               │   └── toBase64.js
│   │   │               └── node_modules/
│   │   │                   └── @smithy/
│   │   │                       └── util-buffer-from/
│   │   │                           ├── dist-cjs/
│   │   │                           │   └── index.js
│   │   │                           └── node_modules/
│   │   │                               └── @smithy/
│   │   │                                   └── is-array-buffer/
│   │   │                                       └── dist-cjs/
│   │   │                                           └── index.js
│   │   ├── core/
│   │   │   ├── dist-cjs/
│   │   │   │   ├── submodules/
│   │   │   │   │   ├── client/
│   │   │   │   │   │   └── index.js
│   │   │   │   │   ├── httpAuthSchemes/
│   │   │   │   │   │   └── index.js
│   │   │   │   │   └── protocols/
│   │   │   │   │       └── index.js
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           ├── protocol-http/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           ├── signature-v4/
│   │   │           │   ├── dist-cjs/
│   │   │           │   │   └── index.js
│   │   │           │   └── node_modules/
│   │   │           │       └── @smithy/
│   │   │           │           ├── is-array-buffer/
│   │   │           │           │   └── dist-cjs/
│   │   │           │           │       └── index.js
│   │   │           │           ├── util-hex-encoding/
│   │   │           │           │   └── dist-cjs/
│   │   │           │           │       └── index.js
│   │   │           │           └── util-uri-escape/
│   │   │           │               └── dist-cjs/
│   │   │           │                   └── index.js
│   │   │           ├── smithy-client/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           ├── types/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           └── util-base64/
│   │   │               ├── dist-cjs/
│   │   │               │   ├── fromBase64.js
│   │   │               │   ├── index.js
│   │   │               │   └── toBase64.js
│   │   │               └── node_modules/
│   │   │                   └── @smithy/
│   │   │                       └── util-buffer-from/
│   │   │                           ├── dist-cjs/
│   │   │                           │   └── index.js
│   │   │                           └── node_modules/
│   │   │                               └── @smithy/
│   │   │                                   └── is-array-buffer/
│   │   │                                       └── dist-cjs/
│   │   │                                           └── index.js
│   │   ├── credential-provider-cognito-identity/
│   │   │   └── dist-cjs/
│   │   │       ├── index.js
│   │   │       └── loadCognitoIdentity-BPNvueUJ.js
│   │   ├── credential-provider-env/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── credential-provider-http/
│   │   │   ├── dist-cjs/
│   │   │   │   ├── fromHttp/
│   │   │   │   │   ├── checkUrl.js
│   │   │   │   │   ├── fromHttp.js
│   │   │   │   │   ├── requestHelpers.js
│   │   │   │   │   └── retry-wrapper.js
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           ├── protocol-http/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           ├── smithy-client/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           └── types/
│   │   │               └── dist-cjs/
│   │   │                   └── index.js
│   │   ├── credential-provider-ini/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── credential-provider-login/
│   │   │   ├── dist-cjs/
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           ├── protocol-http/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           └── types/
│   │   │               └── dist-cjs/
│   │   │                   └── index.js
│   │   ├── credential-provider-node/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── credential-provider-process/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── credential-provider-sso/
│   │   │   └── dist-cjs/
│   │   │       ├── index.js
│   │   │       └── loadSso-CVy8iqsZ.js
│   │   ├── credential-provider-web-identity/
│   │   │   └── dist-cjs/
│   │   │       ├── fromTokenFile.js
│   │   │       ├── fromWebToken.js
│   │   │       └── index.js
│   │   ├── credential-providers/
│   │   │   └── dist-cjs/
│   │   │       ├── createCredentialChain.js
│   │   │       ├── fromCognitoIdentity.js
│   │   │       ├── fromCognitoIdentityPool.js
│   │   │       ├── fromContainerMetadata.js
│   │   │       ├── fromEnv.js
│   │   │       ├── fromIni.js
│   │   │       ├── fromInstanceMetadata.js
│   │   │       ├── fromLoginCredentials.js
│   │   │       ├── fromNodeProviderChain.js
│   │   │       ├── fromProcess.js
│   │   │       ├── fromSSO.js
│   │   │       ├── fromTemporaryCredentials.base.js
│   │   │       ├── fromTemporaryCredentials.js
│   │   │       ├── fromTokenFile.js
│   │   │       ├── fromWebToken.js
│   │   │       ├── index.js
│   │   │       └── loadSts.js
│   │   ├── eventstream-handler-node/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── middleware-eventstream/
│   │   │   ├── dist-cjs/
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           ├── protocol-http/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           └── types/
│   │   │               └── dist-cjs/
│   │   │                   └── index.js
│   │   ├── middleware-host-header/
│   │   │   ├── dist-cjs/
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           ├── protocol-http/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           └── types/
│   │   │               └── dist-cjs/
│   │   │                   └── index.js
│   │   ├── middleware-logger/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── middleware-recursion-detection/
│   │   │   ├── dist-cjs/
│   │   │   │   ├── index.js
│   │   │   │   └── recursionDetectionMiddleware.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           ├── protocol-http/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           └── types/
│   │   │               └── dist-cjs/
│   │   │                   └── index.js
│   │   ├── middleware-user-agent/
│   │   │   ├── dist-cjs/
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           ├── protocol-http/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           └── types/
│   │   │               └── dist-cjs/
│   │   │                   └── index.js
│   │   ├── middleware-websocket/
│   │   │   ├── dist-cjs/
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           ├── fetch-http-handler/
│   │   │           │   ├── dist-cjs/
│   │   │           │   │   └── index.js
│   │   │           │   └── node_modules/
│   │   │           │       └── @smithy/
│   │   │           │           ├── querystring-builder/
│   │   │           │           │   ├── dist-cjs/
│   │   │           │           │   │   └── index.js
│   │   │           │           │   └── node_modules/
│   │   │           │           │       └── @smithy/
│   │   │           │           │           └── util-uri-escape/
│   │   │           │           │               └── dist-cjs/
│   │   │           │           │                   └── index.js
│   │   │           │           └── util-base64/
│   │   │           │               ├── dist-cjs/
│   │   │           │               │   ├── fromBase64.js
│   │   │           │               │   ├── index.js
│   │   │           │               │   └── toBase64.js
│   │   │           │               └── node_modules/
│   │   │           │                   └── @smithy/
│   │   │           │                       └── util-buffer-from/
│   │   │           │                           ├── dist-cjs/
│   │   │           │                           │   └── index.js
│   │   │           │                           └── node_modules/
│   │   │           │                               └── @smithy/
│   │   │           │                                   └── is-array-buffer/
│   │   │           │                                       └── dist-cjs/
│   │   │           │                                           └── index.js
│   │   │           ├── protocol-http/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           ├── types/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           └── util-hex-encoding/
│   │   │               └── dist-cjs/
│   │   │                   └── index.js
│   │   ├── nested-clients/
│   │   │   ├── dist-cjs/
│   │   │   │   └── submodules/
│   │   │   │       ├── signin/
│   │   │   │       │   ├── auth/
│   │   │   │       │   │   └── httpAuthSchemeProvider.js
│   │   │   │       │   ├── endpoint/
│   │   │   │       │   │   ├── endpointResolver.js
│   │   │   │       │   │   └── ruleset.js
│   │   │   │       │   ├── index.js
│   │   │   │       │   ├── runtimeConfig.js
│   │   │   │       │   └── runtimeConfig.shared.js
│   │   │   │       ├── sso-oidc/
│   │   │   │       │   ├── auth/
│   │   │   │       │   │   └── httpAuthSchemeProvider.js
│   │   │   │       │   ├── endpoint/
│   │   │   │       │   │   ├── endpointResolver.js
│   │   │   │       │   │   └── ruleset.js
│   │   │   │       │   ├── index.js
│   │   │   │       │   ├── runtimeConfig.js
│   │   │   │       │   └── runtimeConfig.shared.js
│   │   │   │       └── sts/
│   │   │   │           ├── auth/
│   │   │   │           │   ├── httpAuthExtensionConfiguration.js
│   │   │   │           │   └── httpAuthSchemeProvider.js
│   │   │   │           ├── endpoint/
│   │   │   │           │   ├── EndpointParameters.js
│   │   │   │           │   ├── endpointResolver.js
│   │   │   │           │   └── ruleset.js
│   │   │   │           ├── index.js
│   │   │   │           ├── runtimeConfig.js
│   │   │   │           ├── runtimeConfig.shared.js
│   │   │   │           ├── runtimeExtensions.js
│   │   │   │           └── STSClient.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           ├── protocol-http/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           ├── smithy-client/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           ├── types/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           └── util-base64/
│   │   │               ├── dist-cjs/
│   │   │               │   ├── fromBase64.js
│   │   │               │   ├── index.js
│   │   │               │   └── toBase64.js
│   │   │               └── node_modules/
│   │   │                   └── @smithy/
│   │   │                       └── util-buffer-from/
│   │   │                           ├── dist-cjs/
│   │   │                           │   └── index.js
│   │   │                           └── node_modules/
│   │   │                               └── @smithy/
│   │   │                                   └── is-array-buffer/
│   │   │                                       └── dist-cjs/
│   │   │                                           └── index.js
│   │   ├── region-config-resolver/
│   │   │   └── dist-cjs/
│   │   │       ├── regionConfig/
│   │   │       │   └── stsRegionDefaultResolver.js
│   │   │       └── index.js
│   │   ├── token-providers/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── util-endpoints/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── util-format-url/
│   │   │   ├── dist-cjs/
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           └── querystring-builder/
│   │   │               ├── dist-cjs/
│   │   │               │   └── index.js
│   │   │               └── node_modules/
│   │   │                   └── @smithy/
│   │   │                       └── util-uri-escape/
│   │   │                           └── dist-cjs/
│   │   │                               └── index.js
│   │   ├── util-user-agent-node/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── util-utf8-browser/
│   │   │   └── dist-cjs/
│   │   │       ├── index.js
│   │   │       ├── pureJs.js
│   │   │       └── whatwgEncodingApi.js
│   │   └── xml-builder/
│   │       └── dist-cjs/
│   │           ├── index.js
│   │           └── xml-parser.js
│   ├── @azure/
│   │   ├── abort-controller/
│   │   │   └── dist/
│   │   │       └── esm/
│   │   │           ├── AbortError.js
│   │   │           └── index.js
│   │   ├── core-client/
│   │   │   └── dist/
│   │   │       ├── commonjs/
│   │   │       │   └── state.js
│   │   │       └── esm/
│   │   │           ├── deserializationPolicy.js
│   │   │           ├── httpClientCache.js
│   │   │           ├── index.js
│   │   │           ├── interfaceHelpers.js
│   │   │           ├── interfaces.js
│   │   │           ├── log.js
│   │   │           ├── operationHelpers.js
│   │   │           ├── pipeline.js
│   │   │           ├── serializationPolicy.js
│   │   │           ├── serializer.js
│   │   │           ├── serviceClient.js
│   │   │           ├── state.js
│   │   │           ├── urlHelpers.js
│   │   │           └── utils.js
│   │   ├── core-rest-pipeline/
│   │   │   └── dist/
│   │   │       └── esm/
│   │   │           ├── policies/
│   │   │           │   ├── agentPolicy.js
│   │   │           │   ├── bearerTokenAuthenticationPolicy.js
│   │   │           │   ├── decompressResponsePolicy.js
│   │   │           │   ├── defaultRetryPolicy.js
│   │   │           │   ├── formDataPolicy.js
│   │   │           │   ├── logPolicy.js
│   │   │           │   ├── multipartPolicy.js
│   │   │           │   ├── proxyPolicy.js
│   │   │           │   ├── redirectPolicy.js
│   │   │           │   ├── retryPolicy.js
│   │   │           │   ├── setClientRequestIdPolicy.js
│   │   │           │   ├── tlsPolicy.js
│   │   │           │   ├── tracingPolicy.js
│   │   │           │   ├── userAgentPolicy.js
│   │   │           │   └── wrapAbortSignalLikePolicy.js
│   │   │           ├── util/
│   │   │           │   ├── file.js
│   │   │           │   ├── tokenCycler.js
│   │   │           │   ├── userAgent.js
│   │   │           │   ├── userAgentPlatform.js
│   │   │           │   └── wrapAbortSignal.js
│   │   │           ├── constants.js
│   │   │           ├── createPipelineFromOptions.js
│   │   │           ├── defaultHttpClient.js
│   │   │           ├── httpHeaders.js
│   │   │           ├── index.js
│   │   │           ├── log.js
│   │   │           ├── pipeline.js
│   │   │           ├── pipelineRequest.js
│   │   │           └── restError.js
│   │   ├── core-tracing/
│   │   │   └── dist/
│   │   │       ├── commonjs/
│   │   │       │   └── state.js
│   │   │       └── esm/
│   │   │           ├── index.js
│   │   │           ├── instrumenter.js
│   │   │           ├── state.js
│   │   │           ├── tracingClient.js
│   │   │           └── tracingContext.js
│   │   ├── core-util/
│   │   │   └── dist/
│   │   │       └── esm/
│   │   │           ├── createAbortablePromise.js
│   │   │           ├── delay.js
│   │   │           ├── error.js
│   │   │           └── index.js
│   │   ├── identity/
│   │   │   └── dist/
│   │   │       └── esm/
│   │   │           ├── client/
│   │   │           │   └── identityClient.js
│   │   │           ├── credentials/
│   │   │           │   ├── managedIdentityCredential/
│   │   │           │   │   ├── imdsMsi.js
│   │   │           │   │   ├── imdsRetryPolicy.js
│   │   │           │   │   ├── index.js
│   │   │           │   │   ├── tokenExchangeMsi.js
│   │   │           │   │   └── utils.js
│   │   │           │   ├── authorizationCodeCredential.js
│   │   │           │   ├── azureCliCredential.js
│   │   │           │   ├── azureDeveloperCliCredential.js
│   │   │           │   ├── azurePipelinesCredential.js
│   │   │           │   ├── azurePowerShellCredential.js
│   │   │           │   ├── chainedTokenCredential.js
│   │   │           │   ├── clientAssertionCredential.js
│   │   │           │   ├── clientCertificateCredential.js
│   │   │           │   ├── clientSecretCredential.js
│   │   │           │   ├── defaultAzureCredential.js
│   │   │           │   ├── deviceCodeCredential.js
│   │   │           │   ├── environmentCredential.js
│   │   │           │   ├── interactiveBrowserCredential.js
│   │   │           │   ├── onBehalfOfCredential.js
│   │   │           │   ├── usernamePasswordCredential.js
│   │   │           │   ├── visualStudioCodeCredential.js
│   │   │           │   └── workloadIdentityCredential.js
│   │   │           ├── msal/
│   │   │           │   ├── nodeFlows/
│   │   │           │   │   ├── msalClient.js
│   │   │           │   │   └── msalPlugins.js
│   │   │           │   ├── msal.js
│   │   │           │   └── utils.js
│   │   │           ├── plugins/
│   │   │           │   └── consumer.js
│   │   │           ├── util/
│   │   │           │   ├── identityTokenEndpoint.js
│   │   │           │   ├── logging.js
│   │   │           │   ├── processMultiTenantRequest.js
│   │   │           │   ├── processUtils.js
│   │   │           │   ├── scopeUtils.js
│   │   │           │   ├── subscriptionUtils.js
│   │   │           │   ├── tenantIdUtils.js
│   │   │           │   └── tracing.js
│   │   │           ├── constants.js
│   │   │           ├── errors.js
│   │   │           ├── index.js
│   │   │           ├── regionalAuthority.js
│   │   │           └── tokenProvider.js
│   │   └── logger/
│   │       └── dist/
│   │           └── esm/
│   │               └── index.js
│   ├── @commander-js/
│   │   └── extra-typings/
│   │       └── index.js
│   ├── @grpc/
│   │   ├── grpc-js/
│   │   │   └── build/
│   │   │       └── src/
│   │   │           ├── admin.js
│   │   │           ├── backoff-timeout.js
│   │   │           ├── call-credentials.js
│   │   │           ├── call-interface.js
│   │   │           ├── call-number.js
│   │   │           ├── call.js
│   │   │           ├── certificate-provider.js
│   │   │           ├── channel-credentials.js
│   │   │           ├── channel-options.js
│   │   │           ├── channel.js
│   │   │           ├── channelz.js
│   │   │           ├── client-interceptors.js
│   │   │           ├── client.js
│   │   │           ├── compression-algorithms.js
│   │   │           ├── compression-filter.js
│   │   │           ├── connectivity-state.js
│   │   │           ├── constants.js
│   │   │           ├── control-plane-status.js
│   │   │           ├── deadline.js
│   │   │           ├── duration.js
│   │   │           ├── environment.js
│   │   │           ├── error.js
│   │   │           ├── experimental.js
│   │   │           ├── filter-stack.js
│   │   │           ├── filter.js
│   │   │           ├── http_proxy.js
│   │   │           ├── index.js
│   │   │           ├── internal-channel.js
│   │   │           ├── load-balancer-child-handler.js
│   │   │           ├── load-balancer-outlier-detection.js
│   │   │           ├── load-balancer-pick-first.js
│   │   │           ├── load-balancer-round-robin.js
│   │   │           ├── load-balancer-weighted-round-robin.js
│   │   │           ├── load-balancer.js
│   │   │           ├── load-balancing-call.js
│   │   │           ├── logging.js
│   │   │           ├── make-client.js
│   │   │           ├── metadata.js
│   │   │           ├── orca.js
│   │   │           ├── picker.js
│   │   │           ├── priority-queue.js
│   │   │           ├── resolver-dns.js
│   │   │           ├── resolver-ip.js
│   │   │           ├── resolver-uds.js
│   │   │           ├── resolver.js
│   │   │           ├── resolving-call.js
│   │   │           ├── resolving-load-balancer.js
│   │   │           ├── retrying-call.js
│   │   │           ├── server-call.js
│   │   │           ├── server-credentials.js
│   │   │           ├── server-interceptors.js
│   │   │           ├── server.js
│   │   │           ├── service-config.js
│   │   │           ├── single-subchannel-channel.js
│   │   │           ├── status-builder.js
│   │   │           ├── stream-decoder.js
│   │   │           ├── subchannel-address.js
│   │   │           ├── subchannel-call.js
│   │   │           ├── subchannel-interface.js
│   │   │           ├── subchannel-pool.js
│   │   │           ├── subchannel.js
│   │   │           ├── tls-helpers.js
│   │   │           ├── transport.js
│   │   │           └── uri-parser.js
│   │   └── proto-loader/
│   │       ├── build/
│   │       │   └── src/
│   │       │       ├── index.js
│   │       │       └── util.js
│   │       └── node_modules/
│   │           └── long/
│   │               └── umd/
│   │                   └── index.js
│   ├── @inquirer/
│   │   ├── core/
│   │   │   └── node_modules/
│   │   │       ├── ansi-escapes/
│   │   │       │   └── index.js
│   │   │       ├── mute-stream/
│   │   │       │   └── lib/
│   │   │       │       └── index.js
│   │   │       ├── strip-ansi/
│   │   │       │   ├── node_modules/
│   │   │       │   │   └── ansi-regex/
│   │   │       │   │       └── index.js
│   │   │       │   └── index.js
│   │   │       └── wrap-ansi/
│   │   │           ├── node_modules/
│   │   │           │   └── ansi-styles/
│   │   │           │       └── index.js
│   │   │           └── index.js
│   │   ├── figures/
│   │   │   └── dist/
│   │   │       └── esm/
│   │   │           └── index.js
│   │   └── select/
│   │       └── node_modules/
│   │           └── ansi-escapes/
│   │               └── index.js
│   ├── @js-sdsl/
│   │   └── ordered-map/
│   │       └── dist/
│   │           └── cjs/
│   │               └── index.js
│   ├── @mixmark-io/
│   │   └── domino/
│   │       └── lib/
│   │           ├── attributes.js
│   │           ├── CharacterData.js
│   │           ├── ChildNode.js
│   │           ├── Comment.js
│   │           ├── config.js
│   │           ├── ContainerNode.js
│   │           ├── CSSStyleDeclaration.js
│   │           ├── CustomEvent.js
│   │           ├── defineElement.js
│   │           ├── Document.js
│   │           ├── DocumentFragment.js
│   │           ├── DocumentType.js
│   │           ├── DOMException.js
│   │           ├── DOMImplementation.js
│   │           ├── DOMTokenList.js
│   │           ├── Element.js
│   │           ├── Event.js
│   │           ├── events.js
│   │           ├── EventTarget.js
│   │           ├── FilteredElementList.js
│   │           ├── htmlelts.js
│   │           ├── HTMLParser.js
│   │           ├── impl.js
│   │           ├── index.js
│   │           ├── Leaf.js
│   │           ├── LinkedList.js
│   │           ├── Location.js
│   │           ├── MouseEvent.js
│   │           ├── MutationConstants.js
│   │           ├── NamedNodeMap.js
│   │           ├── NavigatorID.js
│   │           ├── Node.js
│   │           ├── NodeFilter.js
│   │           ├── NodeIterator.js
│   │           ├── NodeList.es5.js
│   │           ├── NodeList.es6.js
│   │           ├── NodeList.js
│   │           ├── NodeTraversal.js
│   │           ├── NodeUtils.js
│   │           ├── NonDocumentTypeChildNode.js
│   │           ├── ProcessingInstruction.js
│   │           ├── select.js
│   │           ├── style_parser.js
│   │           ├── svg.js
│   │           ├── Text.js
│   │           ├── TreeWalker.js
│   │           ├── UIEvent.js
│   │           ├── URL.js
│   │           ├── URLUtils.js
│   │           ├── utils.js
│   │           ├── Window.js
│   │           ├── WindowTimers.js
│   │           └── xmlnames.js
│   ├── @modelcontextprotocol/
│   │   └── sdk/
│   │       └── dist/
│   │           └── esm/
│   │               ├── client/
│   │               │   ├── auth.js
│   │               │   ├── index.js
│   │               │   ├── sse.js
│   │               │   ├── stdio.js
│   │               │   └── streamableHttp.js
│   │               ├── experimental/
│   │               │   └── tasks/
│   │               │       ├── client.js
│   │               │       ├── helpers.js
│   │               │       ├── interfaces.js
│   │               │       └── server.js
│   │               ├── server/
│   │               │   ├── auth/
│   │               │   │   └── errors.js
│   │               │   ├── index.js
│   │               │   ├── stdio.js
│   │               │   ├── zod-compat.js
│   │               │   └── zod-json-schema-compat.js
│   │               ├── shared/
│   │               │   ├── auth-utils.js
│   │               │   ├── auth.js
│   │               │   ├── protocol.js
│   │               │   ├── stdio.js
│   │               │   └── transport.js
│   │               ├── validation/
│   │               │   └── ajv-provider.js
│   │               └── types.js
│   ├── @opentelemetry/
│   │   ├── api/
│   │   │   └── build/
│   │   │       └── src/
│   │   │           ├── api/
│   │   │           │   ├── context.js
│   │   │           │   ├── diag.js
│   │   │           │   ├── metrics.js
│   │   │           │   ├── propagation.js
│   │   │           │   └── trace.js
│   │   │           ├── baggage/
│   │   │           │   ├── internal/
│   │   │           │   │   ├── baggage-impl.js
│   │   │           │   │   └── symbol.js
│   │   │           │   ├── context-helpers.js
│   │   │           │   └── utils.js
│   │   │           ├── context/
│   │   │           │   ├── context.js
│   │   │           │   └── NoopContextManager.js
│   │   │           ├── diag/
│   │   │           │   ├── internal/
│   │   │           │   │   └── logLevelLogger.js
│   │   │           │   ├── ComponentLogger.js
│   │   │           │   ├── consoleLogger.js
│   │   │           │   └── types.js
│   │   │           ├── internal/
│   │   │           │   ├── global-utils.js
│   │   │           │   └── semver.js
│   │   │           ├── metrics/
│   │   │           │   ├── Metric.js
│   │   │           │   ├── NoopMeter.js
│   │   │           │   └── NoopMeterProvider.js
│   │   │           ├── platform/
│   │   │           │   ├── node/
│   │   │           │   │   ├── globalThis.js
│   │   │           │   │   └── index.js
│   │   │           │   └── index.js
│   │   │           ├── propagation/
│   │   │           │   ├── NoopTextMapPropagator.js
│   │   │           │   └── TextMapPropagator.js
│   │   │           ├── trace/
│   │   │           │   ├── internal/
│   │   │           │   │   ├── tracestate-impl.js
│   │   │           │   │   ├── tracestate-validators.js
│   │   │           │   │   └── utils.js
│   │   │           │   ├── context-utils.js
│   │   │           │   ├── invalid-span-constants.js
│   │   │           │   ├── NonRecordingSpan.js
│   │   │           │   ├── NoopTracer.js
│   │   │           │   ├── NoopTracerProvider.js
│   │   │           │   ├── ProxyTracer.js
│   │   │           │   ├── ProxyTracerProvider.js
│   │   │           │   ├── SamplingResult.js
│   │   │           │   ├── span_kind.js
│   │   │           │   ├── spancontext-utils.js
│   │   │           │   ├── status.js
│   │   │           │   └── trace_flags.js
│   │   │           ├── context-api.js
│   │   │           ├── diag-api.js
│   │   │           ├── index.js
│   │   │           ├── metrics-api.js
│   │   │           ├── propagation-api.js
│   │   │           ├── trace-api.js
│   │   │           └── version.js
│   │   ├── api-logs/
│   │   │   └── build/
│   │   │       └── src/
│   │   │           ├── api/
│   │   │           │   └── logs.js
│   │   │           ├── internal/
│   │   │           │   └── global-utils.js
│   │   │           ├── platform/
│   │   │           │   ├── node/
│   │   │           │   │   ├── globalThis.js
│   │   │           │   │   └── index.js
│   │   │           │   └── index.js
│   │   │           ├── types/
│   │   │           │   └── LogRecord.js
│   │   │           ├── index.js
│   │   │           ├── NoopLogger.js
│   │   │           ├── NoopLoggerProvider.js
│   │   │           ├── ProxyLogger.js
│   │   │           └── ProxyLoggerProvider.js
│   │   ├── core/
│   │   │   └── build/
│   │   │       └── src/
│   │   │           ├── baggage/
│   │   │           │   ├── propagation/
│   │   │           │   │   └── W3CBaggagePropagator.js
│   │   │           │   ├── constants.js
│   │   │           │   └── utils.js
│   │   │           ├── common/
│   │   │           │   ├── anchored-clock.js
│   │   │           │   ├── attributes.js
│   │   │           │   ├── global-error-handler.js
│   │   │           │   ├── logging-error-handler.js
│   │   │           │   ├── time.js
│   │   │           │   └── timer-util.js
│   │   │           ├── internal/
│   │   │           │   ├── exporter.js
│   │   │           │   └── validators.js
│   │   │           ├── platform/
│   │   │           │   ├── node/
│   │   │           │   │   ├── environment.js
│   │   │           │   │   ├── globalThis.js
│   │   │           │   │   ├── index.js
│   │   │           │   │   ├── performance.js
│   │   │           │   │   └── sdk-info.js
│   │   │           │   └── index.js
│   │   │           ├── propagation/
│   │   │           │   └── composite.js
│   │   │           ├── trace/
│   │   │           │   ├── rpc-metadata.js
│   │   │           │   ├── suppress-tracing.js
│   │   │           │   ├── TraceState.js
│   │   │           │   └── W3CTraceContextPropagator.js
│   │   │           ├── utils/
│   │   │           │   ├── callback.js
│   │   │           │   ├── configuration.js
│   │   │           │   ├── lodash.merge.js
│   │   │           │   ├── merge.js
│   │   │           │   ├── promise.js
│   │   │           │   ├── timeout.js
│   │   │           │   └── url.js
│   │   │           ├── ExportResult.js
│   │   │           ├── index.js
│   │   │           ├── semconv.js
│   │   │           └── version.js
│   │   ├── exporter-logs-otlp-grpc/
│   │   │   └── build/
│   │   │       └── src/
│   │   │           ├── index.js
│   │   │           └── OTLPLogExporter.js
│   │   ├── exporter-logs-otlp-http/
│   │   │   └── build/
│   │   │       └── src/
│   │   │           ├── platform/
│   │   │           │   ├── node/
│   │   │           │   │   ├── index.js
│   │   │           │   │   └── OTLPLogExporter.js
│   │   │           │   └── index.js
│   │   │           └── index.js
│   │   ├── exporter-logs-otlp-proto/
│   │   │   └── build/
│   │   │       └── src/
│   │   │           ├── platform/
│   │   │           │   ├── node/
│   │   │           │   │   ├── index.js
│   │   │           │   │   └── OTLPLogExporter.js
│   │   │           │   └── index.js
│   │   │           └── index.js
│   │   ├── exporter-metrics-otlp-grpc/
│   │   │   └── build/
│   │   │       └── src/
│   │   │           ├── index.js
│   │   │           └── OTLPMetricExporter.js
│   │   ├── exporter-metrics-otlp-http/
│   │   │   └── build/
│   │   │       └── src/
│   │   │           ├── platform/
│   │   │           │   ├── node/
│   │   │           │   │   ├── index.js
│   │   │           │   │   └── OTLPMetricExporter.js
│   │   │           │   └── index.js
│   │   │           ├── index.js
│   │   │           ├── OTLPMetricExporterBase.js
│   │   │           └── OTLPMetricExporterOptions.js
│   │   ├── exporter-metrics-otlp-proto/
│   │   │   └── build/
│   │   │       └── src/
│   │   │           ├── platform/
│   │   │           │   ├── node/
│   │   │           │   │   ├── index.js
│   │   │           │   │   └── OTLPMetricExporter.js
│   │   │           │   └── index.js
│   │   │           └── index.js
│   │   ├── exporter-prometheus/
│   │   │   └── build/
│   │   │       └── src/
│   │   │           ├── index.js
│   │   │           ├── PrometheusExporter.js
│   │   │           └── PrometheusSerializer.js
│   │   ├── exporter-trace-otlp-grpc/
│   │   │   └── build/
│   │   │       └── src/
│   │   │           ├── index.js
│   │   │           └── OTLPTraceExporter.js
│   │   ├── exporter-trace-otlp-http/
│   │   │   └── build/
│   │   │       └── src/
│   │   │           ├── platform/
│   │   │           │   ├── node/
│   │   │           │   │   ├── index.js
│   │   │           │   │   └── OTLPTraceExporter.js
│   │   │           │   └── index.js
│   │   │           └── index.js
│   │   ├── exporter-trace-otlp-proto/
│   │   │   └── build/
│   │   │       └── src/
│   │   │           ├── platform/
│   │   │           │   ├── node/
│   │   │           │   │   ├── index.js
│   │   │           │   │   └── OTLPTraceExporter.js
│   │   │           │   └── index.js
│   │   │           └── index.js
│   │   ├── otlp-exporter-base/
│   │   │   └── build/
│   │   │       └── src/
│   │   │           ├── configuration/
│   │   │           │   ├── convert-legacy-http-options.js
│   │   │           │   ├── convert-legacy-node-http-options.js
│   │   │           │   ├── legacy-node-configuration.js
│   │   │           │   ├── otlp-http-configuration.js
│   │   │           │   ├── otlp-node-http-configuration.js
│   │   │           │   ├── otlp-node-http-env-configuration.js
│   │   │           │   ├── shared-configuration.js
│   │   │           │   └── shared-env-configuration.js
│   │   │           ├── transport/
│   │   │           │   ├── http-exporter-transport.js
│   │   │           │   └── http-transport-utils.js
│   │   │           ├── bounded-queue-export-promise-handler.js
│   │   │           ├── index-node-http.js
│   │   │           ├── index.js
│   │   │           ├── is-export-retryable.js
│   │   │           ├── logging-response-handler.js
│   │   │           ├── otlp-export-delegate.js
│   │   │           ├── otlp-http-export-delegate.js
│   │   │           ├── otlp-network-export-delegate.js
│   │   │           ├── OTLPExporterBase.js
│   │   │           ├── retrying-transport.js
│   │   │           ├── types.js
│   │   │           ├── util.js
│   │   │           └── version.js
│   │   ├── otlp-grpc-exporter-base/
│   │   │   └── build/
│   │   │       └── src/
│   │   │           ├── configuration/
│   │   │           │   ├── convert-legacy-otlp-grpc-options.js
│   │   │           │   ├── otlp-grpc-configuration.js
│   │   │           │   └── otlp-grpc-env-configuration.js
│   │   │           ├── create-service-client-constructor.js
│   │   │           ├── grpc-exporter-transport.js
│   │   │           ├── index.js
│   │   │           ├── otlp-grpc-export-delegate.js
│   │   │           └── version.js
│   │   ├── otlp-transformer/
│   │   │   └── build/
│   │   │       └── src/
│   │   │           ├── common/
│   │   │           │   ├── hex-to-binary.js
│   │   │           │   ├── internal.js
│   │   │           │   └── utils.js
│   │   │           ├── generated/
│   │   │           │   └── root.js
│   │   │           ├── logs/
│   │   │           │   ├── json/
│   │   │           │   │   ├── index.js
│   │   │           │   │   └── logs.js
│   │   │           │   ├── protobuf/
│   │   │           │   │   ├── index.js
│   │   │           │   │   └── logs.js
│   │   │           │   └── internal.js
│   │   │           ├── metrics/
│   │   │           │   ├── json/
│   │   │           │   │   ├── index.js
│   │   │           │   │   └── metrics.js
│   │   │           │   ├── protobuf/
│   │   │           │   │   ├── index.js
│   │   │           │   │   └── metrics.js
│   │   │           │   ├── internal-types.js
│   │   │           │   └── internal.js
│   │   │           ├── trace/
│   │   │           │   ├── json/
│   │   │           │   │   ├── index.js
│   │   │           │   │   └── trace.js
│   │   │           │   ├── protobuf/
│   │   │           │   │   ├── index.js
│   │   │           │   │   └── trace.js
│   │   │           │   └── internal.js
│   │   │           └── index.js
│   │   ├── resources/
│   │   │   └── build/
│   │   │       └── src/
│   │   │           ├── detectors/
│   │   │           │   ├── platform/
│   │   │           │   │   ├── node/
│   │   │           │   │   │   ├── machine-id/
│   │   │           │   │   │   │   ├── execAsync.js
│   │   │           │   │   │   │   ├── getMachineId-bsd.js
│   │   │           │   │   │   │   ├── getMachineId-darwin.js
│   │   │           │   │   │   │   ├── getMachineId-linux.js
│   │   │           │   │   │   │   ├── getMachineId-unsupported.js
│   │   │           │   │   │   │   ├── getMachineId-win.js
│   │   │           │   │   │   │   └── getMachineId.js
│   │   │           │   │   │   ├── HostDetector.js
│   │   │           │   │   │   ├── index.js
│   │   │           │   │   │   ├── OSDetector.js
│   │   │           │   │   │   ├── ProcessDetector.js
│   │   │           │   │   │   ├── ServiceInstanceIdDetector.js
│   │   │           │   │   │   └── utils.js
│   │   │           │   │   └── index.js
│   │   │           │   ├── EnvDetector.js
│   │   │           │   ├── index.js
│   │   │           │   └── NoopDetector.js
│   │   │           ├── platform/
│   │   │           │   ├── node/
│   │   │           │   │   ├── default-service-name.js
│   │   │           │   │   └── index.js
│   │   │           │   └── index.js
│   │   │           ├── detect-resources.js
│   │   │           ├── index.js
│   │   │           ├── ResourceImpl.js
│   │   │           ├── semconv.js
│   │   │           └── utils.js
│   │   ├── sdk-logs/
│   │   │   └── build/
│   │   │       └── src/
│   │   │           ├── export/
│   │   │           │   ├── BatchLogRecordProcessorBase.js
│   │   │           │   ├── ConsoleLogRecordExporter.js
│   │   │           │   ├── InMemoryLogRecordExporter.js
│   │   │           │   ├── NoopLogRecordProcessor.js
│   │   │           │   └── SimpleLogRecordProcessor.js
│   │   │           ├── internal/
│   │   │           │   └── LoggerProviderSharedState.js
│   │   │           ├── platform/
│   │   │           │   ├── node/
│   │   │           │   │   ├── export/
│   │   │           │   │   │   └── BatchLogRecordProcessor.js
│   │   │           │   │   └── index.js
│   │   │           │   └── index.js
│   │   │           ├── config.js
│   │   │           ├── index.js
│   │   │           ├── Logger.js
│   │   │           ├── LoggerProvider.js
│   │   │           ├── LogRecordImpl.js
│   │   │           └── MultiLogRecordProcessor.js
│   │   ├── sdk-metrics/
│   │   │   └── build/
│   │   │       └── src/
│   │   │           ├── aggregator/
│   │   │           │   ├── exponential-histogram/
│   │   │           │   │   ├── mapping/
│   │   │           │   │   │   ├── ExponentMapping.js
│   │   │           │   │   │   ├── getMapping.js
│   │   │           │   │   │   ├── ieee754.js
│   │   │           │   │   │   ├── LogarithmMapping.js
│   │   │           │   │   │   └── types.js
│   │   │           │   │   ├── Buckets.js
│   │   │           │   │   └── util.js
│   │   │           │   ├── Drop.js
│   │   │           │   ├── ExponentialHistogram.js
│   │   │           │   ├── Histogram.js
│   │   │           │   ├── index.js
│   │   │           │   ├── LastValue.js
│   │   │           │   ├── Sum.js
│   │   │           │   └── types.js
│   │   │           ├── export/
│   │   │           │   ├── AggregationSelector.js
│   │   │           │   ├── AggregationTemporality.js
│   │   │           │   ├── ConsoleMetricExporter.js
│   │   │           │   ├── InMemoryMetricExporter.js
│   │   │           │   ├── MetricData.js
│   │   │           │   ├── MetricReader.js
│   │   │           │   └── PeriodicExportingMetricReader.js
│   │   │           ├── state/
│   │   │           │   ├── AsyncMetricStorage.js
│   │   │           │   ├── DeltaMetricProcessor.js
│   │   │           │   ├── HashMap.js
│   │   │           │   ├── MeterProviderSharedState.js
│   │   │           │   ├── MeterSharedState.js
│   │   │           │   ├── MetricCollector.js
│   │   │           │   ├── MetricStorage.js
│   │   │           │   ├── MetricStorageRegistry.js
│   │   │           │   ├── MultiWritableMetricStorage.js
│   │   │           │   ├── ObservableRegistry.js
│   │   │           │   ├── SyncMetricStorage.js
│   │   │           │   └── TemporalMetricProcessor.js
│   │   │           ├── view/
│   │   │           │   ├── Aggregation.js
│   │   │           │   ├── AggregationOption.js
│   │   │           │   ├── AttributesProcessor.js
│   │   │           │   ├── InstrumentSelector.js
│   │   │           │   ├── MeterSelector.js
│   │   │           │   ├── Predicate.js
│   │   │           │   ├── RegistrationConflicts.js
│   │   │           │   ├── View.js
│   │   │           │   └── ViewRegistry.js
│   │   │           ├── index.js
│   │   │           ├── InstrumentDescriptor.js
│   │   │           ├── Instruments.js
│   │   │           ├── Meter.js
│   │   │           ├── MeterProvider.js
│   │   │           ├── ObservableResult.js
│   │   │           └── utils.js
│   │   ├── sdk-trace-base/
│   │   │   └── build/
│   │   │       └── src/
│   │   │           ├── export/
│   │   │           │   ├── BatchSpanProcessorBase.js
│   │   │           │   ├── ConsoleSpanExporter.js
│   │   │           │   ├── InMemorySpanExporter.js
│   │   │           │   ├── NoopSpanProcessor.js
│   │   │           │   └── SimpleSpanProcessor.js
│   │   │           ├── platform/
│   │   │           │   ├── node/
│   │   │           │   │   ├── export/
│   │   │           │   │   │   └── BatchSpanProcessor.js
│   │   │           │   │   ├── index.js
│   │   │           │   │   └── RandomIdGenerator.js
│   │   │           │   └── index.js
│   │   │           ├── sampler/
│   │   │           │   ├── AlwaysOffSampler.js
│   │   │           │   ├── AlwaysOnSampler.js
│   │   │           │   ├── ParentBasedSampler.js
│   │   │           │   └── TraceIdRatioBasedSampler.js
│   │   │           ├── BasicTracerProvider.js
│   │   │           ├── config.js
│   │   │           ├── enums.js
│   │   │           ├── index.js
│   │   │           ├── MultiSpanProcessor.js
│   │   │           ├── Sampler.js
│   │   │           ├── Span.js
│   │   │           ├── Tracer.js
│   │   │           └── utility.js
│   │   └── semantic-conventions/
│   │       └── build/
│   │           └── src/
│   │               ├── internal/
│   │               │   └── utils.js
│   │               ├── resource/
│   │               │   ├── index.js
│   │               │   └── SemanticResourceAttributes.js
│   │               ├── trace/
│   │               │   ├── index.js
│   │               │   └── SemanticAttributes.js
│   │               ├── index.js
│   │               ├── stable_attributes.js
│   │               ├── stable_events.js
│   │               └── stable_metrics.js
│   ├── @pondwader/
│   │   └── socks5-server/
│   │       └── dist/
│   │           └── index.js
│   ├── @protobufjs/
│   │   ├── aspromise/
│   │   │   └── index.js
│   │   ├── base64/
│   │   │   └── index.js
│   │   ├── codegen/
│   │   │   └── index.js
│   │   ├── eventemitter/
│   │   │   └── index.js
│   │   ├── fetch/
│   │   │   └── index.js
│   │   ├── float/
│   │   │   └── index.js
│   │   ├── inquire/
│   │   │   └── index.js
│   │   ├── path/
│   │   │   └── index.js
│   │   ├── pool/
│   │   │   └── index.js
│   │   └── utf8/
│   │       └── index.js
│   ├── @smithy/
│   │   ├── config-resolver/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── core/
│   │   │   ├── dist-cjs/
│   │   │   │   ├── submodules/
│   │   │   │   │   ├── cbor/
│   │   │   │   │   │   └── index.js
│   │   │   │   │   ├── event-streams/
│   │   │   │   │   │   └── index.js
│   │   │   │   │   ├── protocols/
│   │   │   │   │   │   └── index.js
│   │   │   │   │   ├── schema/
│   │   │   │   │   │   └── index.js
│   │   │   │   │   └── serde/
│   │   │   │   │       └── index.js
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           ├── protocol-http/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           ├── types/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           └── util-base64/
│   │   │               ├── dist-cjs/
│   │   │               │   ├── fromBase64.js
│   │   │               │   ├── index.js
│   │   │               │   └── toBase64.js
│   │   │               └── node_modules/
│   │   │                   └── @smithy/
│   │   │                       └── util-buffer-from/
│   │   │                           ├── dist-cjs/
│   │   │                           │   └── index.js
│   │   │                           └── node_modules/
│   │   │                               └── @smithy/
│   │   │                                   └── is-array-buffer/
│   │   │                                       └── dist-cjs/
│   │   │                                           └── index.js
│   │   ├── credential-provider-imds/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── eventstream-codec/
│   │   │   ├── dist-cjs/
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           └── util-hex-encoding/
│   │   │               └── dist-cjs/
│   │   │                   └── index.js
│   │   ├── eventstream-serde-browser/
│   │   │   ├── dist-cjs/
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           └── eventstream-serde-universal/
│   │   │               └── dist-cjs/
│   │   │                   └── index.js
│   │   ├── eventstream-serde-config-resolver/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── eventstream-serde-node/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── eventstream-serde-universal/
│   │   │   ├── dist-cjs/
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           └── eventstream-codec/
│   │   │               ├── dist-cjs/
│   │   │               │   └── index.js
│   │   │               └── node_modules/
│   │   │                   ├── @aws-crypto/
│   │   │                   │   └── crc32/
│   │   │                   │       ├── build/
│   │   │                   │       │   ├── aws_crc32.js
│   │   │                   │       │   └── index.js
│   │   │                   │       └── node_modules/
│   │   │                   │           ├── @aws-crypto/
│   │   │                   │           │   └── util/
│   │   │                   │           │       └── build/
│   │   │                   │           │           ├── convertToBuffer.js
│   │   │                   │           │           ├── index.js
│   │   │                   │           │           ├── isEmptyData.js
│   │   │                   │           │           ├── numToUint8.js
│   │   │                   │           │           └── uint32ArrayFrom.js
│   │   │                   │           └── tslib/
│   │   │                   │               └── tslib.js
│   │   │                   └── @smithy/
│   │   │                       └── util-hex-encoding/
│   │   │                           └── dist-cjs/
│   │   │                               └── index.js
│   │   ├── fetch-http-handler/
│   │   │   ├── dist-cjs/
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           ├── protocol-http/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           ├── types/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           └── util-base64/
│   │   │               ├── dist-cjs/
│   │   │               │   ├── fromBase64.js
│   │   │               │   ├── index.js
│   │   │               │   └── toBase64.js
│   │   │               └── node_modules/
│   │   │                   └── @smithy/
│   │   │                       └── util-buffer-from/
│   │   │                           ├── dist-cjs/
│   │   │                           │   └── index.js
│   │   │                           └── node_modules/
│   │   │                               └── @smithy/
│   │   │                                   └── is-array-buffer/
│   │   │                                       └── dist-cjs/
│   │   │                                           └── index.js
│   │   ├── hash-node/
│   │   │   ├── dist-cjs/
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           └── util-buffer-from/
│   │   │               ├── dist-cjs/
│   │   │               │   └── index.js
│   │   │               └── node_modules/
│   │   │                   └── @smithy/
│   │   │                       └── is-array-buffer/
│   │   │                           └── dist-cjs/
│   │   │                               └── index.js
│   │   ├── is-array-buffer/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── middleware-content-length/
│   │   │   ├── dist-cjs/
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           ├── protocol-http/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           └── types/
│   │   │               └── dist-cjs/
│   │   │                   └── index.js
│   │   ├── middleware-endpoint/
│   │   │   └── dist-cjs/
│   │   │       ├── adaptors/
│   │   │       │   ├── getEndpointFromConfig.js
│   │   │       │   └── getEndpointUrlConfig.js
│   │   │       └── index.js
│   │   ├── middleware-retry/
│   │   │   ├── dist-cjs/
│   │   │   │   ├── isStreamingPayload/
│   │   │   │   │   └── isStreamingPayload.js
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           ├── protocol-http/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           ├── smithy-client/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           └── types/
│   │   │               └── dist-cjs/
│   │   │                   └── index.js
│   │   ├── middleware-serde/
│   │   │   ├── dist-cjs/
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           ├── protocol-http/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           └── types/
│   │   │               └── dist-cjs/
│   │   │                   └── index.js
│   │   ├── middleware-stack/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── node-config-provider/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── node-http-handler/
│   │   │   ├── dist-cjs/
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           ├── protocol-http/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           ├── querystring-builder/
│   │   │           │   ├── dist-cjs/
│   │   │           │   │   └── index.js
│   │   │           │   └── node_modules/
│   │   │           │       └── @smithy/
│   │   │           │           └── util-uri-escape/
│   │   │           │               └── dist-cjs/
│   │   │           │                   └── index.js
│   │   │           └── types/
│   │   │               └── dist-cjs/
│   │   │                   └── index.js
│   │   ├── property-provider/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── protocol-http/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── querystring-builder/
│   │   │   ├── dist-cjs/
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           └── util-uri-escape/
│   │   │               └── dist-cjs/
│   │   │                   └── index.js
│   │   ├── querystring-parser/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── service-error-classification/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── shared-ini-file-loader/
│   │   │   ├── dist-cjs/
│   │   │   │   ├── getHomeDir.js
│   │   │   │   ├── getSSOTokenFilepath.js
│   │   │   │   ├── getSSOTokenFromFile.js
│   │   │   │   ├── index.js
│   │   │   │   └── readFile.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           └── types/
│   │   │               └── dist-cjs/
│   │   │                   └── index.js
│   │   ├── signature-v4/
│   │   │   ├── dist-cjs/
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           ├── types/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           ├── util-middleware/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           └── util-utf8/
│   │   │               ├── dist-cjs/
│   │   │               │   └── index.js
│   │   │               └── node_modules/
│   │   │                   └── @smithy/
│   │   │                       └── util-buffer-from/
│   │   │                           └── dist-cjs/
│   │   │                               └── index.js
│   │   ├── smithy-client/
│   │   │   ├── dist-cjs/
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           ├── middleware-stack/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           └── util-stream/
│   │   │               ├── dist-cjs/
│   │   │               │   ├── getAwsChunkedEncodingStream.js
│   │   │               │   ├── index.js
│   │   │               │   └── sdk-stream-mixin.js
│   │   │               └── node_modules/
│   │   │                   └── @smithy/
│   │   │                       ├── node-http-handler/
│   │   │                       │   ├── dist-cjs/
│   │   │                       │   │   └── index.js
│   │   │                       │   └── node_modules/
│   │   │                       │       └── @smithy/
│   │   │                       │           └── querystring-builder/
│   │   │                       │               ├── dist-cjs/
│   │   │                       │               │   └── index.js
│   │   │                       │               └── node_modules/
│   │   │                       │                   └── @smithy/
│   │   │                       │                       └── util-uri-escape/
│   │   │                       │                           └── dist-cjs/
│   │   │                       │                               └── index.js
│   │   │                       └── util-utf8/
│   │   │                           └── dist-cjs/
│   │   │                               └── index.js
│   │   ├── types/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── url-parser/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── util-base64/
│   │   │   ├── dist-cjs/
│   │   │   │   ├── fromBase64.js
│   │   │   │   ├── index.js
│   │   │   │   └── toBase64.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           └── util-utf8/
│   │   │               └── dist-cjs/
│   │   │                   └── index.js
│   │   ├── util-body-length-browser/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── util-body-length-node/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── util-buffer-from/
│   │   │   ├── dist-cjs/
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           └── is-array-buffer/
│   │   │               └── dist-cjs/
│   │   │                   └── index.js
│   │   ├── util-config-provider/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── util-defaults-mode-node/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── util-endpoints/
│   │   │   ├── dist-cjs/
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           └── types/
│   │   │               └── dist-cjs/
│   │   │                   └── index.js
│   │   ├── util-hex-encoding/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── util-middleware/
│   │   │   ├── dist-cjs/
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           └── types/
│   │   │               └── dist-cjs/
│   │   │                   └── index.js
│   │   ├── util-retry/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── util-stream/
│   │   │   ├── dist-cjs/
│   │   │   │   ├── checksum/
│   │   │   │   │   ├── ChecksumStream.browser.js
│   │   │   │   │   ├── ChecksumStream.js
│   │   │   │   │   ├── createChecksumStream.browser.js
│   │   │   │   │   └── createChecksumStream.js
│   │   │   │   ├── ByteArrayCollector.js
│   │   │   │   ├── createBufferedReadable.js
│   │   │   │   ├── createBufferedReadableStream.js
│   │   │   │   ├── getAwsChunkedEncodingStream.js
│   │   │   │   ├── headStream.browser.js
│   │   │   │   ├── headStream.js
│   │   │   │   ├── index.js
│   │   │   │   ├── sdk-stream-mixin.browser.js
│   │   │   │   ├── sdk-stream-mixin.js
│   │   │   │   ├── splitStream.browser.js
│   │   │   │   ├── splitStream.js
│   │   │   │   └── stream-type-check.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           ├── fetch-http-handler/
│   │   │           │   ├── dist-cjs/
│   │   │           │   │   └── index.js
│   │   │           │   └── node_modules/
│   │   │           │       └── @smithy/
│   │   │           │           ├── protocol-http/
│   │   │           │           │   └── dist-cjs/
│   │   │           │           │       └── index.js
│   │   │           │           └── querystring-builder/
│   │   │           │               ├── dist-cjs/
│   │   │           │               │   └── index.js
│   │   │           │               └── node_modules/
│   │   │           │                   └── @smithy/
│   │   │           │                       └── util-uri-escape/
│   │   │           │                           └── dist-cjs/
│   │   │           │                               └── index.js
│   │   │           ├── types/
│   │   │           │   └── dist-cjs/
│   │   │           │       └── index.js
│   │   │           ├── util-base64/
│   │   │           │   └── dist-cjs/
│   │   │           │       ├── fromBase64.js
│   │   │           │       ├── index.js
│   │   │           │       └── toBase64.js
│   │   │           ├── util-buffer-from/
│   │   │           │   ├── dist-cjs/
│   │   │           │   │   └── index.js
│   │   │           │   └── node_modules/
│   │   │           │       └── @smithy/
│   │   │           │           └── is-array-buffer/
│   │   │           │               └── dist-cjs/
│   │   │           │                   └── index.js
│   │   │           └── util-hex-encoding/
│   │   │               └── dist-cjs/
│   │   │                   └── index.js
│   │   ├── util-uri-escape/
│   │   │   └── dist-cjs/
│   │   │       └── index.js
│   │   ├── util-utf8/
│   │   │   ├── dist-cjs/
│   │   │   │   └── index.js
│   │   │   └── node_modules/
│   │   │       └── @smithy/
│   │   │           └── util-buffer-from/
│   │   │               ├── dist-cjs/
│   │   │               │   └── index.js
│   │   │               └── node_modules/
│   │   │                   └── @smithy/
│   │   │                       └── is-array-buffer/
│   │   │                           └── dist-cjs/
│   │   │                               └── index.js
│   │   └── uuid/
│   │       └── dist-cjs/
│   │           ├── index.js
│   │           └── randomUUID.js
│   ├── @typespec/
│   │   └── ts-http-runtime/
│   │       └── dist/
│   │           └── esm/
│   │               ├── abort-controller/
│   │               │   └── AbortError.js
│   │               ├── logger/
│   │               │   ├── debug.js
│   │               │   ├── internal.js
│   │               │   ├── log.js
│   │               │   └── logger.js
│   │               ├── policies/
│   │               │   ├── agentPolicy.js
│   │               │   ├── decompressResponsePolicy.js
│   │               │   ├── defaultRetryPolicy.js
│   │               │   ├── formDataPolicy.js
│   │               │   ├── internal.js
│   │               │   ├── logPolicy.js
│   │               │   ├── multipartPolicy.js
│   │               │   ├── proxyPolicy.js
│   │               │   ├── redirectPolicy.js
│   │               │   ├── retryPolicy.js
│   │               │   └── tlsPolicy.js
│   │               ├── retryStrategies/
│   │               │   ├── exponentialRetryStrategy.js
│   │               │   └── throttlingRetryStrategy.js
│   │               ├── util/
│   │               │   ├── bytesEncoding.js
│   │               │   ├── checkEnvironment.js
│   │               │   ├── concat.js
│   │               │   ├── delay.js
│   │               │   ├── error.js
│   │               │   ├── helpers.js
│   │               │   ├── inspect.js
│   │               │   ├── internal.js
│   │               │   ├── object.js
│   │               │   ├── random.js
│   │               │   ├── sanitizer.js
│   │               │   ├── typeGuards.js
│   │               │   └── uuidUtils.js
│   │               ├── constants.js
│   │               ├── defaultHttpClient.js
│   │               ├── httpHeaders.js
│   │               ├── index.js
│   │               ├── log.js
│   │               ├── nodeHttpClient.js
│   │               ├── pipeline.js
│   │               ├── pipelineRequest.js
│   │               └── restError.js
│   ├── @xmldom/
│   │   └── xmldom/
│   │       └── lib/
│   │           ├── conventions.js
│   │           ├── dom-parser.js
│   │           ├── dom.js
│   │           ├── entities.js
│   │           ├── index.js
│   │           └── sax.js
│   ├── agent-base/
│   │   └── dist/
│   │       ├── helpers.js
│   │       └── index.js
│   ├── ajv/
│   │   └── dist/
│   │       ├── compile/
│   │       │   ├── codegen/
│   │       │   │   ├── code.js
│   │       │   │   ├── index.js
│   │       │   │   └── scope.js
│   │       │   ├── validate/
│   │       │   │   ├── applicability.js
│   │       │   │   ├── boolSchema.js
│   │       │   │   ├── dataType.js
│   │       │   │   ├── defaults.js
│   │       │   │   ├── index.js
│   │       │   │   ├── keyword.js
│   │       │   │   └── subschema.js
│   │       │   ├── errors.js
│   │       │   ├── index.js
│   │       │   ├── names.js
│   │       │   ├── ref_error.js
│   │       │   ├── resolve.js
│   │       │   ├── rules.js
│   │       │   └── util.js
│   │       ├── runtime/
│   │       │   ├── equal.js
│   │       │   ├── ucs2length.js
│   │       │   ├── uri.js
│   │       │   └── validation_error.js
│   │       ├── vocabularies/
│   │       │   ├── applicator/
│   │       │   │   ├── additionalItems.js
│   │       │   │   ├── additionalProperties.js
│   │       │   │   ├── allOf.js
│   │       │   │   ├── anyOf.js
│   │       │   │   ├── contains.js
│   │       │   │   ├── dependencies.js
│   │       │   │   ├── if.js
│   │       │   │   ├── index.js
│   │       │   │   ├── items.js
│   │       │   │   ├── items2020.js
│   │       │   │   ├── not.js
│   │       │   │   ├── oneOf.js
│   │       │   │   ├── patternProperties.js
│   │       │   │   ├── prefixItems.js
│   │       │   │   ├── properties.js
│   │       │   │   ├── propertyNames.js
│   │       │   │   └── thenElse.js
│   │       │   ├── core/
│   │       │   │   ├── id.js
│   │       │   │   ├── index.js
│   │       │   │   └── ref.js
│   │       │   ├── discriminator/
│   │       │   │   ├── index.js
│   │       │   │   └── types.js
│   │       │   ├── format/
│   │       │   │   ├── format.js
│   │       │   │   └── index.js
│   │       │   ├── validation/
│   │       │   │   ├── const.js
│   │       │   │   ├── enum.js
│   │       │   │   ├── index.js
│   │       │   │   ├── limitItems.js
│   │       │   │   ├── limitLength.js
│   │       │   │   ├── limitNumber.js
│   │       │   │   ├── limitProperties.js
│   │       │   │   ├── multipleOf.js
│   │       │   │   ├── pattern.js
│   │       │   │   ├── required.js
│   │       │   │   └── uniqueItems.js
│   │       │   ├── code.js
│   │       │   ├── draft7.js
│   │       │   └── metadata.js
│   │       ├── ajv.js
│   │       └── core.js
│   ├── ajv-formats/
│   │   └── dist/
│   │       ├── formats.js
│   │       ├── index.js
│   │       └── limit.js
│   ├── ansi-regex/
│   │   └── index.js
│   ├── ansi-styles/
│   │   └── index.js
│   ├── asciichart/
│   │   └── asciichart.js
│   ├── asynckit/
│   │   ├── lib/
│   │   │   ├── abort.js
│   │   │   ├── async.js
│   │   │   ├── defer.js
│   │   │   ├── iterate.js
│   │   │   ├── state.js
│   │   │   └── terminator.js
│   │   ├── index.js
│   │   ├── parallel.js
│   │   ├── serial.js
│   │   └── serialOrdered.js
│   ├── auto-bind/
│   │   └── index.js
│   ├── axios/
│   │   ├── lib/
│   │   │   ├── adapters/
│   │   │   │   ├── adapters.js
│   │   │   │   ├── fetch.js
│   │   │   │   ├── http.js
│   │   │   │   └── xhr.js
│   │   │   ├── cancel/
│   │   │   │   ├── CanceledError.js
│   │   │   │   ├── CancelToken.js
│   │   │   │   └── isCancel.js
│   │   │   ├── core/
│   │   │   │   ├── Axios.js
│   │   │   │   ├── AxiosError.js
│   │   │   │   ├── AxiosHeaders.js
│   │   │   │   ├── buildFullPath.js
│   │   │   │   ├── dispatchRequest.js
│   │   │   │   ├── InterceptorManager.js
│   │   │   │   ├── mergeConfig.js
│   │   │   │   ├── settle.js
│   │   │   │   └── transformData.js
│   │   │   ├── defaults/
│   │   │   │   ├── index.js
│   │   │   │   └── transitional.js
│   │   │   ├── env/
│   │   │   │   └── data.js
│   │   │   ├── helpers/
│   │   │   │   ├── AxiosTransformStream.js
│   │   │   │   ├── AxiosURLSearchParams.js
│   │   │   │   ├── bind.js
│   │   │   │   ├── buildURL.js
│   │   │   │   ├── callbackify.js
│   │   │   │   ├── combineURLs.js
│   │   │   │   ├── composeSignals.js
│   │   │   │   ├── cookies.js
│   │   │   │   ├── estimateDataURLDecodedBytes.js
│   │   │   │   ├── formDataToJSON.js
│   │   │   │   ├── formDataToStream.js
│   │   │   │   ├── fromDataURI.js
│   │   │   │   ├── HttpStatusCode.js
│   │   │   │   ├── isAbsoluteURL.js
│   │   │   │   ├── isAxiosError.js
│   │   │   │   ├── isURLSameOrigin.js
│   │   │   │   ├── parseHeaders.js
│   │   │   │   ├── parseProtocol.js
│   │   │   │   ├── progressEventReducer.js
│   │   │   │   ├── readBlob.js
│   │   │   │   ├── resolveConfig.js
│   │   │   │   ├── speedometer.js
│   │   │   │   ├── spread.js
│   │   │   │   ├── throttle.js
│   │   │   │   ├── toFormData.js
│   │   │   │   ├── toURLEncodedForm.js
│   │   │   │   ├── trackStream.js
│   │   │   │   ├── validator.js
│   │   │   │   └── ZlibHeaderTransformStream.js
│   │   │   ├── platform/
│   │   │   │   ├── common/
│   │   │   │   │   └── utils.js
│   │   │   │   ├── node/
│   │   │   │   │   ├── classes/
│   │   │   │   │   │   ├── FormData.js
│   │   │   │   │   │   └── URLSearchParams.js
│   │   │   │   │   └── index.js
│   │   │   │   └── index.js
│   │   │   ├── axios.js
│   │   │   └── utils.js
│   │   └── index.js
│   ├── base64-js/
│   │   └── index.js
│   ├── bidi-js/
│   │   └── dist/
│   │       └── bidi.js
│   ├── bignumber.js/
│   │   └── bignumber.js
│   ├── buffer-equal-constant-time/
│   │   └── index.js
│   ├── bundle-name/
│   │   └── index.js
│   ├── call-bind-apply-helpers/
│   │   ├── actualApply.js
│   │   ├── functionApply.js
│   │   ├── functionCall.js
│   │   ├── index.js
│   │   └── reflectApply.js
│   ├── chalk/
│   │   └── source/
│   │       ├── vendor/
│   │       │   ├── ansi-styles/
│   │       │   │   └── index.js
│   │       │   └── supports-color/
│   │       │       └── index.js
│   │       ├── index.js
│   │       └── utilities.js
│   ├── chokidar/
│   │   └── esm/
│   │       ├── handler.js
│   │       └── index.js
│   ├── cli-boxes/
│   │   └── index.js
│   ├── cli-highlight/
│   │   ├── dist/
│   │   │   ├── index.js
│   │   │   └── theme.js
│   │   └── node_modules/
│   │       └── chalk/
│   │           ├── node_modules/
│   │           │   ├── ansi-styles/
│   │           │   │   └── index.js
│   │           │   └── supports-color/
│   │           │       └── index.js
│   │           └── source/
│   │               ├── index.js
│   │               ├── templates.js
│   │               └── util.js
│   ├── cli-width/
│   │   └── index.js
│   ├── code-excerpt/
│   │   └── dist/
│   │       └── index.js
│   ├── color-convert/
│   │   ├── conversions.js
│   │   ├── index.js
│   │   └── route.js
│   ├── color-name/
│   │   └── index.js
│   ├── combined-stream/
│   │   └── lib/
│   │       └── combined_stream.js
│   ├── commander/
│   │   ├── lib/
│   │   │   ├── argument.js
│   │   │   ├── command.js
│   │   │   ├── error.js
│   │   │   ├── help.js
│   │   │   ├── option.js
│   │   │   └── suggestSimilar.js
│   │   └── index.js
│   ├── convert-to-spaces/
│   │   └── dist/
│   │       └── index.js
│   ├── cross-spawn/
│   │   ├── lib/
│   │   │   ├── util/
│   │   │   │   ├── escape.js
│   │   │   │   ├── readShebang.js
│   │   │   │   └── resolveCommand.js
│   │   │   ├── enoent.js
│   │   │   └── parse.js
│   │   └── index.js
│   ├── cssfilter/
│   │   └── lib/
│   │       ├── css.js
│   │       ├── default.js
│   │       ├── index.js
│   │       ├── parser.js
│   │       └── util.js
│   ├── debug/
│   │   └── src/
│   │       ├── browser.js
│   │       ├── common.js
│   │       ├── index.js
│   │       └── node.js
│   ├── default-browser/
│   │   ├── index.js
│   │   └── windows.js
│   ├── default-browser-id/
│   │   └── index.js
│   ├── define-lazy-prop/
│   │   └── index.js
│   ├── delayed-stream/
│   │   └── lib/
│   │       └── delayed_stream.js
│   ├── detect-libc/
│   │   └── lib/
│   │       ├── detect-libc.js
│   │       ├── elf.js
│   │       ├── filesystem.js
│   │       └── process.js
│   ├── diff/
│   │   └── libesm/
│   │       ├── diff/
│   │       │   ├── array.js
│   │       │   ├── base.js
│   │       │   ├── line.js
│   │       │   └── word.js
│   │       ├── patch/
│   │       │   └── create.js
│   │       ├── util/
│   │       │   └── string.js
│   │       └── index.js
│   ├── dijkstrajs/
│   │   └── dijkstra.js
│   ├── dom-mutator/
│   │   └── dist/
│   │       └── dom-mutator.cjs.production.min.js
│   ├── dunder-proto/
│   │   └── get.js
│   ├── ecdsa-sig-formatter/
│   │   └── src/
│   │       ├── ecdsa-sig-formatter.js
│   │       └── param-bytes-for-alg.js
│   ├── emoji-regex/
│   │   └── index.js
│   ├── env-paths/
│   │   └── index.js
│   ├── es-define-property/
│   │   └── index.js
│   ├── es-errors/
│   │   ├── eval.js
│   │   ├── index.js
│   │   ├── range.js
│   │   ├── ref.js
│   │   ├── syntax.js
│   │   ├── type.js
│   │   └── uri.js
│   ├── es-object-atoms/
│   │   └── index.js
│   ├── es-set-tostringtag/
│   │   └── index.js
│   ├── eventsource/
│   │   └── dist/
│   │       └── index.js
│   ├── eventsource-parser/
│   │   └── dist/
│   │       ├── index.js
│   │       └── stream.js
│   ├── execa/
│   │   ├── lib/
│   │   │   ├── command.js
│   │   │   ├── error.js
│   │   │   ├── kill.js
│   │   │   ├── pipe.js
│   │   │   ├── promise.js
│   │   │   ├── stdio.js
│   │   │   ├── stream.js
│   │   │   └── verbose.js
│   │   └── index.js
│   ├── extend/
│   │   └── index.js
│   ├── fast-deep-equal/
│   │   └── index.js
│   ├── fast-uri/
│   │   ├── lib/
│   │   │   ├── schemes.js
│   │   │   ├── scopedChars.js
│   │   │   └── utils.js
│   │   └── index.js
│   ├── figures/
│   │   └── index.js
│   ├── flora-colossus/
│   │   ├── lib/
│   │   │   ├── depTypes.js
│   │   │   ├── index.js
│   │   │   ├── nativeModuleTypes.js
│   │   │   └── Walker.js
│   │   └── node_modules/
│   │       └── fs-extra/
│   │           └── lib/
│   │               ├── copy/
│   │               │   ├── copy-sync.js
│   │               │   ├── copy.js
│   │               │   └── index.js
│   │               ├── empty/
│   │               │   └── index.js
│   │               ├── ensure/
│   │               │   ├── file.js
│   │               │   ├── index.js
│   │               │   ├── link.js
│   │               │   ├── symlink-paths.js
│   │               │   ├── symlink-type.js
│   │               │   └── symlink.js
│   │               ├── fs/
│   │               │   └── index.js
│   │               ├── json/
│   │               │   ├── index.js
│   │               │   ├── jsonfile.js
│   │               │   ├── output-json-sync.js
│   │               │   └── output-json.js
│   │               ├── mkdirs/
│   │               │   ├── index.js
│   │               │   ├── make-dir.js
│   │               │   └── utils.js
│   │               ├── move/
│   │               │   ├── index.js
│   │               │   ├── move-sync.js
│   │               │   └── move.js
│   │               ├── output-file/
│   │               │   └── index.js
│   │               ├── path-exists/
│   │               │   └── index.js
│   │               ├── remove/
│   │               │   ├── index.js
│   │               │   └── rimraf.js
│   │               ├── util/
│   │               │   ├── stat.js
│   │               │   └── utimes.js
│   │               └── index.js
│   ├── follow-redirects/
│   │   ├── debug.js
│   │   └── index.js
│   ├── form-data/
│   │   └── lib/
│   │       ├── form_data.js
│   │       └── populate.js
│   ├── function-bind/
│   │   ├── implementation.js
│   │   └── index.js
│   ├── galactus/
│   │   ├── lib/
│   │   │   ├── DestroyerOfModules.js
│   │   │   └── index.js
│   │   └── node_modules/
│   │       └── fs-extra/
│   │           └── lib/
│   │               ├── copy/
│   │               │   ├── copy-sync.js
│   │               │   ├── copy.js
│   │               │   └── index.js
│   │               ├── empty/
│   │               │   └── index.js
│   │               ├── ensure/
│   │               │   ├── file.js
│   │               │   ├── index.js
│   │               │   ├── link.js
│   │               │   ├── symlink-paths.js
│   │               │   ├── symlink-type.js
│   │               │   └── symlink.js
│   │               ├── fs/
│   │               │   └── index.js
│   │               ├── json/
│   │               │   ├── index.js
│   │               │   ├── jsonfile.js
│   │               │   ├── output-json-sync.js
│   │               │   └── output-json.js
│   │               ├── mkdirs/
│   │               │   ├── index.js
│   │               │   ├── make-dir.js
│   │               │   └── utils.js
│   │               ├── move/
│   │               │   ├── index.js
│   │               │   ├── move-sync.js
│   │               │   └── move.js
│   │               ├── output-file/
│   │               │   └── index.js
│   │               ├── path-exists/
│   │               │   └── index.js
│   │               ├── remove/
│   │               │   ├── index.js
│   │               │   └── rimraf.js
│   │               ├── util/
│   │               │   ├── stat.js
│   │               │   └── utimes.js
│   │               └── index.js
│   ├── gaxios/
│   │   ├── build/
│   │   │   └── src/
│   │   │       ├── common.js
│   │   │       ├── gaxios.js
│   │   │       ├── index.js
│   │   │       ├── interceptor.js
│   │   │       ├── retry.js
│   │   │       └── util.js
│   │   └── node_modules/
│   │       ├── is-stream/
│   │       │   └── index.js
│   │       └── uuid/
│   │           └── dist/
│   │               ├── index.js
│   │               ├── md5.js
│   │               ├── native.js
│   │               ├── nil.js
│   │               ├── parse.js
│   │               ├── regex.js
│   │               ├── rng.js
│   │               ├── sha1.js
│   │               ├── stringify.js
│   │               ├── v1.js
│   │               ├── v3.js
│   │               ├── v35.js
│   │               ├── v4.js
│   │               ├── v5.js
│   │               ├── validate.js
│   │               └── version.js
│   ├── gcp-metadata/
│   │   └── build/
│   │       └── src/
│   │           ├── gcp-residency.js
│   │           └── index.js
│   ├── get-east-asian-width/
│   │   ├── index.js
│   │   └── lookup.js
│   ├── get-intrinsic/
│   │   └── index.js
│   ├── get-proto/
│   │   ├── index.js
│   │   ├── Object.getPrototypeOf.js
│   │   └── Reflect.getPrototypeOf.js
│   ├── get-stream/
│   │   └── source/
│   │       ├── array-buffer.js
│   │       ├── array.js
│   │       ├── buffer.js
│   │       ├── contents.js
│   │       ├── index.js
│   │       ├── string.js
│   │       └── utils.js
│   ├── google-auth-library/
│   │   └── build/
│   │       └── src/
│   │           ├── auth/
│   │           │   ├── authclient.js
│   │           │   ├── awsclient.js
│   │           │   ├── awsrequestsigner.js
│   │           │   ├── baseexternalclient.js
│   │           │   ├── computeclient.js
│   │           │   ├── defaultawssecuritycredentialssupplier.js
│   │           │   ├── downscopedclient.js
│   │           │   ├── envDetect.js
│   │           │   ├── executable-response.js
│   │           │   ├── externalAccountAuthorizedUserClient.js
│   │           │   ├── externalclient.js
│   │           │   ├── filesubjecttokensupplier.js
│   │           │   ├── googleauth.js
│   │           │   ├── iam.js
│   │           │   ├── identitypoolclient.js
│   │           │   ├── idtokenclient.js
│   │           │   ├── impersonated.js
│   │           │   ├── jwtaccess.js
│   │           │   ├── jwtclient.js
│   │           │   ├── loginticket.js
│   │           │   ├── oauth2client.js
│   │           │   ├── oauth2common.js
│   │           │   ├── passthrough.js
│   │           │   ├── pluggable-auth-client.js
│   │           │   ├── pluggable-auth-handler.js
│   │           │   ├── refreshclient.js
│   │           │   ├── stscredentials.js
│   │           │   └── urlsubjecttokensupplier.js
│   │           ├── crypto/
│   │           │   ├── browser/
│   │           │   │   └── crypto.js
│   │           │   ├── node/
│   │           │   │   └── crypto.js
│   │           │   └── crypto.js
│   │           ├── index.js
│   │           ├── options.js
│   │           ├── transporters.js
│   │           └── util.js
│   ├── google-logging-utils/
│   │   └── build/
│   │       └── src/
│   │           ├── colours.js
│   │           ├── index.js
│   │           └── logging-utils.js
│   ├── gopd/
│   │   ├── gOPD.js
│   │   └── index.js
│   ├── graceful-fs/
│   │   ├── clone.js
│   │   ├── graceful-fs.js
│   │   ├── legacy-streams.js
│   │   └── polyfills.js
│   ├── gtoken/
│   │   └── build/
│   │       └── src/
│   │           └── index.js
│   ├── has-flag/
│   │   └── index.js
│   ├── has-symbols/
│   │   ├── index.js
│   │   └── shams.js
│   ├── has-tostringtag/
│   │   └── shams.js
│   ├── hasown/
│   │   └── index.js
│   ├── highlight.js/
│   │   └── lib/
│   │       ├── languages/
│   │       │   ├── 1c.js
│   │       │   ├── abnf.js
│   │       │   ├── accesslog.js
│   │       │   ├── actionscript.js
│   │       │   ├── ada.js
│   │       │   ├── angelscript.js
│   │       │   ├── apache.js
│   │       │   ├── applescript.js
│   │       │   ├── arcade.js
│   │       │   ├── arduino.js
│   │       │   ├── armasm.js
│   │       │   ├── asciidoc.js
│   │       │   ├── aspectj.js
│   │       │   ├── autohotkey.js
│   │       │   ├── autoit.js
│   │       │   ├── avrasm.js
│   │       │   ├── awk.js
│   │       │   ├── axapta.js
│   │       │   ├── bash.js
│   │       │   ├── basic.js
│   │       │   ├── bnf.js
│   │       │   ├── brainfuck.js
│   │       │   ├── c-like.js
│   │       │   ├── c.js
│   │       │   ├── cal.js
│   │       │   ├── capnproto.js
│   │       │   ├── ceylon.js
│   │       │   ├── clean.js
│   │       │   ├── clojure-repl.js
│   │       │   ├── clojure.js
│   │       │   ├── cmake.js
│   │       │   ├── coffeescript.js
│   │       │   ├── coq.js
│   │       │   ├── cos.js
│   │       │   ├── cpp.js
│   │       │   ├── crmsh.js
│   │       │   ├── crystal.js
│   │       │   ├── csharp.js
│   │       │   ├── csp.js
│   │       │   ├── css.js
│   │       │   ├── d.js
│   │       │   ├── dart.js
│   │       │   ├── delphi.js
│   │       │   ├── diff.js
│   │       │   ├── django.js
│   │       │   ├── dns.js
│   │       │   ├── dockerfile.js
│   │       │   ├── dos.js
│   │       │   ├── dsconfig.js
│   │       │   ├── dts.js
│   │       │   ├── dust.js
│   │       │   ├── ebnf.js
│   │       │   ├── elixir.js
│   │       │   ├── elm.js
│   │       │   ├── erb.js
│   │       │   ├── erlang-repl.js
│   │       │   ├── erlang.js
│   │       │   ├── excel.js
│   │       │   ├── fix.js
│   │       │   ├── flix.js
│   │       │   ├── fortran.js
│   │       │   ├── fsharp.js
│   │       │   ├── gams.js
│   │       │   ├── gauss.js
│   │       │   ├── gcode.js
│   │       │   ├── gherkin.js
│   │       │   ├── glsl.js
│   │       │   ├── gml.js
│   │       │   ├── go.js
│   │       │   ├── golo.js
│   │       │   ├── gradle.js
│   │       │   ├── groovy.js
│   │       │   ├── haml.js
│   │       │   ├── handlebars.js
│   │       │   ├── haskell.js
│   │       │   ├── haxe.js
│   │       │   ├── hsp.js
│   │       │   ├── htmlbars.js
│   │       │   ├── http.js
│   │       │   ├── hy.js
│   │       │   ├── inform7.js
│   │       │   ├── ini.js
│   │       │   ├── irpf90.js
│   │       │   ├── isbl.js
│   │       │   ├── java.js
│   │       │   ├── javascript.js
│   │       │   ├── jboss-cli.js
│   │       │   ├── json.js
│   │       │   ├── julia-repl.js
│   │       │   ├── julia.js
│   │       │   ├── kotlin.js
│   │       │   ├── lasso.js
│   │       │   ├── latex.js
│   │       │   ├── ldif.js
│   │       │   ├── leaf.js
│   │       │   ├── less.js
│   │       │   ├── lisp.js
│   │       │   ├── livecodeserver.js
│   │       │   ├── livescript.js
│   │       │   ├── llvm.js
│   │       │   ├── lsl.js
│   │       │   ├── lua.js
│   │       │   ├── makefile.js
│   │       │   ├── markdown.js
│   │       │   ├── mathematica.js
│   │       │   ├── matlab.js
│   │       │   ├── maxima.js
│   │       │   ├── mel.js
│   │       │   ├── mercury.js
│   │       │   ├── mipsasm.js
│   │       │   ├── mizar.js
│   │       │   ├── mojolicious.js
│   │       │   ├── monkey.js
│   │       │   ├── moonscript.js
│   │       │   ├── n1ql.js
│   │       │   ├── nginx.js
│   │       │   ├── nim.js
│   │       │   ├── nix.js
│   │       │   ├── node-repl.js
│   │       │   ├── nsis.js
│   │       │   ├── objectivec.js
│   │       │   ├── ocaml.js
│   │       │   ├── openscad.js
│   │       │   ├── oxygene.js
│   │       │   ├── parser3.js
│   │       │   ├── perl.js
│   │       │   ├── pf.js
│   │       │   ├── pgsql.js
│   │       │   ├── php-template.js
│   │       │   ├── php.js
│   │       │   ├── plaintext.js
│   │       │   ├── pony.js
│   │       │   ├── powershell.js
│   │       │   ├── processing.js
│   │       │   ├── profile.js
│   │       │   ├── prolog.js
│   │       │   ├── properties.js
│   │       │   ├── protobuf.js
│   │       │   ├── puppet.js
│   │       │   ├── purebasic.js
│   │       │   ├── python-repl.js
│   │       │   ├── python.js
│   │       │   ├── q.js
│   │       │   ├── qml.js
│   │       │   ├── r.js
│   │       │   ├── reasonml.js
│   │       │   ├── rib.js
│   │       │   ├── roboconf.js
│   │       │   ├── routeros.js
│   │       │   ├── rsl.js
│   │       │   ├── ruby.js
│   │       │   ├── ruleslanguage.js
│   │       │   ├── rust.js
│   │       │   ├── sas.js
│   │       │   ├── scala.js
│   │       │   ├── scheme.js
│   │       │   ├── scilab.js
│   │       │   ├── scss.js
│   │       │   ├── shell.js
│   │       │   ├── smali.js
│   │       │   ├── smalltalk.js
│   │       │   ├── sml.js
│   │       │   ├── sqf.js
│   │       │   ├── sql_more.js
│   │       │   ├── sql.js
│   │       │   ├── stan.js
│   │       │   ├── stata.js
│   │       │   ├── step21.js
│   │       │   ├── stylus.js
│   │       │   ├── subunit.js
│   │       │   ├── swift.js
│   │       │   ├── taggerscript.js
│   │       │   ├── tap.js
│   │       │   ├── tcl.js
│   │       │   ├── thrift.js
│   │       │   ├── tp.js
│   │       │   ├── twig.js
│   │       │   ├── typescript.js
│   │       │   ├── vala.js
│   │       │   ├── vbnet.js
│   │       │   ├── vbscript-html.js
│   │       │   ├── vbscript.js
│   │       │   ├── verilog.js
│   │       │   ├── vhdl.js
│   │       │   ├── vim.js
│   │       │   ├── x86asm.js
│   │       │   ├── xl.js
│   │       │   ├── xml.js
│   │       │   ├── xquery.js
│   │       │   ├── yaml.js
│   │       │   └── zephir.js
│   │       ├── core.js
│   │       └── index.js
│   ├── http-proxy-agent/
│   │   └── dist/
│   │       └── index.js
│   ├── https-proxy-agent/
│   │   └── dist/
│   │       ├── index.js
│   │       └── parse-proxy-response.js
│   ├── human-signals/
│   │   └── build/
│   │       └── src/
│   │           ├── core.js
│   │           ├── main.js
│   │           ├── realtime.js
│   │           └── signals.js
│   ├── ignore/
│   │   └── index.js
│   ├── indent-string/
│   │   └── index.js
│   ├── is-docker/
│   │   └── index.js
│   ├── is-fullwidth-code-point/
│   │   └── index.js
│   ├── is-inside-container/
│   │   └── index.js
│   ├── is-stream/
│   │   └── index.js
│   ├── is-unicode-supported/
│   │   └── index.js
│   ├── is-wsl/
│   │   └── index.js
│   ├── isexe/
│   │   ├── index.js
│   │   ├── mode.js
│   │   └── windows.js
│   ├── json-bigint/
│   │   ├── lib/
│   │   │   ├── parse.js
│   │   │   └── stringify.js
│   │   └── index.js
│   ├── json-schema-traverse/
│   │   └── index.js
│   ├── jsonc-parser/
│   │   └── lib/
│   │       └── esm/
│   │           ├── impl/
│   │           │   ├── edit.js
│   │           │   ├── format.js
│   │           │   ├── parser.js
│   │           │   ├── scanner.js
│   │           │   └── string-intern.js
│   │           └── main.js
│   ├── jsonfile/
│   │   ├── index.js
│   │   └── utils.js
│   ├── jsonwebtoken/
│   │   ├── lib/
│   │   │   ├── asymmetricKeyDetailsSupported.js
│   │   │   ├── JsonWebTokenError.js
│   │   │   ├── NotBeforeError.js
│   │   │   ├── psSupported.js
│   │   │   ├── rsaPssKeyDetailsSupported.js
│   │   │   ├── timespan.js
│   │   │   ├── TokenExpiredError.js
│   │   │   └── validateAsymmetricKey.js
│   │   ├── node_modules/
│   │   │   └── semver/
│   │   │       ├── classes/
│   │   │       │   ├── comparator.js
│   │   │       │   ├── range.js
│   │   │       │   └── semver.js
│   │   │       ├── functions/
│   │   │       │   ├── clean.js
│   │   │       │   ├── cmp.js
│   │   │       │   ├── coerce.js
│   │   │       │   ├── compare-build.js
│   │   │       │   ├── compare-loose.js
│   │   │       │   ├── compare.js
│   │   │       │   ├── diff.js
│   │   │       │   ├── eq.js
│   │   │       │   ├── gt.js
│   │   │       │   ├── gte.js
│   │   │       │   ├── inc.js
│   │   │       │   ├── lt.js
│   │   │       │   ├── lte.js
│   │   │       │   ├── major.js
│   │   │       │   ├── minor.js
│   │   │       │   ├── neq.js
│   │   │       │   ├── parse.js
│   │   │       │   ├── patch.js
│   │   │       │   ├── prerelease.js
│   │   │       │   ├── rcompare.js
│   │   │       │   ├── rsort.js
│   │   │       │   ├── satisfies.js
│   │   │       │   ├── sort.js
│   │   │       │   └── valid.js
│   │   │       ├── internal/
│   │   │       │   ├── constants.js
│   │   │       │   ├── debug.js
│   │   │       │   ├── identifiers.js
│   │   │       │   ├── lrucache.js
│   │   │       │   ├── parse-options.js
│   │   │       │   └── re.js
│   │   │       ├── ranges/
│   │   │       │   ├── gtr.js
│   │   │       │   ├── intersects.js
│   │   │       │   ├── ltr.js
│   │   │       │   ├── max-satisfying.js
│   │   │       │   ├── min-satisfying.js
│   │   │       │   ├── min-version.js
│   │   │       │   ├── outside.js
│   │   │       │   ├── simplify.js
│   │   │       │   ├── subset.js
│   │   │       │   ├── to-comparators.js
│   │   │       │   └── valid.js
│   │   │       └── index.js
│   │   ├── decode.js
│   │   ├── index.js
│   │   ├── sign.js
│   │   └── verify.js
│   ├── jwa/
│   │   └── index.js
│   ├── jws/
│   │   ├── lib/
│   │   │   ├── data-stream.js
│   │   │   ├── sign-stream.js
│   │   │   ├── tostring.js
│   │   │   └── verify-stream.js
│   │   └── index.js
│   ├── lodash-es/
│   │   ├── _apply.js
│   │   ├── _arrayAggregator.js
│   │   ├── _arrayEach.js
│   │   ├── _arrayFilter.js
│   │   ├── _arrayIncludes.js
│   │   ├── _arrayIncludesWith.js
│   │   ├── _arrayLikeKeys.js
│   │   ├── _arrayMap.js
│   │   ├── _arrayPush.js
│   │   ├── _arraySample.js
│   │   ├── _arraySome.js
│   │   ├── _asciiToArray.js
│   │   ├── _assignMergeValue.js
│   │   ├── _assignValue.js
│   │   ├── _assocIndexOf.js
│   │   ├── _baseAggregator.js
│   │   ├── _baseAssign.js
│   │   ├── _baseAssignIn.js
│   │   ├── _baseAssignValue.js
│   │   ├── _baseClone.js
│   │   ├── _baseCreate.js
│   │   ├── _baseEach.js
│   │   ├── _baseFilter.js
│   │   ├── _baseFindIndex.js
│   │   ├── _baseFlatten.js
│   │   ├── _baseFor.js
│   │   ├── _baseForOwn.js
│   │   ├── _baseGet.js
│   │   ├── _baseGetAllKeys.js
│   │   ├── _baseGetTag.js
│   │   ├── _baseHasIn.js
│   │   ├── _baseIndexOf.js
│   │   ├── _baseIsArguments.js
│   │   ├── _baseIsEqual.js
│   │   ├── _baseIsEqualDeep.js
│   │   ├── _baseIsMap.js
│   │   ├── _baseIsMatch.js
│   │   ├── _baseIsNaN.js
│   │   ├── _baseIsNative.js
│   │   ├── _baseIsSet.js
│   │   ├── _baseIsTypedArray.js
│   │   ├── _baseIteratee.js
│   │   ├── _baseKeys.js
│   │   ├── _baseKeysIn.js
│   │   ├── _baseMatches.js
│   │   ├── _baseMatchesProperty.js
│   │   ├── _baseMerge.js
│   │   ├── _baseMergeDeep.js
│   │   ├── _basePickBy.js
│   │   ├── _baseProperty.js
│   │   ├── _basePropertyDeep.js
│   │   ├── _baseRandom.js
│   │   ├── _baseRest.js
│   │   ├── _baseSample.js
│   │   ├── _baseSet.js
│   │   ├── _baseSetToString.js
│   │   ├── _baseSlice.js
│   │   ├── _baseSum.js
│   │   ├── _baseTimes.js
│   │   ├── _baseToString.js
│   │   ├── _baseTrim.js
│   │   ├── _baseUnary.js
│   │   ├── _baseUniq.js
│   │   ├── _baseUnset.js
│   │   ├── _baseValues.js
│   │   ├── _baseZipObject.js
│   │   ├── _cacheHas.js
│   │   ├── _castPath.js
│   │   ├── _castSlice.js
│   │   ├── _cloneArrayBuffer.js
│   │   ├── _cloneBuffer.js
│   │   ├── _cloneDataView.js
│   │   ├── _cloneRegExp.js
│   │   ├── _cloneSymbol.js
│   │   ├── _cloneTypedArray.js
│   │   ├── _copyArray.js
│   │   ├── _copyObject.js
│   │   ├── _copySymbols.js
│   │   ├── _copySymbolsIn.js
│   │   ├── _coreJsData.js
│   │   ├── _createAggregator.js
│   │   ├── _createAssigner.js
│   │   ├── _createBaseEach.js
│   │   ├── _createBaseFor.js
│   │   ├── _createCaseFirst.js
│   │   ├── _createSet.js
│   │   ├── _customOmitClone.js
│   │   ├── _DataView.js
│   │   ├── _defineProperty.js
│   │   ├── _equalArrays.js
│   │   ├── _equalByTag.js
│   │   ├── _equalObjects.js
│   │   ├── _flatRest.js
│   │   ├── _freeGlobal.js
│   │   ├── _getAllKeys.js
│   │   ├── _getAllKeysIn.js
│   │   ├── _getMapData.js
│   │   ├── _getMatchData.js
│   │   ├── _getNative.js
│   │   ├── _getPrototype.js
│   │   ├── _getRawTag.js
│   │   ├── _getSymbols.js
│   │   ├── _getSymbolsIn.js
│   │   ├── _getTag.js
│   │   ├── _getValue.js
│   │   ├── _Hash.js
│   │   ├── _hashClear.js
│   │   ├── _hashDelete.js
│   │   ├── _hashGet.js
│   │   ├── _hashHas.js
│   │   ├── _hashSet.js
│   │   ├── _hasPath.js
│   │   ├── _hasUnicode.js
│   │   ├── _initCloneArray.js
│   │   ├── _initCloneByTag.js
│   │   ├── _initCloneObject.js
│   │   ├── _isFlattenable.js
│   │   ├── _isIndex.js
│   │   ├── _isIterateeCall.js
│   │   ├── _isKey.js
│   │   ├── _isKeyable.js
│   │   ├── _isMasked.js
│   │   ├── _isPrototype.js
│   │   ├── _isStrictComparable.js
│   │   ├── _ListCache.js
│   │   ├── _listCacheClear.js
│   │   ├── _listCacheDelete.js
│   │   ├── _listCacheGet.js
│   │   ├── _listCacheHas.js
│   │   ├── _listCacheSet.js
│   │   ├── _Map.js
│   │   ├── _MapCache.js
│   │   ├── _mapCacheClear.js
│   │   ├── _mapCacheDelete.js
│   │   ├── _mapCacheGet.js
│   │   ├── _mapCacheHas.js
│   │   ├── _mapCacheSet.js
│   │   ├── _mapToArray.js
│   │   ├── _matchesStrictComparable.js
│   │   ├── _memoizeCapped.js
│   │   ├── _nativeCreate.js
│   │   ├── _nativeKeys.js
│   │   ├── _nativeKeysIn.js
│   │   ├── _nodeUtil.js
│   │   ├── _objectToString.js
│   │   ├── _overArg.js
│   │   ├── _overRest.js
│   │   ├── _parent.js
│   │   ├── _Promise.js
│   │   ├── _root.js
│   │   ├── _safeGet.js
│   │   ├── _Set.js
│   │   ├── _SetCache.js
│   │   ├── _setCacheAdd.js
│   │   ├── _setCacheHas.js
│   │   ├── _setToArray.js
│   │   ├── _setToString.js
│   │   ├── _shortOut.js
│   │   ├── _Stack.js
│   │   ├── _stackClear.js
│   │   ├── _stackDelete.js
│   │   ├── _stackGet.js
│   │   ├── _stackHas.js
│   │   ├── _stackSet.js
│   │   ├── _strictIndexOf.js
│   │   ├── _stringToArray.js
│   │   ├── _stringToPath.js
│   │   ├── _Symbol.js
│   │   ├── _toKey.js
│   │   ├── _toSource.js
│   │   ├── _trimmedEndIndex.js
│   │   ├── _Uint8Array.js
│   │   ├── _unicodeToArray.js
│   │   ├── _WeakMap.js
│   │   ├── capitalize.js
│   │   ├── cloneDeep.js
│   │   ├── constant.js
│   │   ├── debounce.js
│   │   ├── eq.js
│   │   ├── flatten.js
│   │   ├── get.js
│   │   ├── hasIn.js
│   │   ├── identity.js
│   │   ├── isArguments.js
│   │   ├── isArray.js
│   │   ├── isArrayLike.js
│   │   ├── isArrayLikeObject.js
│   │   ├── isBuffer.js
│   │   ├── isEqual.js
│   │   ├── isFunction.js
│   │   ├── isLength.js
│   │   ├── isMap.js
│   │   ├── isObject.js
│   │   ├── isObjectLike.js
│   │   ├── isPlainObject.js
│   │   ├── isSet.js
│   │   ├── isSymbol.js
│   │   ├── isTypedArray.js
│   │   ├── keys.js
│   │   ├── keysIn.js
│   │   ├── last.js
│   │   ├── lodash.js
│   │   ├── mapValues.js
│   │   ├── memoize.js
│   │   ├── mergeWith.js
│   │   ├── negate.js
│   │   ├── noop.js
│   │   ├── now.js
│   │   ├── omit.js
│   │   ├── partition.js
│   │   ├── pickBy.js
│   │   ├── property.js
│   │   ├── reject.js
│   │   ├── sample.js
│   │   ├── setWith.js
│   │   ├── stubArray.js
│   │   ├── stubFalse.js
│   │   ├── sumBy.js
│   │   ├── throttle.js
│   │   ├── toNumber.js
│   │   ├── toPlainObject.js
│   │   ├── toString.js
│   │   ├── uniqBy.js
│   │   ├── upperFirst.js
│   │   ├── values.js
│   │   └── zipObject.js
│   ├── lodash.camelcase/
│   │   └── index.js
│   ├── lodash.debounce/
│   │   └── index.js
│   ├── lodash.includes/
│   │   └── index.js
│   ├── lodash.isboolean/
│   │   └── index.js
│   ├── lodash.isinteger/
│   │   └── index.js
│   ├── lodash.isnumber/
│   │   └── index.js
│   ├── lodash.isplainobject/
│   │   └── index.js
│   ├── lodash.isstring/
│   │   └── index.js
│   ├── lodash.once/
│   │   └── index.js
│   ├── long/
│   │   └── umd/
│   │       └── index.js
│   ├── lru-cache/
│   │   └── dist/
│   │       └── esm/
│   │           └── index.js
│   ├── marked/
│   │   └── lib/
│   │       └── marked.esm.js
│   ├── math-intrinsics/
│   │   ├── abs.js
│   │   ├── floor.js
│   │   ├── isNaN.js
│   │   ├── max.js
│   │   ├── min.js
│   │   ├── pow.js
│   │   ├── round.js
│   │   └── sign.js
│   ├── merge-stream/
│   │   └── index.js
│   ├── mime-types/
│   │   └── index.js
│   ├── mimic-fn/
│   │   └── index.js
│   ├── ms/
│   │   └── index.js
│   ├── node-fetch/
│   │   └── lib/
│   │       └── index.js
│   ├── node-forge/
│   │   └── lib/
│   │       ├── aes.js
│   │       ├── aesCipherSuites.js
│   │       ├── asn1-validator.js
│   │       ├── asn1.js
│   │       ├── baseN.js
│   │       ├── cipher.js
│   │       ├── cipherModes.js
│   │       ├── des.js
│   │       ├── ed25519.js
│   │       ├── forge.js
│   │       ├── hmac.js
│   │       ├── index.js
│   │       ├── jsbn.js
│   │       ├── kem.js
│   │       ├── log.js
│   │       ├── md.all.js
│   │       ├── md.js
│   │       ├── md5.js
│   │       ├── mgf.js
│   │       ├── mgf1.js
│   │       ├── oids.js
│   │       ├── pbe.js
│   │       ├── pbkdf2.js
│   │       ├── pem.js
│   │       ├── pkcs1.js
│   │       ├── pkcs12.js
│   │       ├── pkcs7.js
│   │       ├── pkcs7asn1.js
│   │       ├── pki.js
│   │       ├── prime.js
│   │       ├── prng.js
│   │       ├── pss.js
│   │       ├── random.js
│   │       ├── rc2.js
│   │       ├── rsa.js
│   │       ├── sha1.js
│   │       ├── sha256.js
│   │       ├── sha512.js
│   │       ├── ssh.js
│   │       ├── tls.js
│   │       ├── util.js
│   │       └── x509.js
│   ├── npm-run-path/
│   │   ├── node_modules/
│   │   │   └── path-key/
│   │   │       └── index.js
│   │   └── index.js
│   ├── onetime/
│   │   └── index.js
│   ├── open/
│   │   └── index.js
│   ├── p-map/
│   │   └── index.js
│   ├── parse5/
│   │   └── lib/
│   │       ├── common/
│   │       │   ├── doctype.js
│   │       │   ├── error-codes.js
│   │       │   ├── foreign-content.js
│   │       │   ├── html.js
│   │       │   └── unicode.js
│   │       ├── extensions/
│   │       │   ├── error-reporting/
│   │       │   │   ├── mixin-base.js
│   │       │   │   ├── parser-mixin.js
│   │       │   │   ├── preprocessor-mixin.js
│   │       │   │   └── tokenizer-mixin.js
│   │       │   ├── location-info/
│   │       │   │   ├── open-element-stack-mixin.js
│   │       │   │   ├── parser-mixin.js
│   │       │   │   └── tokenizer-mixin.js
│   │       │   └── position-tracking/
│   │       │       └── preprocessor-mixin.js
│   │       ├── parser/
│   │       │   ├── formatting-element-list.js
│   │       │   ├── index.js
│   │       │   └── open-element-stack.js
│   │       ├── serializer/
│   │       │   └── index.js
│   │       ├── tokenizer/
│   │       │   ├── index.js
│   │       │   ├── named-entity-data.js
│   │       │   └── preprocessor.js
│   │       ├── tree-adapters/
│   │       │   └── default.js
│   │       ├── utils/
│   │       │   ├── merge-options.js
│   │       │   └── mixin.js
│   │       └── index.js
│   ├── parse5-htmlparser2-tree-adapter/
│   │   ├── lib/
│   │   │   └── index.js
│   │   └── node_modules/
│   │       └── parse5/
│   │           └── lib/
│   │               └── common/
│   │                   ├── doctype.js
│   │                   └── html.js
│   ├── path-key/
│   │   └── index.js
│   ├── picomatch/
│   │   ├── lib/
│   │   │   ├── constants.js
│   │   │   ├── parse.js
│   │   │   ├── picomatch.js
│   │   │   ├── scan.js
│   │   │   └── utils.js
│   │   └── index.js
│   ├── pkce-challenge/
│   │   └── dist/
│   │       └── index.node.js
│   ├── plist/
│   │   ├── lib/
│   │   │   ├── build.js
│   │   │   └── parse.js
│   │   └── index.js
│   ├── pngjs/
│   │   └── lib/
│   │       ├── bitmapper.js
│   │       ├── bitpacker.js
│   │       ├── chunkstream.js
│   │       ├── constants.js
│   │       ├── crc.js
│   │       ├── filter-pack.js
│   │       ├── filter-parse-async.js
│   │       ├── filter-parse-sync.js
│   │       ├── filter-parse.js
│   │       ├── format-normaliser.js
│   │       ├── interlace.js
│   │       ├── packer-async.js
│   │       ├── packer-sync.js
│   │       ├── packer.js
│   │       ├── paeth-predictor.js
│   │       ├── parser-async.js
│   │       ├── parser-sync.js
│   │       ├── parser.js
│   │       ├── png-sync.js
│   │       ├── png.js
│   │       ├── sync-inflate.js
│   │       └── sync-reader.js
│   ├── pretty-bytes/
│   │   └── index.js
│   ├── proper-lockfile/
│   │   ├── lib/
│   │   │   ├── adapter.js
│   │   │   ├── lockfile.js
│   │   │   └── mtime-precision.js
│   │   ├── node_modules/
│   │   │   └── signal-exit/
│   │   │       ├── index.js
│   │   │       └── signals.js
│   │   └── index.js
│   ├── protobufjs/
│   │   ├── ext/
│   │   │   └── descriptor/
│   │   │       └── index.js
│   │   └── src/
│   │       ├── rpc/
│   │       │   └── service.js
│   │       ├── util/
│   │       │   ├── longbits.js
│   │       │   └── minimal.js
│   │       ├── common.js
│   │       ├── converter.js
│   │       ├── decoder.js
│   │       ├── encoder.js
│   │       ├── enum.js
│   │       ├── field.js
│   │       ├── index-light.js
│   │       ├── index-minimal.js
│   │       ├── index.js
│   │       ├── mapfield.js
│   │       ├── message.js
│   │       ├── method.js
│   │       ├── namespace.js
│   │       ├── object.js
│   │       ├── oneof.js
│   │       ├── parse.js
│   │       ├── reader_buffer.js
│   │       ├── reader.js
│   │       ├── root.js
│   │       ├── roots.js
│   │       ├── rpc.js
│   │       ├── service.js
│   │       ├── tokenize.js
│   │       ├── type.js
│   │       ├── types.js
│   │       ├── util.js
│   │       ├── verifier.js
│   │       ├── wrappers.js
│   │       ├── writer_buffer.js
│   │       └── writer.js
│   ├── proxy-from-env/
│   │   └── index.js
│   ├── punycode/
│   │   └── punycode.js
│   ├── qrcode/
│   │   └── lib/
│   │       ├── core/
│   │       │   ├── alignment-pattern.js
│   │       │   ├── alphanumeric-data.js
│   │       │   ├── bit-buffer.js
│   │       │   ├── bit-matrix.js
│   │       │   ├── byte-data.js
│   │       │   ├── error-correction-code.js
│   │       │   ├── error-correction-level.js
│   │       │   ├── finder-pattern.js
│   │       │   ├── format-info.js
│   │       │   ├── galois-field.js
│   │       │   ├── kanji-data.js
│   │       │   ├── mask-pattern.js
│   │       │   ├── mode.js
│   │       │   ├── numeric-data.js
│   │       │   ├── polynomial.js
│   │       │   ├── qrcode.js
│   │       │   ├── reed-solomon-encoder.js
│   │       │   ├── regex.js
│   │       │   ├── segments.js
│   │       │   ├── utils.js
│   │       │   ├── version-check.js
│   │       │   └── version.js
│   │       ├── renderer/
│   │       │   ├── terminal/
│   │       │   │   ├── terminal-small.js
│   │       │   │   └── terminal.js
│   │       │   ├── canvas.js
│   │       │   ├── png.js
│   │       │   ├── svg-tag.js
│   │       │   ├── svg.js
│   │       │   ├── terminal.js
│   │       │   ├── utf8.js
│   │       │   └── utils.js
│   │       ├── browser.js
│   │       ├── can-promise.js
│   │       └── server.js
│   ├── react/
│   │   └── cjs/
│   │       ├── react-compiler-runtime.production.js
│   │       └── react.production.js
│   ├── react-reconciler/
│   │   ├── cjs/
│   │   │   ├── react-reconciler-constants.production.js
│   │   │   └── react-reconciler.production.js
│   │   └── node_modules/
│   │       └── scheduler/
│   │           └── cjs/
│   │               └── scheduler.production.js
│   ├── readdirp/
│   │   └── esm/
│   │       └── index.js
│   ├── retry/
│   │   └── lib/
│   │       ├── retry_operation.js
│   │       └── retry.js
│   ├── run-applescript/
│   │   └── index.js
│   ├── safe-buffer/
│   │   └── index.js
│   ├── semver/
│   │   ├── classes/
│   │   │   ├── comparator.js
│   │   │   ├── range.js
│   │   │   └── semver.js
│   │   ├── functions/
│   │   │   ├── clean.js
│   │   │   ├── cmp.js
│   │   │   ├── coerce.js
│   │   │   ├── compare-build.js
│   │   │   ├── compare-loose.js
│   │   │   ├── compare.js
│   │   │   ├── diff.js
│   │   │   ├── eq.js
│   │   │   ├── gt.js
│   │   │   ├── gte.js
│   │   │   ├── inc.js
│   │   │   ├── lt.js
│   │   │   ├── lte.js
│   │   │   ├── major.js
│   │   │   ├── minor.js
│   │   │   ├── neq.js
│   │   │   ├── parse.js
│   │   │   ├── patch.js
│   │   │   ├── prerelease.js
│   │   │   ├── rcompare.js
│   │   │   ├── rsort.js
│   │   │   ├── satisfies.js
│   │   │   ├── sort.js
│   │   │   └── valid.js
│   │   ├── internal/
│   │   │   ├── constants.js
│   │   │   ├── debug.js
│   │   │   ├── identifiers.js
│   │   │   ├── lrucache.js
│   │   │   ├── parse-options.js
│   │   │   └── re.js
│   │   ├── ranges/
│   │   │   ├── gtr.js
│   │   │   ├── intersects.js
│   │   │   ├── ltr.js
│   │   │   ├── max-satisfying.js
│   │   │   ├── min-satisfying.js
│   │   │   ├── min-version.js
│   │   │   ├── outside.js
│   │   │   ├── simplify.js
│   │   │   ├── subset.js
│   │   │   ├── to-comparators.js
│   │   │   └── valid.js
│   │   └── index.js
│   ├── sharp/
│   │   ├── lib/
│   │   │   ├── channel.js
│   │   │   ├── colour.js
│   │   │   ├── composite.js
│   │   │   ├── constructor.js
│   │   │   ├── index.js
│   │   │   ├── input.js
│   │   │   ├── is.js
│   │   │   ├── libvips.js
│   │   │   ├── operation.js
│   │   │   ├── output.js
│   │   │   ├── resize.js
│   │   │   ├── sharp.js
│   │   │   └── utility.js
│   │   └── node_modules/
│   │       └── semver/
│   │           ├── classes/
│   │           │   ├── comparator.js
│   │           │   ├── range.js
│   │           │   └── semver.js
│   │           ├── functions/
│   │           │   ├── cmp.js
│   │           │   ├── coerce.js
│   │           │   ├── compare.js
│   │           │   ├── eq.js
│   │           │   ├── gt.js
│   │           │   ├── gte.js
│   │           │   ├── lt.js
│   │           │   ├── lte.js
│   │           │   ├── neq.js
│   │           │   ├── parse.js
│   │           │   └── satisfies.js
│   │           └── internal/
│   │               ├── constants.js
│   │               ├── debug.js
│   │               ├── identifiers.js
│   │               ├── lrucache.js
│   │               ├── parse-options.js
│   │               └── re.js
│   ├── shebang-command/
│   │   └── index.js
│   ├── shebang-regex/
│   │   └── index.js
│   ├── shell-quote/
│   │   ├── index.js
│   │   ├── parse.js
│   │   └── quote.js
│   ├── signal-exit/
│   │   └── dist/
│   │       └── mjs/
│   │           ├── index.js
│   │           └── signals.js
│   ├── stack-utils/
│   │   ├── node_modules/
│   │   │   └── escape-string-regexp/
│   │   │       └── index.js
│   │   └── index.js
│   ├── string-width/
│   │   ├── node_modules/
│   │   │   ├── is-fullwidth-code-point/
│   │   │   │   └── index.js
│   │   │   └── strip-ansi/
│   │   │       ├── node_modules/
│   │   │       │   └── ansi-regex/
│   │   │       │       └── index.js
│   │   │       └── index.js
│   │   └── index.js
│   ├── strip-ansi/
│   │   └── index.js
│   ├── strip-final-newline/
│   │   └── index.js
│   ├── supports-color/
│   │   └── index.js
│   ├── supports-hyperlinks/
│   │   ├── node_modules/
│   │   │   └── supports-color/
│   │   │       └── index.js
│   │   └── index.js
│   ├── tr46/
│   │   ├── lib/
│   │   │   ├── regexes.js
│   │   │   └── statusMapping.js
│   │   └── index.js
│   ├── tree-kill/
│   │   └── index.js
│   ├── tslib/
│   │   ├── modules/
│   │   │   └── index.js
│   │   └── tslib.js
│   ├── turndown/
│   │   └── lib/
│   │       └── turndown.cjs.js
│   ├── undici/
│   │   ├── lib/
│   │   │   ├── api/
│   │   │   │   ├── abort-signal.js
│   │   │   │   ├── api-connect.js
│   │   │   │   ├── api-pipeline.js
│   │   │   │   ├── api-request.js
│   │   │   │   ├── api-stream.js
│   │   │   │   ├── api-upgrade.js
│   │   │   │   ├── index.js
│   │   │   │   ├── readable.js
│   │   │   │   └── util.js
│   │   │   ├── core/
│   │   │   │   ├── connect.js
│   │   │   │   ├── constants.js
│   │   │   │   ├── diagnostics.js
│   │   │   │   ├── errors.js
│   │   │   │   ├── request.js
│   │   │   │   ├── symbols.js
│   │   │   │   ├── tree.js
│   │   │   │   └── util.js
│   │   │   ├── dispatcher/
│   │   │   │   ├── agent.js
│   │   │   │   ├── balanced-pool.js
│   │   │   │   ├── client-h1.js
│   │   │   │   ├── client-h2.js
│   │   │   │   ├── client.js
│   │   │   │   ├── dispatcher-base.js
│   │   │   │   ├── dispatcher.js
│   │   │   │   ├── env-http-proxy-agent.js
│   │   │   │   ├── fixed-queue.js
│   │   │   │   ├── pool-base.js
│   │   │   │   ├── pool-stats.js
│   │   │   │   ├── pool.js
│   │   │   │   ├── proxy-agent.js
│   │   │   │   └── retry-agent.js
│   │   │   ├── handler/
│   │   │   │   ├── decorator-handler.js
│   │   │   │   ├── redirect-handler.js
│   │   │   │   └── retry-handler.js
│   │   │   ├── interceptor/
│   │   │   │   ├── dns.js
│   │   │   │   ├── dump.js
│   │   │   │   ├── redirect-interceptor.js
│   │   │   │   ├── redirect.js
│   │   │   │   └── retry.js
│   │   │   ├── llhttp/
│   │   │   │   ├── constants.js
│   │   │   │   ├── llhttp_simd-wasm.js
│   │   │   │   ├── llhttp-wasm.js
│   │   │   │   └── utils.js
│   │   │   ├── mock/
│   │   │   │   ├── mock-agent.js
│   │   │   │   ├── mock-client.js
│   │   │   │   ├── mock-errors.js
│   │   │   │   ├── mock-interceptor.js
│   │   │   │   ├── mock-pool.js
│   │   │   │   ├── mock-symbols.js
│   │   │   │   ├── mock-utils.js
│   │   │   │   ├── pending-interceptors-formatter.js
│   │   │   │   └── pluralizer.js
│   │   │   ├── util/
│   │   │   │   └── timers.js
│   │   │   ├── web/
│   │   │   │   ├── cache/
│   │   │   │   │   ├── cache.js
│   │   │   │   │   ├── cachestorage.js
│   │   │   │   │   ├── symbols.js
│   │   │   │   │   └── util.js
│   │   │   │   ├── cookies/
│   │   │   │   │   ├── constants.js
│   │   │   │   │   ├── index.js
│   │   │   │   │   ├── parse.js
│   │   │   │   │   └── util.js
│   │   │   │   ├── eventsource/
│   │   │   │   │   ├── eventsource-stream.js
│   │   │   │   │   ├── eventsource.js
│   │   │   │   │   └── util.js
│   │   │   │   ├── fetch/
│   │   │   │   │   ├── body.js
│   │   │   │   │   ├── constants.js
│   │   │   │   │   ├── data-url.js
│   │   │   │   │   ├── dispatcher-weakref.js
│   │   │   │   │   ├── file.js
│   │   │   │   │   ├── formdata-parser.js
│   │   │   │   │   ├── formdata.js
│   │   │   │   │   ├── global.js
│   │   │   │   │   ├── headers.js
│   │   │   │   │   ├── index.js
│   │   │   │   │   ├── request.js
│   │   │   │   │   ├── response.js
│   │   │   │   │   ├── symbols.js
│   │   │   │   │   ├── util.js
│   │   │   │   │   └── webidl.js
│   │   │   │   ├── fileapi/
│   │   │   │   │   ├── encoding.js
│   │   │   │   │   ├── filereader.js
│   │   │   │   │   ├── progressevent.js
│   │   │   │   │   ├── symbols.js
│   │   │   │   │   └── util.js
│   │   │   │   └── websocket/
│   │   │   │       ├── connection.js
│   │   │   │       ├── constants.js
│   │   │   │       ├── events.js
│   │   │   │       ├── frame.js
│   │   │   │       ├── permessage-deflate.js
│   │   │   │       ├── receiver.js
│   │   │   │       ├── sender.js
│   │   │   │       ├── symbols.js
│   │   │   │       ├── util.js
│   │   │   │       └── websocket.js
│   │   │   └── global.js
│   │   └── index.js
│   ├── universalify/
│   │   └── index.js
│   ├── usehooks-ts/
│   │   └── dist/
│   │       └── index.js
│   ├── uuid/
│   │   └── dist/
│   │       ├── index.js
│   │       ├── md5.js
│   │       ├── nil.js
│   │       ├── parse.js
│   │       ├── regex.js
│   │       ├── rng.js
│   │       ├── sha1.js
│   │       ├── stringify.js
│   │       ├── v1.js
│   │       ├── v3.js
│   │       ├── v35.js
│   │       ├── v4.js
│   │       ├── v5.js
│   │       ├── validate.js
│   │       └── version.js
│   ├── vscode-jsonrpc/
│   │   └── lib/
│   │       ├── common/
│   │       │   ├── api.js
│   │       │   ├── cancellation.js
│   │       │   ├── connection.js
│   │       │   ├── disposable.js
│   │       │   ├── events.js
│   │       │   ├── is.js
│   │       │   ├── linkedMap.js
│   │       │   ├── messageBuffer.js
│   │       │   ├── messageReader.js
│   │       │   ├── messages.js
│   │       │   ├── messageWriter.js
│   │       │   ├── ral.js
│   │       │   ├── semaphore.js
│   │       │   └── sharedArrayCancellation.js
│   │       └── node/
│   │           ├── main.js
│   │           └── ril.js
│   ├── webidl-conversions/
│   │   └── lib/
│   │       └── index.js
│   ├── whatwg-url/
│   │   ├── lib/
│   │   │   ├── encoding.js
│   │   │   ├── Function.js
│   │   │   ├── infra.js
│   │   │   ├── percent-encoding.js
│   │   │   ├── URL-impl.js
│   │   │   ├── url-state-machine.js
│   │   │   ├── URL.js
│   │   │   ├── urlencoded.js
│   │   │   ├── URLSearchParams-impl.js
│   │   │   ├── URLSearchParams.js
│   │   │   └── utils.js
│   │   ├── index.js
│   │   └── webidl2js-wrapper.js
│   ├── which/
│   │   └── which.js
│   ├── wrap-ansi/
│   │   ├── node_modules/
│   │   │   └── string-width/
│   │   │       ├── node_modules/
│   │   │       │   └── emoji-regex/
│   │   │       │       └── index.js
│   │   │       └── index.js
│   │   └── index.js
│   ├── ws/
│   │   └── lib/
│   │       ├── buffer-util.js
│   │       ├── constants.js
│   │       ├── event-target.js
│   │       ├── extension.js
│   │       ├── limiter.js
│   │       ├── permessage-deflate.js
│   │       ├── receiver.js
│   │       ├── sender.js
│   │       ├── stream.js
│   │       ├── subprotocol.js
│   │       ├── validation.js
│   │       ├── websocket-server.js
│   │       └── websocket.js
│   ├── wsl-utils/
│   │   └── index.js
│   ├── xmlbuilder/
│   │   └── lib/
│   │       ├── DocumentPosition.js
│   │       ├── index.js
│   │       ├── NodeType.js
│   │       ├── Utility.js
│   │       ├── WriterState.js
│   │       ├── XMLAttribute.js
│   │       ├── XMLCData.js
│   │       ├── XMLCharacterData.js
│   │       ├── XMLComment.js
│   │       ├── XMLDeclaration.js
│   │       ├── XMLDocType.js
│   │       ├── XMLDocument.js
│   │       ├── XMLDocumentCB.js
│   │       ├── XMLDOMConfiguration.js
│   │       ├── XMLDOMErrorHandler.js
│   │       ├── XMLDOMImplementation.js
│   │       ├── XMLDOMStringList.js
│   │       ├── XMLDTDAttList.js
│   │       ├── XMLDTDElement.js
│   │       ├── XMLDTDEntity.js
│   │       ├── XMLDTDNotation.js
│   │       ├── XMLDummy.js
│   │       ├── XMLElement.js
│   │       ├── XMLNamedNodeMap.js
│   │       ├── XMLNode.js
│   │       ├── XMLNodeList.js
│   │       ├── XMLProcessingInstruction.js
│   │       ├── XMLRaw.js
│   │       ├── XMLStreamWriter.js
│   │       ├── XMLStringifier.js
│   │       ├── XMLStringWriter.js
│   │       ├── XMLText.js
│   │       └── XMLWriterBase.js
│   ├── xss/
│   │   └── lib/
│   │       ├── default.js
│   │       ├── index.js
│   │       ├── parser.js
│   │       ├── util.js
│   │       └── xss.js
│   ├── yaml/
│   │   └── dist/
│   │       ├── compose/
│   │       │   ├── compose-collection.js
│   │       │   ├── compose-doc.js
│   │       │   ├── compose-node.js
│   │       │   ├── compose-scalar.js
│   │       │   ├── composer.js
│   │       │   ├── resolve-block-map.js
│   │       │   ├── resolve-block-scalar.js
│   │       │   ├── resolve-block-seq.js
│   │       │   ├── resolve-end.js
│   │       │   ├── resolve-flow-collection.js
│   │       │   ├── resolve-flow-scalar.js
│   │       │   ├── resolve-props.js
│   │       │   ├── util-contains-newline.js
│   │       │   ├── util-empty-scalar-position.js
│   │       │   ├── util-flow-indent-check.js
│   │       │   └── util-map-includes.js
│   │       ├── doc/
│   │       │   ├── anchors.js
│   │       │   ├── applyReviver.js
│   │       │   ├── createNode.js
│   │       │   ├── directives.js
│   │       │   └── Document.js
│   │       ├── nodes/
│   │       │   ├── addPairToJSMap.js
│   │       │   ├── Alias.js
│   │       │   ├── Collection.js
│   │       │   ├── identity.js
│   │       │   ├── Node.js
│   │       │   ├── Pair.js
│   │       │   ├── Scalar.js
│   │       │   ├── toJS.js
│   │       │   ├── YAMLMap.js
│   │       │   └── YAMLSeq.js
│   │       ├── parse/
│   │       │   ├── cst-scalar.js
│   │       │   ├── cst-stringify.js
│   │       │   ├── cst-visit.js
│   │       │   ├── cst.js
│   │       │   ├── lexer.js
│   │       │   ├── line-counter.js
│   │       │   └── parser.js
│   │       ├── schema/
│   │       │   ├── common/
│   │       │   │   ├── map.js
│   │       │   │   ├── null.js
│   │       │   │   ├── seq.js
│   │       │   │   └── string.js
│   │       │   ├── core/
│   │       │   │   ├── bool.js
│   │       │   │   ├── float.js
│   │       │   │   ├── int.js
│   │       │   │   └── schema.js
│   │       │   ├── json/
│   │       │   │   └── schema.js
│   │       │   ├── yaml-1.1/
│   │       │   │   ├── binary.js
│   │       │   │   ├── bool.js
│   │       │   │   ├── float.js
│   │       │   │   ├── int.js
│   │       │   │   ├── merge.js
│   │       │   │   ├── omap.js
│   │       │   │   ├── pairs.js
│   │       │   │   ├── schema.js
│   │       │   │   ├── set.js
│   │       │   │   └── timestamp.js
│   │       │   ├── Schema.js
│   │       │   └── tags.js
│   │       ├── stringify/
│   │       │   ├── foldFlowLines.js
│   │       │   ├── stringify.js
│   │       │   ├── stringifyCollection.js
│   │       │   ├── stringifyComment.js
│   │       │   ├── stringifyDocument.js
│   │       │   ├── stringifyNumber.js
│   │       │   ├── stringifyPair.js
│   │       │   └── stringifyString.js
│   │       ├── errors.js
│   │       ├── index.js
│   │       ├── log.js
│   │       ├── public-api.js
│   │       └── visit.js
│   ├── yoctocolors-cjs/
│   │   └── index.js
│   ├── zod/
│   │   ├── v3/
│   │   │   ├── helpers/
│   │   │   │   ├── errorUtil.js
│   │   │   │   ├── parseUtil.js
│   │   │   │   └── util.js
│   │   │   ├── locales/
│   │   │   │   └── en.js
│   │   │   ├── errors.js
│   │   │   ├── external.js
│   │   │   ├── types.js
│   │   │   └── ZodError.js
│   │   ├── v4/
│   │   │   ├── classic/
│   │   │   │   ├── checks.js
│   │   │   │   ├── coerce.js
│   │   │   │   ├── compat.js
│   │   │   │   ├── errors.js
│   │   │   │   ├── external.js
│   │   │   │   ├── index.js
│   │   │   │   ├── iso.js
│   │   │   │   ├── parse.js
│   │   │   │   └── schemas.js
│   │   │   ├── core/
│   │   │   │   ├── api.js
│   │   │   │   ├── checks.js
│   │   │   │   ├── core.js
│   │   │   │   ├── doc.js
│   │   │   │   ├── errors.js
│   │   │   │   ├── function.js
│   │   │   │   ├── index.js
│   │   │   │   ├── parse.js
│   │   │   │   ├── regexes.js
│   │   │   │   ├── registries.js
│   │   │   │   ├── schemas.js
│   │   │   │   ├── to-json-schema.js
│   │   │   │   ├── util.js
│   │   │   │   └── versions.js
│   │   │   ├── locales/
│   │   │   │   ├── ar.js
│   │   │   │   ├── az.js
│   │   │   │   ├── be.js
│   │   │   │   ├── ca.js
│   │   │   │   ├── cs.js
│   │   │   │   ├── de.js
│   │   │   │   ├── en.js
│   │   │   │   ├── eo.js
│   │   │   │   ├── es.js
│   │   │   │   ├── fa.js
│   │   │   │   ├── fi.js
│   │   │   │   ├── fr-CA.js
│   │   │   │   ├── fr.js
│   │   │   │   ├── he.js
│   │   │   │   ├── hu.js
│   │   │   │   ├── id.js
│   │   │   │   ├── index.js
│   │   │   │   ├── it.js
│   │   │   │   ├── ja.js
│   │   │   │   ├── kh.js
│   │   │   │   ├── ko.js
│   │   │   │   ├── mk.js
│   │   │   │   ├── ms.js
│   │   │   │   ├── nl.js
│   │   │   │   ├── no.js
│   │   │   │   ├── ota.js
│   │   │   │   ├── pl.js
│   │   │   │   ├── ps.js
│   │   │   │   ├── pt.js
│   │   │   │   ├── ru.js
│   │   │   │   ├── sl.js
│   │   │   │   ├── sv.js
│   │   │   │   ├── ta.js
│   │   │   │   ├── th.js
│   │   │   │   ├── tr.js
│   │   │   │   ├── ua.js
│   │   │   │   ├── ur.js
│   │   │   │   ├── vi.js
│   │   │   │   ├── zh-CN.js
│   │   │   │   └── zh-TW.js
│   │   │   ├── mini/
│   │   │   │   ├── external.js
│   │   │   │   ├── index.js
│   │   │   │   └── parse.js
│   │   │   └── index.js
│   │   ├── v4-mini/
│   │   │   └── index.js
│   │   └── index.js
│   └── zod-to-json-schema/
│       └── dist/
│           └── esm/
│               ├── parsers/
│               │   ├── array.js
│               │   ├── branded.js
│               │   ├── catch.js
│               │   ├── default.js
│               │   ├── effects.js
│               │   ├── intersection.js
│               │   ├── map.js
│               │   ├── never.js
│               │   ├── nullable.js
│               │   ├── object.js
│               │   ├── optional.js
│               │   ├── pipeline.js
│               │   ├── promise.js
│               │   ├── readonly.js
│               │   ├── record.js
│               │   ├── set.js
│               │   ├── string.js
│               │   ├── tuple.js
│               │   ├── undefined.js
│               │   ├── union.js
│               │   └── unknown.js
│               ├── index.js
│               ├── Options.js
│               ├── parseDef.js
│               ├── Refs.js
│               ├── selectParser.js
│               └── zodToJsonSchema.js
├── src/
│   ├── assistant/
│   │   └── sessionHistory.ts
│   ├── bootstrap/
│   │   └── state.ts
│   ├── bridge/
│   │   ├── bridgeApi.ts
│   │   ├── bridgeConfig.ts
│   │   ├── bridgeDebug.ts
│   │   ├── bridgeEnabled.ts
│   │   ├── bridgeMain.ts
│   │   ├── bridgeMessaging.ts
│   │   ├── bridgePermissionCallbacks.ts
│   │   ├── bridgePointer.ts
│   │   ├── bridgeStatusUtil.ts
│   │   ├── bridgeUI.ts
│   │   ├── capacityWake.ts
│   │   ├── codeSessionApi.ts
│   │   ├── createSession.ts
│   │   ├── debugUtils.ts
│   │   ├── envLessBridgeConfig.ts
│   │   ├── flushGate.ts
│   │   ├── inboundAttachments.ts
│   │   ├── inboundMessages.ts
│   │   ├── initReplBridge.ts
│   │   ├── jwtUtils.ts
│   │   ├── pollConfig.ts
│   │   ├── pollConfigDefaults.ts
│   │   ├── remoteBridgeCore.ts
│   │   ├── replBridge.ts
│   │   ├── replBridgeHandle.ts
│   │   ├── replBridgeTransport.ts
│   │   ├── sessionIdCompat.ts
│   │   ├── sessionRunner.ts
│   │   ├── trustedDevice.ts
│   │   ├── types.ts
│   │   └── workSecret.ts
│   ├── buddy/
│   │   ├── companion.ts
│   │   ├── CompanionSprite.tsx
│   │   ├── prompt.ts
│   │   ├── sprites.ts
│   │   ├── types.ts
│   │   └── useBuddyNotification.tsx
│   ├── cli/
│   │   ├── handlers/
│   │   │   ├── agents.ts
│   │   │   ├── auth.ts
│   │   │   ├── autoMode.ts
│   │   │   ├── mcp.tsx
│   │   │   ├── plugins.ts
│   │   │   └── util.tsx
│   │   ├── transports/
│   │   │   ├── ccrClient.ts
│   │   │   ├── HybridTransport.ts
│   │   │   ├── SerialBatchEventUploader.ts
│   │   │   ├── SSETransport.ts
│   │   │   ├── transportUtils.ts
│   │   │   ├── WebSocketTransport.ts
│   │   │   └── WorkerStateUploader.ts
│   │   ├── exit.ts
│   │   ├── ndjsonSafeStringify.ts
│   │   ├── print.ts
│   │   ├── remoteIO.ts
│   │   ├── structuredIO.ts
│   │   └── update.ts
│   ├── commands/
│   │   ├── add-dir/
│   │   │   ├── add-dir.tsx
│   │   │   ├── index.ts
│   │   │   └── validation.ts
│   │   ├── agents/
│   │   │   ├── agents.tsx
│   │   │   └── index.ts
│   │   ├── ant-trace/
│   │   │   └── index.js
│   │   ├── autofix-pr/
│   │   │   └── index.js
│   │   ├── backfill-sessions/
│   │   │   └── index.js
│   │   ├── branch/
│   │   │   ├── branch.ts
│   │   │   └── index.ts
│   │   ├── break-cache/
│   │   │   └── index.js
│   │   ├── bridge/
│   │   │   ├── bridge.tsx
│   │   │   └── index.ts
│   │   ├── btw/
│   │   │   ├── btw.tsx
│   │   │   └── index.ts
│   │   ├── bughunter/
│   │   │   └── index.js
│   │   ├── chrome/
│   │   │   ├── chrome.tsx
│   │   │   └── index.ts
│   │   ├── clear/
│   │   │   ├── caches.ts
│   │   │   ├── clear.ts
│   │   │   ├── conversation.ts
│   │   │   └── index.ts
│   │   ├── color/
│   │   │   ├── color.ts
│   │   │   └── index.ts
│   │   ├── compact/
│   │   │   ├── compact.ts
│   │   │   └── index.ts
│   │   ├── config/
│   │   │   ├── config.tsx
│   │   │   └── index.ts
│   │   ├── context/
│   │   │   ├── context-noninteractive.ts
│   │   │   ├── context.tsx
│   │   │   └── index.ts
│   │   ├── copy/
│   │   │   ├── copy.tsx
│   │   │   └── index.ts
│   │   ├── cost/
│   │   │   ├── cost.ts
│   │   │   └── index.ts
│   │   ├── ctx_viz/
│   │   │   └── index.js
│   │   ├── debug-tool-call/
│   │   │   └── index.js
│   │   ├── desktop/
│   │   │   ├── desktop.tsx
│   │   │   └── index.ts
│   │   ├── diff/
│   │   │   ├── diff.tsx
│   │   │   └── index.ts
│   │   ├── doctor/
│   │   │   ├── doctor.tsx
│   │   │   └── index.ts
│   │   ├── effort/
│   │   │   ├── effort.tsx
│   │   │   └── index.ts
│   │   ├── env/
│   │   │   └── index.js
│   │   ├── exit/
│   │   │   ├── exit.tsx
│   │   │   └── index.ts
│   │   ├── export/
│   │   │   ├── export.tsx
│   │   │   └── index.ts
│   │   ├── extra-usage/
│   │   │   ├── extra-usage-core.ts
│   │   │   ├── extra-usage-noninteractive.ts
│   │   │   ├── extra-usage.tsx
│   │   │   └── index.ts
│   │   ├── fast/
│   │   │   ├── fast.tsx
│   │   │   └── index.ts
│   │   ├── feedback/
│   │   │   ├── feedback.tsx
│   │   │   └── index.ts
│   │   ├── files/
│   │   │   ├── files.ts
│   │   │   └── index.ts
│   │   ├── good-claude/
│   │   │   └── index.js
│   │   ├── heapdump/
│   │   │   ├── heapdump.ts
│   │   │   └── index.ts
│   │   ├── help/
│   │   │   ├── help.tsx
│   │   │   └── index.ts
│   │   ├── hooks/
│   │   │   ├── hooks.tsx
│   │   │   └── index.ts
│   │   ├── ide/
│   │   │   ├── ide.tsx
│   │   │   └── index.ts
│   │   ├── install-github-app/
│   │   │   ├── ApiKeyStep.tsx
│   │   │   ├── CheckExistingSecretStep.tsx
│   │   │   ├── CheckGitHubStep.tsx
│   │   │   ├── ChooseRepoStep.tsx
│   │   │   ├── CreatingStep.tsx
│   │   │   ├── ErrorStep.tsx
│   │   │   ├── ExistingWorkflowStep.tsx
│   │   │   ├── index.ts
│   │   │   ├── install-github-app.tsx
│   │   │   ├── InstallAppStep.tsx
│   │   │   ├── OAuthFlowStep.tsx
│   │   │   ├── setupGitHubActions.ts
│   │   │   ├── SuccessStep.tsx
│   │   │   └── WarningsStep.tsx
│   │   ├── install-slack-app/
│   │   │   ├── index.ts
│   │   │   └── install-slack-app.ts
│   │   ├── issue/
│   │   │   └── index.js
│   │   ├── keybindings/
│   │   │   ├── index.ts
│   │   │   └── keybindings.ts
│   │   ├── login/
│   │   │   ├── index.ts
│   │   │   └── login.tsx
│   │   ├── logout/
│   │   │   ├── index.ts
│   │   │   └── logout.tsx
│   │   ├── mcp/
│   │   │   ├── addCommand.ts
│   │   │   ├── index.ts
│   │   │   ├── mcp.tsx
│   │   │   └── xaaIdpCommand.ts
│   │   ├── memory/
│   │   │   ├── index.ts
│   │   │   └── memory.tsx
│   │   ├── mobile/
│   │   │   ├── index.ts
│   │   │   └── mobile.tsx
│   │   ├── mock-limits/
│   │   │   └── index.js
│   │   ├── model/
│   │   │   ├── index.ts
│   │   │   └── model.tsx
│   │   ├── oauth-refresh/
│   │   │   └── index.js
│   │   ├── onboarding/
│   │   │   └── index.js
│   │   ├── output-style/
│   │   │   ├── index.ts
│   │   │   └── output-style.tsx
│   │   ├── passes/
│   │   │   ├── index.ts
│   │   │   └── passes.tsx
│   │   ├── perf-issue/
│   │   │   └── index.js
│   │   ├── permissions/
│   │   │   ├── index.ts
│   │   │   └── permissions.tsx
│   │   ├── plan/
│   │   │   ├── index.ts
│   │   │   └── plan.tsx
│   │   ├── plugin/
│   │   │   ├── AddMarketplace.tsx
│   │   │   ├── BrowseMarketplace.tsx
│   │   │   ├── DiscoverPlugins.tsx
│   │   │   ├── index.tsx
│   │   │   ├── ManageMarketplaces.tsx
│   │   │   ├── ManagePlugins.tsx
│   │   │   ├── parseArgs.ts
│   │   │   ├── plugin.tsx
│   │   │   ├── pluginDetailsHelpers.tsx
│   │   │   ├── PluginErrors.tsx
│   │   │   ├── PluginOptionsDialog.tsx
│   │   │   ├── PluginOptionsFlow.tsx
│   │   │   ├── PluginSettings.tsx
│   │   │   ├── PluginTrustWarning.tsx
│   │   │   ├── UnifiedInstalledCell.tsx
│   │   │   ├── usePagination.ts
│   │   │   └── ValidatePlugin.tsx
│   │   ├── pr_comments/
│   │   │   └── index.ts
│   │   ├── privacy-settings/
│   │   │   ├── index.ts
│   │   │   └── privacy-settings.tsx
│   │   ├── rate-limit-options/
│   │   │   ├── index.ts
│   │   │   └── rate-limit-options.tsx
│   │   ├── release-notes/
│   │   │   ├── index.ts
│   │   │   └── release-notes.ts
│   │   ├── reload-plugins/
│   │   │   ├── index.ts
│   │   │   └── reload-plugins.ts
│   │   ├── remote-env/
│   │   │   ├── index.ts
│   │   │   └── remote-env.tsx
│   │   ├── remote-setup/
│   │   │   ├── api.ts
│   │   │   ├── index.ts
│   │   │   └── remote-setup.tsx
│   │   ├── rename/
│   │   │   ├── generateSessionName.ts
│   │   │   ├── index.ts
│   │   │   └── rename.ts
│   │   ├── reset-limits/
│   │   │   └── index.js
│   │   ├── resume/
│   │   │   ├── index.ts
│   │   │   └── resume.tsx
│   │   ├── review/
│   │   │   ├── reviewRemote.ts
│   │   │   ├── ultrareviewCommand.tsx
│   │   │   ├── ultrareviewEnabled.ts
│   │   │   └── UltrareviewOverageDialog.tsx
│   │   ├── rewind/
│   │   │   ├── index.ts
│   │   │   └── rewind.ts
│   │   ├── sandbox-toggle/
│   │   │   ├── index.ts
│   │   │   └── sandbox-toggle.tsx
│   │   ├── session/
│   │   │   ├── index.ts
│   │   │   └── session.tsx
│   │   ├── share/
│   │   │   └── index.js
│   │   ├── skills/
│   │   │   ├── index.ts
│   │   │   └── skills.tsx
│   │   ├── stats/
│   │   │   ├── index.ts
│   │   │   └── stats.tsx
│   │   ├── status/
│   │   │   ├── index.ts
│   │   │   └── status.tsx
│   │   ├── stickers/
│   │   │   ├── index.ts
│   │   │   └── stickers.ts
│   │   ├── summary/
│   │   │   └── index.js
│   │   ├── tag/
│   │   │   ├── index.ts
│   │   │   └── tag.tsx
│   │   ├── tasks/
│   │   │   ├── index.ts
│   │   │   └── tasks.tsx
│   │   ├── teleport/
│   │   │   └── index.js
│   │   ├── terminalSetup/
│   │   │   ├── index.ts
│   │   │   └── terminalSetup.tsx
│   │   ├── theme/
│   │   │   ├── index.ts
│   │   │   └── theme.tsx
│   │   ├── thinkback/
│   │   │   ├── index.ts
│   │   │   └── thinkback.tsx
│   │   ├── thinkback-play/
│   │   │   ├── index.ts
│   │   │   └── thinkback-play.ts
│   │   ├── upgrade/
│   │   │   ├── index.ts
│   │   │   └── upgrade.tsx
│   │   ├── usage/
│   │   │   ├── index.ts
│   │   │   └── usage.tsx
│   │   ├── vim/
│   │   │   ├── index.ts
│   │   │   └── vim.ts
│   │   ├── voice/
│   │   │   ├── index.ts
│   │   │   └── voice.ts
│   │   ├── advisor.ts
│   │   ├── bridge-kick.ts
│   │   ├── brief.ts
│   │   ├── commit-push-pr.ts
│   │   ├── commit.ts
│   │   ├── createMovedToPluginCommand.ts
│   │   ├── init-verifiers.ts
│   │   ├── init.ts
│   │   ├── insights.ts
│   │   ├── install.tsx
│   │   ├── review.ts
│   │   ├── security-review.ts
│   │   ├── statusline.tsx
│   │   ├── ultraplan.tsx
│   │   └── version.ts
│   ├── components/
│   │   ├── agents/
│   │   │   ├── new-agent-creation/
│   │   │   │   ├── wizard-steps/
│   │   │   │   │   ├── ColorStep.tsx
│   │   │   │   │   ├── ConfirmStep.tsx
│   │   │   │   │   ├── ConfirmStepWrapper.tsx
│   │   │   │   │   ├── DescriptionStep.tsx
│   │   │   │   │   ├── GenerateStep.tsx
│   │   │   │   │   ├── LocationStep.tsx
│   │   │   │   │   ├── MemoryStep.tsx
│   │   │   │   │   ├── MethodStep.tsx
│   │   │   │   │   ├── ModelStep.tsx
│   │   │   │   │   ├── PromptStep.tsx
│   │   │   │   │   ├── ToolsStep.tsx
│   │   │   │   │   └── TypeStep.tsx
│   │   │   │   └── CreateAgentWizard.tsx
│   │   │   ├── AgentDetail.tsx
│   │   │   ├── AgentEditor.tsx
│   │   │   ├── agentFileUtils.ts
│   │   │   ├── AgentNavigationFooter.tsx
│   │   │   ├── AgentsList.tsx
│   │   │   ├── AgentsMenu.tsx
│   │   │   ├── ColorPicker.tsx
│   │   │   ├── generateAgent.ts
│   │   │   ├── ModelSelector.tsx
│   │   │   ├── ToolSelector.tsx
│   │   │   ├── types.ts
│   │   │   ├── utils.ts
│   │   │   └── validateAgent.ts
│   │   ├── ClaudeCodeHint/
│   │   │   └── PluginHintMenu.tsx
│   │   ├── CustomSelect/
│   │   │   ├── index.ts
│   │   │   ├── option-map.ts
│   │   │   ├── select-input-option.tsx
│   │   │   ├── select-option.tsx
│   │   │   ├── select.tsx
│   │   │   ├── SelectMulti.tsx
│   │   │   ├── use-multi-select-state.ts
│   │   │   ├── use-select-input.ts
│   │   │   ├── use-select-navigation.ts
│   │   │   └── use-select-state.ts
│   │   ├── design-system/
│   │   │   ├── Byline.tsx
│   │   │   ├── color.ts
│   │   │   ├── Dialog.tsx
│   │   │   ├── Divider.tsx
│   │   │   ├── FuzzyPicker.tsx
│   │   │   ├── KeyboardShortcutHint.tsx
│   │   │   ├── ListItem.tsx
│   │   │   ├── LoadingState.tsx
│   │   │   ├── Pane.tsx
│   │   │   ├── ProgressBar.tsx
│   │   │   ├── Ratchet.tsx
│   │   │   ├── StatusIcon.tsx
│   │   │   ├── Tabs.tsx
│   │   │   ├── ThemedBox.tsx
│   │   │   ├── ThemedText.tsx
│   │   │   └── ThemeProvider.tsx
│   │   ├── DesktopUpsell/
│   │   │   └── DesktopUpsellStartup.tsx
│   │   ├── diff/
│   │   │   ├── DiffDetailView.tsx
│   │   │   ├── DiffDialog.tsx
│   │   │   └── DiffFileList.tsx
│   │   ├── FeedbackSurvey/
│   │   │   ├── FeedbackSurvey.tsx
│   │   │   ├── FeedbackSurveyView.tsx
│   │   │   ├── submitTranscriptShare.ts
│   │   │   ├── TranscriptSharePrompt.tsx
│   │   │   ├── useDebouncedDigitInput.ts
│   │   │   ├── useFeedbackSurvey.tsx
│   │   │   ├── useMemorySurvey.tsx
│   │   │   ├── usePostCompactSurvey.tsx
│   │   │   └── useSurveyState.tsx
│   │   ├── grove/
│   │   │   └── Grove.tsx
│   │   ├── HelpV2/
│   │   │   ├── Commands.tsx
│   │   │   ├── General.tsx
│   │   │   └── HelpV2.tsx
│   │   ├── HighlightedCode/
│   │   │   └── Fallback.tsx
│   │   ├── hooks/
│   │   │   ├── HooksConfigMenu.tsx
│   │   │   ├── PromptDialog.tsx
│   │   │   ├── SelectEventMode.tsx
│   │   │   ├── SelectHookMode.tsx
│   │   │   ├── SelectMatcherMode.tsx
│   │   │   └── ViewHookMode.tsx
│   │   ├── LogoV2/
│   │   │   ├── AnimatedAsterisk.tsx
│   │   │   ├── AnimatedClawd.tsx
│   │   │   ├── ChannelsNotice.tsx
│   │   │   ├── Clawd.tsx
│   │   │   ├── CondensedLogo.tsx
│   │   │   ├── EmergencyTip.tsx
│   │   │   ├── Feed.tsx
│   │   │   ├── FeedColumn.tsx
│   │   │   ├── feedConfigs.tsx
│   │   │   ├── GuestPassesUpsell.tsx
│   │   │   ├── LogoV2.tsx
│   │   │   ├── Opus1mMergeNotice.tsx
│   │   │   ├── OverageCreditUpsell.tsx
│   │   │   ├── VoiceModeNotice.tsx
│   │   │   └── WelcomeV2.tsx
│   │   ├── LspRecommendation/
│   │   │   └── LspRecommendationMenu.tsx
│   │   ├── ManagedSettingsSecurityDialog/
│   │   │   ├── ManagedSettingsSecurityDialog.tsx
│   │   │   └── utils.ts
│   │   ├── mcp/
│   │   │   ├── utils/
│   │   │   │   └── reconnectHelpers.tsx
│   │   │   ├── CapabilitiesSection.tsx
│   │   │   ├── ElicitationDialog.tsx
│   │   │   ├── index.ts
│   │   │   ├── MCPAgentServerMenu.tsx
│   │   │   ├── MCPListPanel.tsx
│   │   │   ├── McpParsingWarnings.tsx
│   │   │   ├── MCPReconnect.tsx
│   │   │   ├── MCPRemoteServerMenu.tsx
│   │   │   ├── MCPSettings.tsx
│   │   │   ├── MCPStdioServerMenu.tsx
│   │   │   ├── MCPToolDetailView.tsx
│   │   │   └── MCPToolListView.tsx
│   │   ├── memory/
│   │   │   ├── MemoryFileSelector.tsx
│   │   │   └── MemoryUpdateNotification.tsx
│   │   ├── messages/
│   │   │   ├── UserToolResultMessage/
│   │   │   │   ├── RejectedPlanMessage.tsx
│   │   │   │   ├── RejectedToolUseMessage.tsx
│   │   │   │   ├── UserToolCanceledMessage.tsx
│   │   │   │   ├── UserToolErrorMessage.tsx
│   │   │   │   ├── UserToolRejectMessage.tsx
│   │   │   │   ├── UserToolResultMessage.tsx
│   │   │   │   ├── UserToolSuccessMessage.tsx
│   │   │   │   └── utils.tsx
│   │   │   ├── AdvisorMessage.tsx
│   │   │   ├── AssistantRedactedThinkingMessage.tsx
│   │   │   ├── AssistantTextMessage.tsx
│   │   │   ├── AssistantThinkingMessage.tsx
│   │   │   ├── AssistantToolUseMessage.tsx
│   │   │   ├── AttachmentMessage.tsx
│   │   │   ├── CollapsedReadSearchContent.tsx
│   │   │   ├── CompactBoundaryMessage.tsx
│   │   │   ├── GroupedToolUseContent.tsx
│   │   │   ├── HighlightedThinkingText.tsx
│   │   │   ├── HookProgressMessage.tsx
│   │   │   ├── nullRenderingAttachments.ts
│   │   │   ├── PlanApprovalMessage.tsx
│   │   │   ├── RateLimitMessage.tsx
│   │   │   ├── ShutdownMessage.tsx
│   │   │   ├── SystemAPIErrorMessage.tsx
│   │   │   ├── SystemTextMessage.tsx
│   │   │   ├── TaskAssignmentMessage.tsx
│   │   │   ├── teamMemCollapsed.tsx
│   │   │   ├── teamMemSaved.ts
│   │   │   ├── UserAgentNotificationMessage.tsx
│   │   │   ├── UserBashInputMessage.tsx
│   │   │   ├── UserBashOutputMessage.tsx
│   │   │   ├── UserChannelMessage.tsx
│   │   │   ├── UserCommandMessage.tsx
│   │   │   ├── UserImageMessage.tsx
│   │   │   ├── UserLocalCommandOutputMessage.tsx
│   │   │   ├── UserMemoryInputMessage.tsx
│   │   │   ├── UserPlanMessage.tsx
│   │   │   ├── UserPromptMessage.tsx
│   │   │   ├── UserResourceUpdateMessage.tsx
│   │   │   ├── UserTeammateMessage.tsx
│   │   │   └── UserTextMessage.tsx
│   │   ├── Passes/
│   │   │   └── Passes.tsx
│   │   ├── permissions/
│   │   │   ├── AskUserQuestionPermissionRequest/
│   │   │   │   ├── AskUserQuestionPermissionRequest.tsx
│   │   │   │   ├── PreviewBox.tsx
│   │   │   │   ├── PreviewQuestionView.tsx
│   │   │   │   ├── QuestionNavigationBar.tsx
│   │   │   │   ├── QuestionView.tsx
│   │   │   │   ├── SubmitQuestionsView.tsx
│   │   │   │   └── use-multiple-choice-state.ts
│   │   │   ├── BashPermissionRequest/
│   │   │   │   ├── BashPermissionRequest.tsx
│   │   │   │   └── bashToolUseOptions.tsx
│   │   │   ├── ComputerUseApproval/
│   │   │   │   └── ComputerUseApproval.tsx
│   │   │   ├── EnterPlanModePermissionRequest/
│   │   │   │   └── EnterPlanModePermissionRequest.tsx
│   │   │   ├── ExitPlanModePermissionRequest/
│   │   │   │   └── ExitPlanModePermissionRequest.tsx
│   │   │   ├── FileEditPermissionRequest/
│   │   │   │   └── FileEditPermissionRequest.tsx
│   │   │   ├── FilePermissionDialog/
│   │   │   │   ├── FilePermissionDialog.tsx
│   │   │   │   ├── ideDiffConfig.ts
│   │   │   │   ├── permissionOptions.tsx
│   │   │   │   ├── useFilePermissionDialog.ts
│   │   │   │   └── usePermissionHandler.ts
│   │   │   ├── FilesystemPermissionRequest/
│   │   │   │   └── FilesystemPermissionRequest.tsx
│   │   │   ├── FileWritePermissionRequest/
│   │   │   │   ├── FileWritePermissionRequest.tsx
│   │   │   │   └── FileWriteToolDiff.tsx
│   │   │   ├── NotebookEditPermissionRequest/
│   │   │   │   ├── NotebookEditPermissionRequest.tsx
│   │   │   │   └── NotebookEditToolDiff.tsx
│   │   │   ├── PowerShellPermissionRequest/
│   │   │   │   ├── PowerShellPermissionRequest.tsx
│   │   │   │   └── powershellToolUseOptions.tsx
│   │   │   ├── rules/
│   │   │   │   ├── AddPermissionRules.tsx
│   │   │   │   ├── AddWorkspaceDirectory.tsx
│   │   │   │   ├── PermissionRuleDescription.tsx
│   │   │   │   ├── PermissionRuleInput.tsx
│   │   │   │   ├── PermissionRuleList.tsx
│   │   │   │   ├── RecentDenialsTab.tsx
│   │   │   │   ├── RemoveWorkspaceDirectory.tsx
│   │   │   │   └── WorkspaceTab.tsx
│   │   │   ├── SedEditPermissionRequest/
│   │   │   │   └── SedEditPermissionRequest.tsx
│   │   │   ├── SkillPermissionRequest/
│   │   │   │   └── SkillPermissionRequest.tsx
│   │   │   ├── WebFetchPermissionRequest/
│   │   │   │   └── WebFetchPermissionRequest.tsx
│   │   │   ├── FallbackPermissionRequest.tsx
│   │   │   ├── hooks.ts
│   │   │   ├── PermissionDecisionDebugInfo.tsx
│   │   │   ├── PermissionDialog.tsx
│   │   │   ├── PermissionExplanation.tsx
│   │   │   ├── PermissionPrompt.tsx
│   │   │   ├── PermissionRequest.tsx
│   │   │   ├── PermissionRequestTitle.tsx
│   │   │   ├── PermissionRuleExplanation.tsx
│   │   │   ├── SandboxPermissionRequest.tsx
│   │   │   ├── shellPermissionHelpers.tsx
│   │   │   ├── useShellPermissionFeedback.ts
│   │   │   ├── utils.ts
│   │   │   ├── WorkerBadge.tsx
│   │   │   └── WorkerPendingPermission.tsx
│   │   ├── PromptInput/
│   │   │   ├── HistorySearchInput.tsx
│   │   │   ├── inputModes.ts
│   │   │   ├── inputPaste.ts
│   │   │   ├── IssueFlagBanner.tsx
│   │   │   ├── Notifications.tsx
│   │   │   ├── PromptInput.tsx
│   │   │   ├── PromptInputFooter.tsx
│   │   │   ├── PromptInputFooterLeftSide.tsx
│   │   │   ├── PromptInputFooterSuggestions.tsx
│   │   │   ├── PromptInputHelpMenu.tsx
│   │   │   ├── PromptInputModeIndicator.tsx
│   │   │   ├── PromptInputQueuedCommands.tsx
│   │   │   ├── PromptInputStashNotice.tsx
│   │   │   ├── SandboxPromptFooterHint.tsx
│   │   │   ├── ShimmeredInput.tsx
│   │   │   ├── useMaybeTruncateInput.ts
│   │   │   ├── usePromptInputPlaceholder.ts
│   │   │   ├── useShowFastIconHint.ts
│   │   │   ├── useSwarmBanner.ts
│   │   │   ├── utils.ts
│   │   │   └── VoiceIndicator.tsx
│   │   ├── sandbox/
│   │   │   ├── SandboxConfigTab.tsx
│   │   │   ├── SandboxDependenciesTab.tsx
│   │   │   ├── SandboxDoctorSection.tsx
│   │   │   ├── SandboxOverridesTab.tsx
│   │   │   └── SandboxSettings.tsx
│   │   ├── Settings/
│   │   │   ├── Config.tsx
│   │   │   ├── Settings.tsx
│   │   │   ├── Status.tsx
│   │   │   └── Usage.tsx
│   │   ├── shell/
│   │   │   ├── ExpandShellOutputContext.tsx
│   │   │   ├── OutputLine.tsx
│   │   │   ├── ShellProgressMessage.tsx
│   │   │   └── ShellTimeDisplay.tsx
│   │   ├── skills/
│   │   │   └── SkillsMenu.tsx
│   │   ├── Spinner/
│   │   │   ├── FlashingChar.tsx
│   │   │   ├── GlimmerMessage.tsx
│   │   │   ├── index.ts
│   │   │   ├── ShimmerChar.tsx
│   │   │   ├── SpinnerAnimationRow.tsx
│   │   │   ├── SpinnerGlyph.tsx
│   │   │   ├── teammateSelectHint.ts
│   │   │   ├── TeammateSpinnerLine.tsx
│   │   │   ├── TeammateSpinnerTree.tsx
│   │   │   ├── useShimmerAnimation.ts
│   │   │   ├── useStalledAnimation.ts
│   │   │   └── utils.ts
│   │   ├── StructuredDiff/
│   │   │   ├── colorDiff.ts
│   │   │   └── Fallback.tsx
│   │   ├── tasks/
│   │   │   ├── AsyncAgentDetailDialog.tsx
│   │   │   ├── BackgroundTask.tsx
│   │   │   ├── BackgroundTasksDialog.tsx
│   │   │   ├── BackgroundTaskStatus.tsx
│   │   │   ├── DreamDetailDialog.tsx
│   │   │   ├── InProcessTeammateDetailDialog.tsx
│   │   │   ├── RemoteSessionDetailDialog.tsx
│   │   │   ├── RemoteSessionProgress.tsx
│   │   │   ├── renderToolActivity.tsx
│   │   │   ├── ShellDetailDialog.tsx
│   │   │   ├── ShellProgress.tsx
│   │   │   └── taskStatusUtils.tsx
│   │   ├── teams/
│   │   │   ├── TeamsDialog.tsx
│   │   │   └── TeamStatus.tsx
│   │   ├── TrustDialog/
│   │   │   ├── TrustDialog.tsx
│   │   │   └── utils.ts
│   │   ├── ui/
│   │   │   ├── OrderedList.tsx
│   │   │   ├── OrderedListItem.tsx
│   │   │   └── TreeSelect.tsx
│   │   ├── wizard/
│   │   │   ├── index.ts
│   │   │   ├── useWizard.ts
│   │   │   ├── WizardDialogLayout.tsx
│   │   │   ├── WizardNavigationFooter.tsx
│   │   │   └── WizardProvider.tsx
│   │   ├── AgentProgressLine.tsx
│   │   ├── App.tsx
│   │   ├── ApproveApiKey.tsx
│   │   ├── AutoModeOptInDialog.tsx
│   │   ├── AutoUpdater.tsx
│   │   ├── AutoUpdaterWrapper.tsx
│   │   ├── AwsAuthStatusBox.tsx
│   │   ├── BaseTextInput.tsx
│   │   ├── BashModeProgress.tsx
│   │   ├── BridgeDialog.tsx
│   │   ├── BypassPermissionsModeDialog.tsx
│   │   ├── ChannelDowngradeDialog.tsx
│   │   ├── ClaudeInChromeOnboarding.tsx
│   │   ├── ClaudeMdExternalIncludesDialog.tsx
│   │   ├── ClickableImageRef.tsx
│   │   ├── CompactSummary.tsx
│   │   ├── ConfigurableShortcutHint.tsx
│   │   ├── ConsoleOAuthFlow.tsx
│   │   ├── ContextSuggestions.tsx
│   │   ├── ContextVisualization.tsx
│   │   ├── CoordinatorAgentStatus.tsx
│   │   ├── CostThresholdDialog.tsx
│   │   ├── CtrlOToExpand.tsx
│   │   ├── DesktopHandoff.tsx
│   │   ├── DevBar.tsx
│   │   ├── DevChannelsDialog.tsx
│   │   ├── DiagnosticsDisplay.tsx
│   │   ├── EffortCallout.tsx
│   │   ├── EffortIndicator.ts
│   │   ├── ExitFlow.tsx
│   │   ├── ExportDialog.tsx
│   │   ├── FallbackToolUseErrorMessage.tsx
│   │   ├── FallbackToolUseRejectedMessage.tsx
│   │   ├── FastIcon.tsx
│   │   ├── Feedback.tsx
│   │   ├── FileEditToolDiff.tsx
│   │   ├── FileEditToolUpdatedMessage.tsx
│   │   ├── FileEditToolUseRejectedMessage.tsx
│   │   ├── FilePathLink.tsx
│   │   ├── FullscreenLayout.tsx
│   │   ├── GlobalSearchDialog.tsx
│   │   ├── HighlightedCode.tsx
│   │   ├── HistorySearchDialog.tsx
│   │   ├── IdeAutoConnectDialog.tsx
│   │   ├── IdeOnboardingDialog.tsx
│   │   ├── IdeStatusIndicator.tsx
│   │   ├── IdleReturnDialog.tsx
│   │   ├── InterruptedByUser.tsx
│   │   ├── InvalidConfigDialog.tsx
│   │   ├── InvalidSettingsDialog.tsx
│   │   ├── KeybindingWarnings.tsx
│   │   ├── LanguagePicker.tsx
│   │   ├── LogSelector.tsx
│   │   ├── Markdown.tsx
│   │   ├── MarkdownTable.tsx
│   │   ├── MCPServerApprovalDialog.tsx
│   │   ├── MCPServerDesktopImportDialog.tsx
│   │   ├── MCPServerDialogCopy.tsx
│   │   ├── MCPServerMultiselectDialog.tsx
│   │   ├── MemoryUsageIndicator.tsx
│   │   ├── Message.tsx
│   │   ├── messageActions.tsx
│   │   ├── MessageModel.tsx
│   │   ├── MessageResponse.tsx
│   │   ├── MessageRow.tsx
│   │   ├── Messages.tsx
│   │   ├── MessageSelector.tsx
│   │   ├── MessageTimestamp.tsx
│   │   ├── ModelPicker.tsx
│   │   ├── NativeAutoUpdater.tsx
│   │   ├── NotebookEditToolUseRejectedMessage.tsx
│   │   ├── OffscreenFreeze.tsx
│   │   ├── Onboarding.tsx
│   │   ├── OutputStylePicker.tsx
│   │   ├── PackageManagerAutoUpdater.tsx
│   │   ├── PrBadge.tsx
│   │   ├── PressEnterToContinue.tsx
│   │   ├── QuickOpenDialog.tsx
│   │   ├── RemoteCallout.tsx
│   │   ├── RemoteEnvironmentDialog.tsx
│   │   ├── ResumeTask.tsx
│   │   ├── SandboxViolationExpandedView.tsx
│   │   ├── ScrollKeybindingHandler.tsx
│   │   ├── SearchBox.tsx
│   │   ├── SentryErrorBoundary.ts
│   │   ├── SessionBackgroundHint.tsx
│   │   ├── SessionPreview.tsx
│   │   ├── ShowInIDEPrompt.tsx
│   │   ├── SkillImprovementSurvey.tsx
│   │   ├── Spinner.tsx
│   │   ├── Stats.tsx
│   │   ├── StatusLine.tsx
│   │   ├── StatusNotices.tsx
│   │   ├── StructuredDiff.tsx
│   │   ├── StructuredDiffList.tsx
│   │   ├── TagTabs.tsx
│   │   ├── TaskListV2.tsx
│   │   ├── TeammateViewHeader.tsx
│   │   ├── TeleportError.tsx
│   │   ├── TeleportProgress.tsx
│   │   ├── TeleportRepoMismatchDialog.tsx
│   │   ├── TeleportResumeWrapper.tsx
│   │   ├── TeleportStash.tsx
│   │   ├── TextInput.tsx
│   │   ├── ThemePicker.tsx
│   │   ├── ThinkingToggle.tsx
│   │   ├── TokenWarning.tsx
│   │   ├── ToolUseLoader.tsx
│   │   ├── ValidationErrorsList.tsx
│   │   ├── VimTextInput.tsx
│   │   ├── VirtualMessageList.tsx
│   │   ├── WorkflowMultiselectDialog.tsx
│   │   └── WorktreeExitDialog.tsx
│   ├── constants/
│   │   ├── apiLimits.ts
│   │   ├── betas.ts
│   │   ├── common.ts
│   │   ├── cyberRiskInstruction.ts
│   │   ├── errorIds.ts
│   │   ├── figures.ts
│   │   ├── files.ts
│   │   ├── github-app.ts
│   │   ├── keys.ts
│   │   ├── messages.ts
│   │   ├── oauth.ts
│   │   ├── outputStyles.ts
│   │   ├── product.ts
│   │   ├── prompts.ts
│   │   ├── spinnerVerbs.ts
│   │   ├── system.ts
│   │   ├── systemPromptSections.ts
│   │   ├── toolLimits.ts
│   │   ├── tools.ts
│   │   ├── turnCompletionVerbs.ts
│   │   └── xml.ts
│   ├── context/
│   │   ├── fpsMetrics.tsx
│   │   ├── mailbox.tsx
│   │   ├── modalContext.tsx
│   │   ├── notifications.tsx
│   │   ├── overlayContext.tsx
│   │   ├── promptOverlayContext.tsx
│   │   ├── QueuedMessageContext.tsx
│   │   ├── stats.tsx
│   │   └── voice.tsx
│   ├── coordinator/
│   │   └── coordinatorMode.ts
│   ├── entrypoints/
│   │   ├── sdk/
│   │   │   ├── controlSchemas.ts
│   │   │   ├── coreSchemas.ts
│   │   │   └── coreTypes.ts
│   │   ├── agentSdkTypes.ts
│   │   ├── cli.tsx
│   │   ├── init.ts
│   │   ├── mcp.ts
│   │   └── sandboxTypes.ts
│   ├── hooks/
│   │   ├── notifs/
│   │   │   ├── useAutoModeUnavailableNotification.ts
│   │   │   ├── useCanSwitchToExistingSubscription.tsx
│   │   │   ├── useDeprecationWarningNotification.tsx
│   │   │   ├── useFastModeNotification.tsx
│   │   │   ├── useIDEStatusIndicator.tsx
│   │   │   ├── useInstallMessages.tsx
│   │   │   ├── useLspInitializationNotification.tsx
│   │   │   ├── useMcpConnectivityStatus.tsx
│   │   │   ├── useModelMigrationNotifications.tsx
│   │   │   ├── useNpmDeprecationNotification.tsx
│   │   │   ├── usePluginAutoupdateNotification.tsx
│   │   │   ├── usePluginInstallationStatus.tsx
│   │   │   ├── useRateLimitWarningNotification.tsx
│   │   │   ├── useSettingsErrors.tsx
│   │   │   ├── useStartupNotification.ts
│   │   │   └── useTeammateShutdownNotification.ts
│   │   ├── toolPermission/
│   │   │   ├── handlers/
│   │   │   │   ├── coordinatorHandler.ts
│   │   │   │   ├── interactiveHandler.ts
│   │   │   │   └── swarmWorkerHandler.ts
│   │   │   ├── PermissionContext.ts
│   │   │   └── permissionLogging.ts
│   │   ├── fileSuggestions.ts
│   │   ├── renderPlaceholder.ts
│   │   ├── unifiedSuggestions.ts
│   │   ├── useAfterFirstRender.ts
│   │   ├── useApiKeyVerification.ts
│   │   ├── useArrowKeyHistory.tsx
│   │   ├── useAssistantHistory.ts
│   │   ├── useAwaySummary.ts
│   │   ├── useBackgroundTaskNavigation.ts
│   │   ├── useBlink.ts
│   │   ├── useCancelRequest.ts
│   │   ├── useCanUseTool.tsx
│   │   ├── useChromeExtensionNotification.tsx
│   │   ├── useClaudeCodeHintRecommendation.tsx
│   │   ├── useClipboardImageHint.ts
│   │   ├── useCommandKeybindings.tsx
│   │   ├── useCommandQueue.ts
│   │   ├── useCopyOnSelect.ts
│   │   ├── useDeferredHookMessages.ts
│   │   ├── useDiffData.ts
│   │   ├── useDiffInIDE.ts
│   │   ├── useDirectConnect.ts
│   │   ├── useDoublePress.ts
│   │   ├── useDynamicConfig.ts
│   │   ├── useElapsedTime.ts
│   │   ├── useExitOnCtrlCD.ts
│   │   ├── useExitOnCtrlCDWithKeybindings.ts
│   │   ├── useFileHistorySnapshotInit.ts
│   │   ├── useGlobalKeybindings.tsx
│   │   ├── useHistorySearch.ts
│   │   ├── useIdeAtMentioned.ts
│   │   ├── useIdeConnectionStatus.ts
│   │   ├── useIDEIntegration.tsx
│   │   ├── useIdeLogging.ts
│   │   ├── useIdeSelection.ts
│   │   ├── useInboxPoller.ts
│   │   ├── useInputBuffer.ts
│   │   ├── useIssueFlagBanner.ts
│   │   ├── useLogMessages.ts
│   │   ├── useLspPluginRecommendation.tsx
│   │   ├── useMailboxBridge.ts
│   │   ├── useMainLoopModel.ts
│   │   ├── useManagePlugins.ts
│   │   ├── useMemoryUsage.ts
│   │   ├── useMergedClients.ts
│   │   ├── useMergedCommands.ts
│   │   ├── useMergedTools.ts
│   │   ├── useMinDisplayTime.ts
│   │   ├── useNotifyAfterTimeout.ts
│   │   ├── useOfficialMarketplaceNotification.tsx
│   │   ├── usePasteHandler.ts
│   │   ├── usePluginRecommendationBase.tsx
│   │   ├── usePromptsFromClaudeInChrome.tsx
│   │   ├── usePromptSuggestion.ts
│   │   ├── usePrStatus.ts
│   │   ├── useQueueProcessor.ts
│   │   ├── useRemoteSession.ts
│   │   ├── useReplBridge.tsx
│   │   ├── useScheduledTasks.ts
│   │   ├── useSearchInput.ts
│   │   ├── useSessionBackgrounding.ts
│   │   ├── useSettings.ts
│   │   ├── useSettingsChange.ts
│   │   ├── useSkillImprovementSurvey.ts
│   │   ├── useSkillsChange.ts
│   │   ├── useSSHSession.ts
│   │   ├── useSwarmInitialization.ts
│   │   ├── useSwarmPermissionPoller.ts
│   │   ├── useTaskListWatcher.ts
│   │   ├── useTasksV2.ts
│   │   ├── useTeammateViewAutoExit.ts
│   │   ├── useTeleportResume.tsx
│   │   ├── useTerminalSize.ts
│   │   ├── useTextInput.ts
│   │   ├── useTimeout.ts
│   │   ├── useTurnDiffs.ts
│   │   ├── useTypeahead.tsx
│   │   ├── useUpdateNotification.ts
│   │   ├── useVimInput.ts
│   │   ├── useVirtualScroll.ts
│   │   ├── useVoice.ts
│   │   ├── useVoiceEnabled.ts
│   │   └── useVoiceIntegration.tsx
│   ├── ink/
│   │   ├── components/
│   │   │   ├── AlternateScreen.tsx
│   │   │   ├── App.tsx
│   │   │   ├── AppContext.ts
│   │   │   ├── Box.tsx
│   │   │   ├── Button.tsx
│   │   │   ├── ClockContext.tsx
│   │   │   ├── CursorDeclarationContext.ts
│   │   │   ├── ErrorOverview.tsx
│   │   │   ├── Link.tsx
│   │   │   ├── Newline.tsx
│   │   │   ├── NoSelect.tsx
│   │   │   ├── RawAnsi.tsx
│   │   │   ├── ScrollBox.tsx
│   │   │   ├── Spacer.tsx
│   │   │   ├── StdinContext.ts
│   │   │   ├── TerminalFocusContext.tsx
│   │   │   ├── TerminalSizeContext.tsx
│   │   │   └── Text.tsx
│   │   ├── events/
│   │   │   ├── click-event.ts
│   │   │   ├── dispatcher.ts
│   │   │   ├── emitter.ts
│   │   │   ├── event-handlers.ts
│   │   │   ├── event.ts
│   │   │   ├── focus-event.ts
│   │   │   ├── input-event.ts
│   │   │   ├── keyboard-event.ts
│   │   │   ├── terminal-event.ts
│   │   │   └── terminal-focus-event.ts
│   │   ├── hooks/
│   │   │   ├── use-animation-frame.ts
│   │   │   ├── use-app.ts
│   │   │   ├── use-declared-cursor.ts
│   │   │   ├── use-input.ts
│   │   │   ├── use-interval.ts
│   │   │   ├── use-search-highlight.ts
│   │   │   ├── use-selection.ts
│   │   │   ├── use-stdin.ts
│   │   │   ├── use-tab-status.ts
│   │   │   ├── use-terminal-focus.ts
│   │   │   ├── use-terminal-title.ts
│   │   │   └── use-terminal-viewport.ts
│   │   ├── layout/
│   │   │   ├── engine.ts
│   │   │   ├── geometry.ts
│   │   │   ├── node.ts
│   │   │   └── yoga.ts
│   │   ├── termio/
│   │   │   ├── ansi.ts
│   │   │   ├── csi.ts
│   │   │   ├── dec.ts
│   │   │   ├── esc.ts
│   │   │   ├── osc.ts
│   │   │   ├── parser.ts
│   │   │   ├── sgr.ts
│   │   │   ├── tokenize.ts
│   │   │   └── types.ts
│   │   ├── Ansi.tsx
│   │   ├── bidi.ts
│   │   ├── clearTerminal.ts
│   │   ├── colorize.ts
│   │   ├── constants.ts
│   │   ├── dom.ts
│   │   ├── focus.ts
│   │   ├── frame.ts
│   │   ├── get-max-width.ts
│   │   ├── hit-test.ts
│   │   ├── ink.tsx
│   │   ├── instances.ts
│   │   ├── line-width-cache.ts
│   │   ├── log-update.ts
│   │   ├── measure-element.ts
│   │   ├── measure-text.ts
│   │   ├── node-cache.ts
│   │   ├── optimizer.ts
│   │   ├── output.ts
│   │   ├── parse-keypress.ts
│   │   ├── reconciler.ts
│   │   ├── render-border.ts
│   │   ├── render-node-to-output.ts
│   │   ├── render-to-screen.ts
│   │   ├── renderer.ts
│   │   ├── root.ts
│   │   ├── screen.ts
│   │   ├── searchHighlight.ts
│   │   ├── selection.ts
│   │   ├── squash-text-nodes.ts
│   │   ├── stringWidth.ts
│   │   ├── styles.ts
│   │   ├── supports-hyperlinks.ts
│   │   ├── tabstops.ts
│   │   ├── terminal-focus-state.ts
│   │   ├── terminal-querier.ts
│   │   ├── terminal.ts
│   │   ├── termio.ts
│   │   ├── useTerminalNotification.ts
│   │   ├── warn.ts
│   │   ├── widest-line.ts
│   │   ├── wrap-text.ts
│   │   └── wrapAnsi.ts
│   ├── keybindings/
│   │   ├── defaultBindings.ts
│   │   ├── KeybindingContext.tsx
│   │   ├── KeybindingProviderSetup.tsx
│   │   ├── loadUserBindings.ts
│   │   ├── match.ts
│   │   ├── parser.ts
│   │   ├── reservedShortcuts.ts
│   │   ├── resolver.ts
│   │   ├── schema.ts
│   │   ├── shortcutFormat.ts
│   │   ├── template.ts
│   │   ├── useKeybinding.ts
│   │   ├── useShortcutDisplay.ts
│   │   └── validate.ts
│   ├── memdir/
│   │   ├── findRelevantMemories.ts
│   │   ├── memdir.ts
│   │   ├── memoryAge.ts
│   │   ├── memoryScan.ts
│   │   ├── memoryTypes.ts
│   │   ├── paths.ts
│   │   ├── teamMemPaths.ts
│   │   └── teamMemPrompts.ts
│   ├── migrations/
│   │   ├── migrateAutoUpdatesToSettings.ts
│   │   ├── migrateBypassPermissionsAcceptedToSettings.ts
│   │   ├── migrateEnableAllProjectMcpServersToSettings.ts
│   │   ├── migrateFennecToOpus.ts
│   │   ├── migrateLegacyOpusToCurrent.ts
│   │   ├── migrateOpusToOpus1m.ts
│   │   ├── migrateReplBridgeEnabledToRemoteControlAtStartup.ts
│   │   ├── migrateSonnet1mToSonnet45.ts
│   │   ├── migrateSonnet45ToSonnet46.ts
│   │   ├── resetAutoModeOptInForDefaultOffer.ts
│   │   └── resetProToOpusDefault.ts
│   ├── moreright/
│   │   └── useMoreRight.tsx
│   ├── native-ts/
│   │   ├── color-diff/
│   │   │   └── index.ts
│   │   ├── file-index/
│   │   │   └── index.ts
│   │   └── yoga-layout/
│   │       ├── enums.ts
│   │       └── index.ts
│   ├── outputStyles/
│   │   └── loadOutputStylesDir.ts
│   ├── plugins/
│   │   ├── bundled/
│   │   │   └── index.ts
│   │   └── builtinPlugins.ts
│   ├── query/
│   │   ├── config.ts
│   │   ├── deps.ts
│   │   ├── stopHooks.ts
│   │   └── tokenBudget.ts
│   ├── remote/
│   │   ├── remotePermissionBridge.ts
│   │   ├── RemoteSessionManager.ts
│   │   ├── sdkMessageAdapter.ts
│   │   └── SessionsWebSocket.ts
│   ├── schemas/
│   │   └── hooks.ts
│   ├── screens/
│   │   ├── Doctor.tsx
│   │   ├── REPL.tsx
│   │   └── ResumeConversation.tsx
│   ├── server/
│   │   ├── createDirectConnectSession.ts
│   │   ├── directConnectManager.ts
│   │   └── types.ts
│   ├── services/
│   │   ├── AgentSummary/
│   │   │   └── agentSummary.ts
│   │   ├── analytics/
│   │   │   ├── config.ts
│   │   │   ├── datadog.ts
│   │   │   ├── firstPartyEventLogger.ts
│   │   │   ├── firstPartyEventLoggingExporter.ts
│   │   │   ├── growthbook.ts
│   │   │   ├── index.ts
│   │   │   ├── metadata.ts
│   │   │   ├── sink.ts
│   │   │   └── sinkKillswitch.ts
│   │   ├── api/
│   │   │   ├── adminRequests.ts
│   │   │   ├── bootstrap.ts
│   │   │   ├── claude.ts
│   │   │   ├── client.ts
│   │   │   ├── dumpPrompts.ts
│   │   │   ├── emptyUsage.ts
│   │   │   ├── errors.ts
│   │   │   ├── errorUtils.ts
│   │   │   ├── filesApi.ts
│   │   │   ├── firstTokenDate.ts
│   │   │   ├── grove.ts
│   │   │   ├── logging.ts
│   │   │   ├── metricsOptOut.ts
│   │   │   ├── overageCreditGrant.ts
│   │   │   ├── promptCacheBreakDetection.ts
│   │   │   ├── referral.ts
│   │   │   ├── sessionIngress.ts
│   │   │   ├── ultrareviewQuota.ts
│   │   │   ├── usage.ts
│   │   │   └── withRetry.ts
│   │   ├── autoDream/
│   │   │   ├── autoDream.ts
│   │   │   ├── config.ts
│   │   │   ├── consolidationLock.ts
│   │   │   └── consolidationPrompt.ts
│   │   ├── compact/
│   │   │   ├── apiMicrocompact.ts
│   │   │   ├── autoCompact.ts
│   │   │   ├── compact.ts
│   │   │   ├── compactWarningHook.ts
│   │   │   ├── compactWarningState.ts
│   │   │   ├── grouping.ts
│   │   │   ├── microCompact.ts
│   │   │   ├── postCompactCleanup.ts
│   │   │   ├── prompt.ts
│   │   │   ├── sessionMemoryCompact.ts
│   │   │   └── timeBasedMCConfig.ts
│   │   ├── extractMemories/
│   │   │   ├── extractMemories.ts
│   │   │   └── prompts.ts
│   │   ├── lsp/
│   │   │   ├── config.ts
│   │   │   ├── LSPClient.ts
│   │   │   ├── LSPDiagnosticRegistry.ts
│   │   │   ├── LSPServerInstance.ts
│   │   │   ├── LSPServerManager.ts
│   │   │   ├── manager.ts
│   │   │   └── passiveFeedback.ts
│   │   ├── MagicDocs/
│   │   │   ├── magicDocs.ts
│   │   │   └── prompts.ts
│   │   ├── mcp/
│   │   │   ├── auth.ts
│   │   │   ├── channelAllowlist.ts
│   │   │   ├── channelNotification.ts
│   │   │   ├── channelPermissions.ts
│   │   │   ├── claudeai.ts
│   │   │   ├── client.ts
│   │   │   ├── config.ts
│   │   │   ├── elicitationHandler.ts
│   │   │   ├── envExpansion.ts
│   │   │   ├── headersHelper.ts
│   │   │   ├── InProcessTransport.ts
│   │   │   ├── MCPConnectionManager.tsx
│   │   │   ├── mcpStringUtils.ts
│   │   │   ├── normalization.ts
│   │   │   ├── oauthPort.ts
│   │   │   ├── officialRegistry.ts
│   │   │   ├── SdkControlTransport.ts
│   │   │   ├── types.ts
│   │   │   ├── useManageMCPConnections.ts
│   │   │   ├── utils.ts
│   │   │   ├── vscodeSdkMcp.ts
│   │   │   ├── xaa.ts
│   │   │   └── xaaIdpLogin.ts
│   │   ├── oauth/
│   │   │   ├── auth-code-listener.ts
│   │   │   ├── client.ts
│   │   │   ├── crypto.ts
│   │   │   ├── getOauthProfile.ts
│   │   │   └── index.ts
│   │   ├── plugins/
│   │   │   ├── pluginCliCommands.ts
│   │   │   ├── PluginInstallationManager.ts
│   │   │   └── pluginOperations.ts
│   │   ├── policyLimits/
│   │   │   ├── index.ts
│   │   │   └── types.ts
│   │   ├── PromptSuggestion/
│   │   │   ├── promptSuggestion.ts
│   │   │   └── speculation.ts
│   │   ├── remoteManagedSettings/
│   │   │   ├── index.ts
│   │   │   ├── securityCheck.tsx
│   │   │   ├── syncCache.ts
│   │   │   ├── syncCacheState.ts
│   │   │   └── types.ts
│   │   ├── SessionMemory/
│   │   │   ├── prompts.ts
│   │   │   ├── sessionMemory.ts
│   │   │   └── sessionMemoryUtils.ts
│   │   ├── settingsSync/
│   │   │   ├── index.ts
│   │   │   └── types.ts
│   │   ├── teamMemorySync/
│   │   │   ├── index.ts
│   │   │   ├── secretScanner.ts
│   │   │   ├── teamMemSecretGuard.ts
│   │   │   ├── types.ts
│   │   │   └── watcher.ts
│   │   ├── tips/
│   │   │   ├── tipHistory.ts
│   │   │   ├── tipRegistry.ts
│   │   │   └── tipScheduler.ts
│   │   ├── tools/
│   │   │   ├── StreamingToolExecutor.ts
│   │   │   ├── toolExecution.ts
│   │   │   ├── toolHooks.ts
│   │   │   └── toolOrchestration.ts
│   │   ├── toolUseSummary/
│   │   │   └── toolUseSummaryGenerator.ts
│   │   ├── awaySummary.ts
│   │   ├── claudeAiLimits.ts
│   │   ├── claudeAiLimitsHook.ts
│   │   ├── diagnosticTracking.ts
│   │   ├── internalLogging.ts
│   │   ├── mcpServerApproval.tsx
│   │   ├── mockRateLimits.ts
│   │   ├── notifier.ts
│   │   ├── preventSleep.ts
│   │   ├── rateLimitMessages.ts
│   │   ├── rateLimitMocking.ts
│   │   ├── tokenEstimation.ts
│   │   ├── vcr.ts
│   │   ├── voice.ts
│   │   ├── voiceKeyterms.ts
│   │   └── voiceStreamSTT.ts
│   ├── skills/
│   │   ├── bundled/
│   │   │   ├── batch.ts
│   │   │   ├── claudeApi.ts
│   │   │   ├── claudeApiContent.ts
│   │   │   ├── claudeInChrome.ts
│   │   │   ├── debug.ts
│   │   │   ├── index.ts
│   │   │   ├── keybindings.ts
│   │   │   ├── loop.ts
│   │   │   ├── loremIpsum.ts
│   │   │   ├── remember.ts
│   │   │   ├── scheduleRemoteAgents.ts
│   │   │   ├── simplify.ts
│   │   │   ├── skillify.ts
│   │   │   ├── stuck.ts
│   │   │   ├── updateConfig.ts
│   │   │   ├── verify.ts
│   │   │   └── verifyContent.ts
│   │   ├── bundledSkills.ts
│   │   ├── loadSkillsDir.ts
│   │   └── mcpSkillBuilders.ts
│   ├── state/
│   │   ├── AppState.tsx
│   │   ├── AppStateStore.ts
│   │   ├── onChangeAppState.ts
│   │   ├── selectors.ts
│   │   ├── store.ts
│   │   └── teammateViewHelpers.ts
│   ├── tasks/
│   │   ├── DreamTask/
│   │   │   └── DreamTask.ts
│   │   ├── InProcessTeammateTask/
│   │   │   ├── InProcessTeammateTask.tsx
│   │   │   └── types.ts
│   │   ├── LocalAgentTask/
│   │   │   └── LocalAgentTask.tsx
│   │   ├── LocalShellTask/
│   │   │   ├── guards.ts
│   │   │   ├── killShellTasks.ts
│   │   │   └── LocalShellTask.tsx
│   │   ├── RemoteAgentTask/
│   │   │   └── RemoteAgentTask.tsx
│   │   ├── LocalMainSessionTask.ts
│   │   ├── pillLabel.ts
│   │   ├── stopTask.ts
│   │   └── types.ts
│   ├── tools/
│   │   ├── AgentTool/
│   │   │   ├── built-in/
│   │   │   │   ├── claudeCodeGuideAgent.ts
│   │   │   │   ├── exploreAgent.ts
│   │   │   │   ├── generalPurposeAgent.ts
│   │   │   │   ├── planAgent.ts
│   │   │   │   ├── statuslineSetup.ts
│   │   │   │   └── verificationAgent.ts
│   │   │   ├── agentColorManager.ts
│   │   │   ├── agentDisplay.ts
│   │   │   ├── agentMemory.ts
│   │   │   ├── agentMemorySnapshot.ts
│   │   │   ├── AgentTool.tsx
│   │   │   ├── agentToolUtils.ts
│   │   │   ├── builtInAgents.ts
│   │   │   ├── constants.ts
│   │   │   ├── forkSubagent.ts
│   │   │   ├── loadAgentsDir.ts
│   │   │   ├── prompt.ts
│   │   │   ├── resumeAgent.ts
│   │   │   ├── runAgent.ts
│   │   │   └── UI.tsx
│   │   ├── AskUserQuestionTool/
│   │   │   ├── AskUserQuestionTool.tsx
│   │   │   └── prompt.ts
│   │   ├── BashTool/
│   │   │   ├── bashCommandHelpers.ts
│   │   │   ├── bashPermissions.ts
│   │   │   ├── bashSecurity.ts
│   │   │   ├── BashTool.tsx
│   │   │   ├── BashToolResultMessage.tsx
│   │   │   ├── commandSemantics.ts
│   │   │   ├── commentLabel.ts
│   │   │   ├── destructiveCommandWarning.ts
│   │   │   ├── modeValidation.ts
│   │   │   ├── pathValidation.ts
│   │   │   ├── prompt.ts
│   │   │   ├── readOnlyValidation.ts
│   │   │   ├── sedEditParser.ts
│   │   │   ├── sedValidation.ts
│   │   │   ├── shouldUseSandbox.ts
│   │   │   ├── toolName.ts
│   │   │   ├── UI.tsx
│   │   │   └── utils.ts
│   │   ├── BriefTool/
│   │   │   ├── attachments.ts
│   │   │   ├── BriefTool.ts
│   │   │   ├── prompt.ts
│   │   │   ├── UI.tsx
│   │   │   └── upload.ts
│   │   ├── ConfigTool/
│   │   │   ├── ConfigTool.ts
│   │   │   ├── constants.ts
│   │   │   ├── prompt.ts
│   │   │   ├── supportedSettings.ts
│   │   │   └── UI.tsx
│   │   ├── EnterPlanModeTool/
│   │   │   ├── constants.ts
│   │   │   ├── EnterPlanModeTool.ts
│   │   │   ├── prompt.ts
│   │   │   └── UI.tsx
│   │   ├── EnterWorktreeTool/
│   │   │   ├── constants.ts
│   │   │   ├── EnterWorktreeTool.ts
│   │   │   ├── prompt.ts
│   │   │   └── UI.tsx
│   │   ├── ExitPlanModeTool/
│   │   │   ├── constants.ts
│   │   │   ├── ExitPlanModeV2Tool.ts
│   │   │   ├── prompt.ts
│   │   │   └── UI.tsx
│   │   ├── ExitWorktreeTool/
│   │   │   ├── constants.ts
│   │   │   ├── ExitWorktreeTool.ts
│   │   │   ├── prompt.ts
│   │   │   └── UI.tsx
│   │   ├── FileEditTool/
│   │   │   ├── constants.ts
│   │   │   ├── FileEditTool.ts
│   │   │   ├── prompt.ts
│   │   │   ├── types.ts
│   │   │   ├── UI.tsx
│   │   │   └── utils.ts
│   │   ├── FileReadTool/
│   │   │   ├── FileReadTool.ts
│   │   │   ├── imageProcessor.ts
│   │   │   ├── limits.ts
│   │   │   ├── prompt.ts
│   │   │   └── UI.tsx
│   │   ├── FileWriteTool/
│   │   │   ├── FileWriteTool.ts
│   │   │   ├── prompt.ts
│   │   │   └── UI.tsx
│   │   ├── GlobTool/
│   │   │   ├── GlobTool.ts
│   │   │   ├── prompt.ts
│   │   │   └── UI.tsx
│   │   ├── GrepTool/
│   │   │   ├── GrepTool.ts
│   │   │   ├── prompt.ts
│   │   │   └── UI.tsx
│   │   ├── ListMcpResourcesTool/
│   │   │   ├── ListMcpResourcesTool.ts
│   │   │   ├── prompt.ts
│   │   │   └── UI.tsx
│   │   ├── LSPTool/
│   │   │   ├── formatters.ts
│   │   │   ├── LSPTool.ts
│   │   │   ├── prompt.ts
│   │   │   ├── schemas.ts
│   │   │   ├── symbolContext.ts
│   │   │   └── UI.tsx
│   │   ├── McpAuthTool/
│   │   │   └── McpAuthTool.ts
│   │   ├── MCPTool/
│   │   │   ├── classifyForCollapse.ts
│   │   │   ├── MCPTool.ts
│   │   │   ├── prompt.ts
│   │   │   └── UI.tsx
│   │   ├── NotebookEditTool/
│   │   │   ├── constants.ts
│   │   │   ├── NotebookEditTool.ts
│   │   │   ├── prompt.ts
│   │   │   └── UI.tsx
│   │   ├── PowerShellTool/
│   │   │   ├── clmTypes.ts
│   │   │   ├── commandSemantics.ts
│   │   │   ├── commonParameters.ts
│   │   │   ├── destructiveCommandWarning.ts
│   │   │   ├── gitSafety.ts
│   │   │   ├── modeValidation.ts
│   │   │   ├── pathValidation.ts
│   │   │   ├── powershellPermissions.ts
│   │   │   ├── powershellSecurity.ts
│   │   │   ├── PowerShellTool.tsx
│   │   │   ├── prompt.ts
│   │   │   ├── readOnlyValidation.ts
│   │   │   ├── toolName.ts
│   │   │   └── UI.tsx
│   │   ├── ReadMcpResourceTool/
│   │   │   ├── prompt.ts
│   │   │   ├── ReadMcpResourceTool.ts
│   │   │   └── UI.tsx
│   │   ├── RemoteTriggerTool/
│   │   │   ├── prompt.ts
│   │   │   ├── RemoteTriggerTool.ts
│   │   │   └── UI.tsx
│   │   ├── REPLTool/
│   │   │   ├── constants.ts
│   │   │   └── primitiveTools.ts
│   │   ├── ScheduleCronTool/
│   │   │   ├── CronCreateTool.ts
│   │   │   ├── CronDeleteTool.ts
│   │   │   ├── CronListTool.ts
│   │   │   ├── prompt.ts
│   │   │   └── UI.tsx
│   │   ├── SendMessageTool/
│   │   │   ├── constants.ts
│   │   │   ├── prompt.ts
│   │   │   ├── SendMessageTool.ts
│   │   │   └── UI.tsx
│   │   ├── shared/
│   │   │   ├── gitOperationTracking.ts
│   │   │   └── spawnMultiAgent.ts
│   │   ├── SkillTool/
│   │   │   ├── constants.ts
│   │   │   ├── prompt.ts
│   │   │   ├── SkillTool.ts
│   │   │   └── UI.tsx
│   │   ├── SleepTool/
│   │   │   └── prompt.ts
│   │   ├── SyntheticOutputTool/
│   │   │   └── SyntheticOutputTool.ts
│   │   ├── TaskCreateTool/
│   │   │   ├── constants.ts
│   │   │   ├── prompt.ts
│   │   │   └── TaskCreateTool.ts
│   │   ├── TaskGetTool/
│   │   │   ├── constants.ts
│   │   │   ├── prompt.ts
│   │   │   └── TaskGetTool.ts
│   │   ├── TaskListTool/
│   │   │   ├── constants.ts
│   │   │   ├── prompt.ts
│   │   │   └── TaskListTool.ts
│   │   ├── TaskOutputTool/
│   │   │   ├── constants.ts
│   │   │   └── TaskOutputTool.tsx
│   │   ├── TaskStopTool/
│   │   │   ├── prompt.ts
│   │   │   ├── TaskStopTool.ts
│   │   │   └── UI.tsx
│   │   ├── TaskUpdateTool/
│   │   │   ├── constants.ts
│   │   │   ├── prompt.ts
│   │   │   └── TaskUpdateTool.ts
│   │   ├── TeamCreateTool/
│   │   │   ├── constants.ts
│   │   │   ├── prompt.ts
│   │   │   ├── TeamCreateTool.ts
│   │   │   └── UI.tsx
│   │   ├── TeamDeleteTool/
│   │   │   ├── constants.ts
│   │   │   ├── prompt.ts
│   │   │   ├── TeamDeleteTool.ts
│   │   │   └── UI.tsx
│   │   ├── testing/
│   │   │   └── TestingPermissionTool.tsx
│   │   ├── TodoWriteTool/
│   │   │   ├── constants.ts
│   │   │   ├── prompt.ts
│   │   │   └── TodoWriteTool.ts
│   │   ├── ToolSearchTool/
│   │   │   ├── constants.ts
│   │   │   ├── prompt.ts
│   │   │   └── ToolSearchTool.ts
│   │   ├── WebFetchTool/
│   │   │   ├── preapproved.ts
│   │   │   ├── prompt.ts
│   │   │   ├── UI.tsx
│   │   │   ├── utils.ts
│   │   │   └── WebFetchTool.ts
│   │   ├── WebSearchTool/
│   │   │   ├── prompt.ts
│   │   │   ├── UI.tsx
│   │   │   └── WebSearchTool.ts
│   │   └── utils.ts
│   ├── types/
│   │   ├── generated/
│   │   │   ├── events_mono/
│   │   │   │   ├── claude_code/
│   │   │   │   │   └── v1/
│   │   │   │   │       └── claude_code_internal_event.ts
│   │   │   │   ├── common/
│   │   │   │   │   └── v1/
│   │   │   │   │       └── auth.ts
│   │   │   │   └── growthbook/
│   │   │   │       └── v1/
│   │   │   │           └── growthbook_experiment_event.ts
│   │   │   └── google/
│   │   │       └── protobuf/
│   │   │           └── timestamp.ts
│   │   ├── command.ts
│   │   ├── hooks.ts
│   │   ├── ids.ts
│   │   ├── logs.ts
│   │   ├── permissions.ts
│   │   ├── plugin.ts
│   │   └── textInputTypes.ts
│   ├── upstreamproxy/
│   │   ├── relay.ts
│   │   └── upstreamproxy.ts
│   ├── utils/
│   │   ├── background/
│   │   │   └── remote/
│   │   │       ├── preconditions.ts
│   │   │       └── remoteSession.ts
│   │   ├── bash/
│   │   │   ├── specs/
│   │   │   │   ├── alias.ts
│   │   │   │   ├── index.ts
│   │   │   │   ├── nohup.ts
│   │   │   │   ├── pyright.ts
│   │   │   │   ├── sleep.ts
│   │   │   │   ├── srun.ts
│   │   │   │   ├── time.ts
│   │   │   │   └── timeout.ts
│   │   │   ├── ast.ts
│   │   │   ├── bashParser.ts
│   │   │   ├── bashPipeCommand.ts
│   │   │   ├── commands.ts
│   │   │   ├── heredoc.ts
│   │   │   ├── ParsedCommand.ts
│   │   │   ├── parser.ts
│   │   │   ├── prefix.ts
│   │   │   ├── registry.ts
│   │   │   ├── shellCompletion.ts
│   │   │   ├── shellPrefix.ts
│   │   │   ├── shellQuote.ts
│   │   │   ├── shellQuoting.ts
│   │   │   ├── ShellSnapshot.ts
│   │   │   └── treeSitterAnalysis.ts
│   │   ├── claudeInChrome/
│   │   │   ├── chromeNativeHost.ts
│   │   │   ├── common.ts
│   │   │   ├── mcpServer.ts
│   │   │   ├── prompt.ts
│   │   │   ├── setup.ts
│   │   │   ├── setupPortable.ts
│   │   │   └── toolRendering.tsx
│   │   ├── computerUse/
│   │   │   ├── appNames.ts
│   │   │   ├── cleanup.ts
│   │   │   ├── common.ts
│   │   │   ├── computerUseLock.ts
│   │   │   ├── drainRunLoop.ts
│   │   │   ├── escHotkey.ts
│   │   │   ├── executor.ts
│   │   │   ├── gates.ts
│   │   │   ├── hostAdapter.ts
│   │   │   ├── inputLoader.ts
│   │   │   ├── mcpServer.ts
│   │   │   ├── setup.ts
│   │   │   ├── swiftLoader.ts
│   │   │   ├── toolRendering.tsx
│   │   │   └── wrapper.tsx
│   │   ├── deepLink/
│   │   │   ├── banner.ts
│   │   │   ├── parseDeepLink.ts
│   │   │   ├── protocolHandler.ts
│   │   │   ├── registerProtocol.ts
│   │   │   ├── terminalLauncher.ts
│   │   │   └── terminalPreference.ts
│   │   ├── dxt/
│   │   │   ├── helpers.ts
│   │   │   └── zip.ts
│   │   ├── filePersistence/
│   │   │   ├── filePersistence.ts
│   │   │   └── outputsScanner.ts
│   │   ├── git/
│   │   │   ├── gitConfigParser.ts
│   │   │   ├── gitFilesystem.ts
│   │   │   └── gitignore.ts
│   │   ├── github/
│   │   │   └── ghAuthStatus.ts
│   │   ├── hooks/
│   │   │   ├── apiQueryHookHelper.ts
│   │   │   ├── AsyncHookRegistry.ts
│   │   │   ├── execAgentHook.ts
│   │   │   ├── execHttpHook.ts
│   │   │   ├── execPromptHook.ts
│   │   │   ├── fileChangedWatcher.ts
│   │   │   ├── hookEvents.ts
│   │   │   ├── hookHelpers.ts
│   │   │   ├── hooksConfigManager.ts
│   │   │   ├── hooksConfigSnapshot.ts
│   │   │   ├── hooksSettings.ts
│   │   │   ├── postSamplingHooks.ts
│   │   │   ├── registerFrontmatterHooks.ts
│   │   │   ├── registerSkillHooks.ts
│   │   │   ├── sessionHooks.ts
│   │   │   ├── skillImprovement.ts
│   │   │   └── ssrfGuard.ts
│   │   ├── mcp/
│   │   │   ├── dateTimeParser.ts
│   │   │   └── elicitationValidation.ts
│   │   ├── memory/
│   │   │   ├── types.ts
│   │   │   └── versions.ts
│   │   ├── messages/
│   │   │   ├── mappers.ts
│   │   │   └── systemInit.ts
│   │   ├── model/
│   │   │   ├── agent.ts
│   │   │   ├── aliases.ts
│   │   │   ├── antModels.ts
│   │   │   ├── bedrock.ts
│   │   │   ├── check1mAccess.ts
│   │   │   ├── configs.ts
│   │   │   ├── contextWindowUpgradeCheck.ts
│   │   │   ├── deprecation.ts
│   │   │   ├── model.ts
│   │   │   ├── modelAllowlist.ts
│   │   │   ├── modelCapabilities.ts
│   │   │   ├── modelOptions.ts
│   │   │   ├── modelStrings.ts
│   │   │   ├── modelSupportOverrides.ts
│   │   │   ├── providers.ts
│   │   │   └── validateModel.ts
│   │   ├── nativeInstaller/
│   │   │   ├── download.ts
│   │   │   ├── index.ts
│   │   │   ├── installer.ts
│   │   │   ├── packageManagers.ts
│   │   │   └── pidLock.ts
│   │   ├── permissions/
│   │   │   ├── autoModeState.ts
│   │   │   ├── bashClassifier.ts
│   │   │   ├── bypassPermissionsKillswitch.ts
│   │   │   ├── classifierDecision.ts
│   │   │   ├── classifierShared.ts
│   │   │   ├── dangerousPatterns.ts
│   │   │   ├── denialTracking.ts
│   │   │   ├── filesystem.ts
│   │   │   ├── getNextPermissionMode.ts
│   │   │   ├── pathValidation.ts
│   │   │   ├── permissionExplainer.ts
│   │   │   ├── PermissionMode.ts
│   │   │   ├── PermissionPromptToolResultSchema.ts
│   │   │   ├── PermissionResult.ts
│   │   │   ├── PermissionRule.ts
│   │   │   ├── permissionRuleParser.ts
│   │   │   ├── permissions.ts
│   │   │   ├── permissionSetup.ts
│   │   │   ├── permissionsLoader.ts
│   │   │   ├── PermissionUpdate.ts
│   │   │   ├── PermissionUpdateSchema.ts
│   │   │   ├── shadowedRuleDetection.ts
│   │   │   ├── shellRuleMatching.ts
│   │   │   └── yoloClassifier.ts
│   │   ├── plugins/
│   │   │   ├── addDirPluginSettings.ts
│   │   │   ├── cacheUtils.ts
│   │   │   ├── dependencyResolver.ts
│   │   │   ├── fetchTelemetry.ts
│   │   │   ├── gitAvailability.ts
│   │   │   ├── headlessPluginInstall.ts
│   │   │   ├── hintRecommendation.ts
│   │   │   ├── installCounts.ts
│   │   │   ├── installedPluginsManager.ts
│   │   │   ├── loadPluginAgents.ts
│   │   │   ├── loadPluginCommands.ts
│   │   │   ├── loadPluginHooks.ts
│   │   │   ├── loadPluginOutputStyles.ts
│   │   │   ├── lspPluginIntegration.ts
│   │   │   ├── lspRecommendation.ts
│   │   │   ├── managedPlugins.ts
│   │   │   ├── marketplaceHelpers.ts
│   │   │   ├── marketplaceManager.ts
│   │   │   ├── mcpbHandler.ts
│   │   │   ├── mcpPluginIntegration.ts
│   │   │   ├── officialMarketplace.ts
│   │   │   ├── officialMarketplaceGcs.ts
│   │   │   ├── officialMarketplaceStartupCheck.ts
│   │   │   ├── orphanedPluginFilter.ts
│   │   │   ├── parseMarketplaceInput.ts
│   │   │   ├── performStartupChecks.tsx
│   │   │   ├── pluginAutoupdate.ts
│   │   │   ├── pluginBlocklist.ts
│   │   │   ├── pluginDirectories.ts
│   │   │   ├── pluginFlagging.ts
│   │   │   ├── pluginIdentifier.ts
│   │   │   ├── pluginInstallationHelpers.ts
│   │   │   ├── pluginLoader.ts
│   │   │   ├── pluginOptionsStorage.ts
│   │   │   ├── pluginPolicy.ts
│   │   │   ├── pluginStartupCheck.ts
│   │   │   ├── pluginVersioning.ts
│   │   │   ├── reconciler.ts
│   │   │   ├── refresh.ts
│   │   │   ├── schemas.ts
│   │   │   ├── validatePlugin.ts
│   │   │   ├── walkPluginMarkdown.ts
│   │   │   ├── zipCache.ts
│   │   │   └── zipCacheAdapters.ts
│   │   ├── powershell/
│   │   │   ├── dangerousCmdlets.ts
│   │   │   ├── parser.ts
│   │   │   └── staticPrefix.ts
│   │   ├── processUserInput/
│   │   │   ├── processBashCommand.tsx
│   │   │   ├── processSlashCommand.tsx
│   │   │   ├── processTextPrompt.ts
│   │   │   └── processUserInput.ts
│   │   ├── sandbox/
│   │   │   ├── sandbox-adapter.ts
│   │   │   └── sandbox-ui-utils.ts
│   │   ├── secureStorage/
│   │   │   ├── fallbackStorage.ts
│   │   │   ├── index.ts
│   │   │   ├── keychainPrefetch.ts
│   │   │   ├── macOsKeychainHelpers.ts
│   │   │   ├── macOsKeychainStorage.ts
│   │   │   └── plainTextStorage.ts
│   │   ├── settings/
│   │   │   ├── mdm/
│   │   │   │   ├── constants.ts
│   │   │   │   ├── rawRead.ts
│   │   │   │   └── settings.ts
│   │   │   ├── allErrors.ts
│   │   │   ├── applySettingsChange.ts
│   │   │   ├── changeDetector.ts
│   │   │   ├── constants.ts
│   │   │   ├── internalWrites.ts
│   │   │   ├── managedPath.ts
│   │   │   ├── permissionValidation.ts
│   │   │   ├── pluginOnlyPolicy.ts
│   │   │   ├── schemaOutput.ts
│   │   │   ├── settings.ts
│   │   │   ├── settingsCache.ts
│   │   │   ├── toolValidationConfig.ts
│   │   │   ├── types.ts
│   │   │   ├── validateEditTool.ts
│   │   │   ├── validation.ts
│   │   │   └── validationTips.ts
│   │   ├── shell/
│   │   │   ├── bashProvider.ts
│   │   │   ├── outputLimits.ts
│   │   │   ├── powershellDetection.ts
│   │   │   ├── powershellProvider.ts
│   │   │   ├── prefix.ts
│   │   │   ├── readOnlyCommandValidation.ts
│   │   │   ├── resolveDefaultShell.ts
│   │   │   ├── shellProvider.ts
│   │   │   ├── shellToolUtils.ts
│   │   │   └── specPrefix.ts
│   │   ├── skills/
│   │   │   └── skillChangeDetector.ts
│   │   ├── suggestions/
│   │   │   ├── commandSuggestions.ts
│   │   │   ├── directoryCompletion.ts
│   │   │   ├── shellHistoryCompletion.ts
│   │   │   ├── skillUsageTracking.ts
│   │   │   └── slackChannelSuggestions.ts
│   │   ├── swarm/
│   │   │   ├── backends/
│   │   │   │   ├── detection.ts
│   │   │   │   ├── InProcessBackend.ts
│   │   │   │   ├── it2Setup.ts
│   │   │   │   ├── ITermBackend.ts
│   │   │   │   ├── PaneBackendExecutor.ts
│   │   │   │   ├── registry.ts
│   │   │   │   ├── teammateModeSnapshot.ts
│   │   │   │   ├── TmuxBackend.ts
│   │   │   │   └── types.ts
│   │   │   ├── constants.ts
│   │   │   ├── inProcessRunner.ts
│   │   │   ├── It2SetupPrompt.tsx
│   │   │   ├── leaderPermissionBridge.ts
│   │   │   ├── permissionSync.ts
│   │   │   ├── reconnection.ts
│   │   │   ├── spawnInProcess.ts
│   │   │   ├── spawnUtils.ts
│   │   │   ├── teamHelpers.ts
│   │   │   ├── teammateInit.ts
│   │   │   ├── teammateLayoutManager.ts
│   │   │   ├── teammateModel.ts
│   │   │   └── teammatePromptAddendum.ts
│   │   ├── task/
│   │   │   ├── diskOutput.ts
│   │   │   ├── framework.ts
│   │   │   ├── outputFormatting.ts
│   │   │   ├── sdkProgress.ts
│   │   │   └── TaskOutput.ts
│   │   ├── telemetry/
│   │   │   ├── betaSessionTracing.ts
│   │   │   ├── bigqueryExporter.ts
│   │   │   ├── events.ts
│   │   │   ├── instrumentation.ts
│   │   │   ├── logger.ts
│   │   │   ├── perfettoTracing.ts
│   │   │   ├── pluginTelemetry.ts
│   │   │   ├── sessionTracing.ts
│   │   │   └── skillLoadedEvent.ts
│   │   ├── teleport/
│   │   │   ├── api.ts
│   │   │   ├── environments.ts
│   │   │   ├── environmentSelection.ts
│   │   │   └── gitBundle.ts
│   │   ├── todo/
│   │   │   └── types.ts
│   │   ├── ultraplan/
│   │   │   ├── ccrSession.ts
│   │   │   └── keyword.ts
│   │   ├── abortController.ts
│   │   ├── activityManager.ts
│   │   ├── advisor.ts
│   │   ├── agentContext.ts
│   │   ├── agenticSessionSearch.ts
│   │   ├── agentId.ts
│   │   ├── agentSwarmsEnabled.ts
│   │   ├── analyzeContext.ts
│   │   ├── ansiToPng.ts
│   │   ├── ansiToSvg.ts
│   │   ├── api.ts
│   │   ├── apiPreconnect.ts
│   │   ├── appleTerminalBackup.ts
│   │   ├── argumentSubstitution.ts
│   │   ├── array.ts
│   │   ├── asciicast.ts
│   │   ├── attachments.ts
│   │   ├── attribution.ts
│   │   ├── auth.ts
│   │   ├── authFileDescriptor.ts
│   │   ├── authPortable.ts
│   │   ├── autoModeDenials.ts
│   │   ├── autoRunIssue.tsx
│   │   ├── autoUpdater.ts
│   │   ├── aws.ts
│   │   ├── awsAuthStatusManager.ts
│   │   ├── backgroundHousekeeping.ts
│   │   ├── betas.ts
│   │   ├── billing.ts
│   │   ├── binaryCheck.ts
│   │   ├── browser.ts
│   │   ├── bufferedWriter.ts
│   │   ├── bundledMode.ts
│   │   ├── caCerts.ts
│   │   ├── caCertsConfig.ts
│   │   ├── cachePaths.ts
│   │   ├── CircularBuffer.ts
│   │   ├── classifierApprovals.ts
│   │   ├── classifierApprovalsHook.ts
│   │   ├── claudeCodeHints.ts
│   │   ├── claudeDesktop.ts
│   │   ├── claudemd.ts
│   │   ├── cleanup.ts
│   │   ├── cleanupRegistry.ts
│   │   ├── cliArgs.ts
│   │   ├── cliHighlight.ts
│   │   ├── codeIndexing.ts
│   │   ├── collapseBackgroundBashNotifications.ts
│   │   ├── collapseHookSummaries.ts
│   │   ├── collapseReadSearch.ts
│   │   ├── collapseTeammateShutdowns.ts
│   │   ├── combinedAbortSignal.ts
│   │   ├── commandLifecycle.ts
│   │   ├── commitAttribution.ts
│   │   ├── completionCache.ts
│   │   ├── concurrentSessions.ts
│   │   ├── config.ts
│   │   ├── configConstants.ts
│   │   ├── contentArray.ts
│   │   ├── context.ts
│   │   ├── contextAnalysis.ts
│   │   ├── contextSuggestions.ts
│   │   ├── controlMessageCompat.ts
│   │   ├── conversationRecovery.ts
│   │   ├── cron.ts
│   │   ├── cronJitterConfig.ts
│   │   ├── cronScheduler.ts
│   │   ├── cronTasks.ts
│   │   ├── cronTasksLock.ts
│   │   ├── crossProjectResume.ts
│   │   ├── crypto.ts
│   │   ├── Cursor.ts
│   │   ├── cwd.ts
│   │   ├── debug.ts
│   │   ├── debugFilter.ts
│   │   ├── desktopDeepLink.ts
│   │   ├── detectRepository.ts
│   │   ├── diagLogs.ts
│   │   ├── diff.ts
│   │   ├── directMemberMessage.ts
│   │   ├── displayTags.ts
│   │   ├── doctorContextWarnings.ts
│   │   ├── doctorDiagnostic.ts
│   │   ├── earlyInput.ts
│   │   ├── editor.ts
│   │   ├── effort.ts
│   │   ├── embeddedTools.ts
│   │   ├── env.ts
│   │   ├── envDynamic.ts
│   │   ├── envUtils.ts
│   │   ├── envValidation.ts
│   │   ├── errorLogSink.ts
│   │   ├── errors.ts
│   │   ├── exampleCommands.ts
│   │   ├── execFileNoThrow.ts
│   │   ├── execFileNoThrowPortable.ts
│   │   ├── execSyncWrapper.ts
│   │   ├── exportRenderer.tsx
│   │   ├── extraUsage.ts
│   │   ├── fastMode.ts
│   │   ├── file.ts
│   │   ├── fileHistory.ts
│   │   ├── fileOperationAnalytics.ts
│   │   ├── fileRead.ts
│   │   ├── fileReadCache.ts
│   │   ├── fileStateCache.ts
│   │   ├── findExecutable.ts
│   │   ├── fingerprint.ts
│   │   ├── forkedAgent.ts
│   │   ├── format.ts
│   │   ├── formatBriefTimestamp.ts
│   │   ├── fpsTracker.ts
│   │   ├── frontmatterParser.ts
│   │   ├── fsOperations.ts
│   │   ├── fullscreen.ts
│   │   ├── generatedFiles.ts
│   │   ├── generators.ts
│   │   ├── genericProcessUtils.ts
│   │   ├── getWorktreePaths.ts
│   │   ├── getWorktreePathsPortable.ts
│   │   ├── ghPrStatus.ts
│   │   ├── git.ts
│   │   ├── gitDiff.ts
│   │   ├── githubRepoPathMapping.ts
│   │   ├── gitSettings.ts
│   │   ├── glob.ts
│   │   ├── gracefulShutdown.ts
│   │   ├── groupToolUses.ts
│   │   ├── handlePromptSubmit.ts
│   │   ├── hash.ts
│   │   ├── headlessProfiler.ts
│   │   ├── heapDumpService.ts
│   │   ├── heatmap.ts
│   │   ├── highlightMatch.tsx
│   │   ├── hooks.ts
│   │   ├── horizontalScroll.ts
│   │   ├── http.ts
│   │   ├── hyperlink.ts
│   │   ├── ide.ts
│   │   ├── idePathConversion.ts
│   │   ├── idleTimeout.ts
│   │   ├── imagePaste.ts
│   │   ├── imageResizer.ts
│   │   ├── imageStore.ts
│   │   ├── imageValidation.ts
│   │   ├── immediateCommand.ts
│   │   ├── ink.ts
│   │   ├── inProcessTeammateHelpers.ts
│   │   ├── intl.ts
│   │   ├── iTermBackup.ts
│   │   ├── jetbrains.ts
│   │   ├── json.ts
│   │   ├── jsonRead.ts
│   │   ├── keyboardShortcuts.ts
│   │   ├── lazySchema.ts
│   │   ├── listSessionsImpl.ts
│   │   ├── localInstaller.ts
│   │   ├── lockfile.ts
│   │   ├── log.ts
│   │   ├── logoV2Utils.ts
│   │   ├── mailbox.ts
│   │   ├── managedEnv.ts
│   │   ├── managedEnvConstants.ts
│   │   ├── markdown.ts
│   │   ├── markdownConfigLoader.ts
│   │   ├── mcpInstructionsDelta.ts
│   │   ├── mcpOutputStorage.ts
│   │   ├── mcpValidation.ts
│   │   ├── mcpWebSocketTransport.ts
│   │   ├── memoize.ts
│   │   ├── memoryFileDetection.ts
│   │   ├── messagePredicates.ts
│   │   ├── messageQueueManager.ts
│   │   ├── messages.ts
│   │   ├── modelCost.ts
│   │   ├── modifiers.ts
│   │   ├── mtls.ts
│   │   ├── notebook.ts
│   │   ├── objectGroupBy.ts
│   │   ├── pasteStore.ts
│   │   ├── path.ts
│   │   ├── pdf.ts
│   │   ├── pdfUtils.ts
│   │   ├── peerAddress.ts
│   │   ├── planModeV2.ts
│   │   ├── plans.ts
│   │   ├── platform.ts
│   │   ├── preflightChecks.tsx
│   │   ├── privacyLevel.ts
│   │   ├── process.ts
│   │   ├── profilerBase.ts
│   │   ├── promptCategory.ts
│   │   ├── promptEditor.ts
│   │   ├── promptShellExecution.ts
│   │   ├── proxy.ts
│   │   ├── queryContext.ts
│   │   ├── QueryGuard.ts
│   │   ├── queryHelpers.ts
│   │   ├── queryProfiler.ts
│   │   ├── queueProcessor.ts
│   │   ├── readEditContext.ts
│   │   ├── readFileInRange.ts
│   │   ├── releaseNotes.ts
│   │   ├── renderOptions.ts
│   │   ├── ripgrep.ts
│   │   ├── sanitization.ts
│   │   ├── screenshotClipboard.ts
│   │   ├── sdkEventQueue.ts
│   │   ├── semanticBoolean.ts
│   │   ├── semanticNumber.ts
│   │   ├── semver.ts
│   │   ├── sequential.ts
│   │   ├── sessionActivity.ts
│   │   ├── sessionEnvironment.ts
│   │   ├── sessionEnvVars.ts
│   │   ├── sessionFileAccessHooks.ts
│   │   ├── sessionIngressAuth.ts
│   │   ├── sessionRestore.ts
│   │   ├── sessionStart.ts
│   │   ├── sessionState.ts
│   │   ├── sessionStorage.ts
│   │   ├── sessionStoragePortable.ts
│   │   ├── sessionTitle.ts
│   │   ├── sessionUrl.ts
│   │   ├── set.ts
│   │   ├── Shell.ts
│   │   ├── ShellCommand.ts
│   │   ├── shellConfig.ts
│   │   ├── sideQuery.ts
│   │   ├── sideQuestion.ts
│   │   ├── signal.ts
│   │   ├── sinks.ts
│   │   ├── slashCommandParsing.ts
│   │   ├── sleep.ts
│   │   ├── sliceAnsi.ts
│   │   ├── slowOperations.ts
│   │   ├── standaloneAgent.ts
│   │   ├── startupProfiler.ts
│   │   ├── staticRender.tsx
│   │   ├── stats.ts
│   │   ├── statsCache.ts
│   │   ├── status.tsx
│   │   ├── statusNoticeDefinitions.tsx
│   │   ├── statusNoticeHelpers.ts
│   │   ├── stream.ts
│   │   ├── streamJsonStdoutGuard.ts
│   │   ├── streamlinedTransform.ts
│   │   ├── stringUtils.ts
│   │   ├── subprocessEnv.ts
│   │   ├── systemDirectories.ts
│   │   ├── systemPrompt.ts
│   │   ├── systemPromptType.ts
│   │   ├── systemTheme.ts
│   │   ├── taggedId.ts
│   │   ├── tasks.ts
│   │   ├── teamDiscovery.ts
│   │   ├── teammate.ts
│   │   ├── teammateContext.ts
│   │   ├── teammateMailbox.ts
│   │   ├── teamMemoryOps.ts
│   │   ├── telemetryAttributes.ts
│   │   ├── teleport.tsx
│   │   ├── tempfile.ts
│   │   ├── terminal.ts
│   │   ├── terminalPanel.ts
│   │   ├── textHighlighting.ts
│   │   ├── theme.ts
│   │   ├── thinking.ts
│   │   ├── timeouts.ts
│   │   ├── tmuxSocket.ts
│   │   ├── tokenBudget.ts
│   │   ├── tokens.ts
│   │   ├── toolErrors.ts
│   │   ├── toolPool.ts
│   │   ├── toolResultStorage.ts
│   │   ├── toolSchemaCache.ts
│   │   ├── toolSearch.ts
│   │   ├── transcriptSearch.ts
│   │   ├── treeify.ts
│   │   ├── truncate.ts
│   │   ├── unaryLogging.ts
│   │   ├── undercover.ts
│   │   ├── user.ts
│   │   ├── userAgent.ts
│   │   ├── userPromptKeywords.ts
│   │   ├── uuid.ts
│   │   ├── warningHandler.ts
│   │   ├── which.ts
│   │   ├── windowsPaths.ts
│   │   ├── withResolvers.ts
│   │   ├── words.ts
│   │   ├── workloadContext.ts
│   │   ├── worktree.ts
│   │   ├── worktreeModeEnabled.ts
│   │   ├── xdg.ts
│   │   ├── xml.ts
│   │   ├── yaml.ts
│   │   └── zodToJsonSchema.ts
│   ├── vim/
│   │   ├── motions.ts
│   │   ├── operators.ts
│   │   ├── textObjects.ts
│   │   ├── transitions.ts
│   │   └── types.ts
│   ├── voice/
│   │   └── voiceModeEnabled.ts
│   ├── commands.ts
│   ├── context.ts
│   ├── cost-tracker.ts
│   ├── costHook.ts
│   ├── dialogLaunchers.tsx
│   ├── history.ts
│   ├── ink.ts
│   ├── interactiveHelpers.tsx
│   ├── main.tsx
│   ├── projectOnboardingState.ts
│   ├── query.ts
│   ├── QueryEngine.ts
│   ├── replLauncher.tsx
│   ├── setup.ts
│   ├── Task.ts
│   ├── tasks.ts
│   ├── Tool.ts
│   └── tools.ts
└── vendor/
    ├── audio-capture-src/
    │   └── index.ts
    ├── image-processor-src/
    │   └── index.ts
    ├── modifiers-napi-src/
    │   └── index.ts
    └── url-handler-src/
        └── index.ts
```