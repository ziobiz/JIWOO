# 게임 에셋 → web/public/assets
$webRoot = Split-Path $PSScriptRoot -Parent
$repoRoot = Split-Path $webRoot -Parent
$src = Join-Path $repoRoot "붉은무공훈장\assets"
$dst = Join-Path $webRoot "public\assets"

if (-not (Test-Path -LiteralPath $src)) {
    Write-Host "[warn] source not found: $src"
    exit 1
}

New-Item -ItemType Directory -Force -Path $dst | Out-Null
Get-ChildItem -LiteralPath $src -File | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $dst -Force
}
$count = (Get-ChildItem -LiteralPath $dst -File).Count
Write-Host "[ok] $count files -> public/assets"
