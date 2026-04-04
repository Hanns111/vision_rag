# Regenera SANTO_GRIAL_PARA_CHATGPT.zip (ejecutar desde esta carpeta o con ruta absoluta).
$ErrorActionPreference = "Stop"
$here = $PSScriptRoot
$root = Resolve-Path (Join-Path $here "..")
$outZip = Join-Path $here "SANTO_GRIAL_PARA_CHATGPT.zip"
$stage = Join-Path ([System.IO.Path]::GetTempPath()) ("sg_chatgpt_" + [guid]::NewGuid().ToString("n"))
New-Item -ItemType Directory -Force -Path $stage | Out-Null
try {
    Copy-Item (Join-Path $here "SANTO_GRIAL_TODO_EN_UNO.md") (Join-Path $stage "00_LEE_PRIMERO_SANTO_GRIAL_TODO_EN_UNO.md") -Force
    Copy-Item (Join-Path $here "README.md") (Join-Path $stage "README_CONSOLIDADO_CARPETA.md") -Force
    Copy-Item (Join-Path $here "INSTRUCCIONES_CHATGPT.md") (Join-Path $stage "INSTRUCCIONES_CHATGPT.md") -Force
    Copy-Item (Join-Path $here "empaquetar_para_chatgpt.ps1") (Join-Path $stage "empaquetar_para_chatgpt.ps1") -Force
    $anaDst = Join-Path $stage "SANTO_GRIAL_ANALYSIS"
    robocopy (Join-Path $root "SANTO_GRIAL_ANALYSIS") $anaDst /E /XD node_modules .git __pycache__ .rag_cache /NFL /NDL /NJH /NJS /NC /NS | Out-Null
    $sbx = Join-Path $stage "agent_sandbox_python_audit"
    New-Item -ItemType Directory -Force -Path $sbx | Out-Null
    robocopy (Join-Path $root "agent_sandbox\CLAUDE_CODE_SOURCE_REFERENCE\AGENT_SANDBOX_SOURCE_FOR_AUDIT") $sbx /E /NFL /NDL /NJH /NJS /NC /NS | Out-Null
    if (Test-Path $outZip) { Remove-Item $outZip -Force }
    & tar.exe -a -c -f $outZip -C $stage .
    Write-Host "OK:" $outZip "(" ([math]::Round((Get-Item $outZip).Length / 1MB, 2)) "MB)"
}
finally {
    Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue
}
