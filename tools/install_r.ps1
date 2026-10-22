$ErrorActionPreference = "Stop"

$pre = "D:\prerequisite"
New-Item -ItemType Directory -Force -Path $pre | Out-Null

function Test-RScript {
    param([string]$exe)

    try {
        & $exe --version *> $null
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

function Find-GoodR {
    $roots = @(
        "C:\Program Files\R",
        "C:\Program Files (x86)\R",
        "D:\prerequisite\R",
        "D:\prerequisite\R-env"
    )

    foreach ($root in $roots) {
        if (Test-Path $root) {
            $files = Get-ChildItem -Path $root -Filter "Rscript.exe" -Recurse -ErrorAction SilentlyContinue
            foreach ($f in $files) {
                if ($f.FullName -match "conda_pkgs") { continue }
                if (Test-RScript $f.FullName) {
                    return $f.FullName
                }
            }
        }
    }

    return $null
}

Write-Host "[R] Searching for an existing working Rscript.exe..."
$existing = Find-GoodR
if ($existing) {
    Write-Host "[R] Found working R: $existing"
    exit 0
}

Write-Host "[R] No working standalone R found."

# Try winget first.
if (Get-Command winget -ErrorAction SilentlyContinue) {
    Write-Host "[R] Trying winget install RProject.R..."
    try {
        winget install --id RProject.R -e --accept-source-agreements --accept-package-agreements
        $existing = Find-GoodR
        if ($existing) {
            Write-Host "[R] winget installed working R: $existing"
            exit 0
        }
    } catch {
        Write-Warning "[R] winget failed: $_"
    }
} else {
    Write-Host "[R] winget is not available in this PowerShell context."
}

# Fallback: download official CRAN Windows installer.
Write-Host "[R] Downloading official CRAN Windows R installer to $pre ..."

$urlBase = "https://cloud.r-project.org/bin/windows/base/"
$html = (Invoke-WebRequest -Uri $urlBase -UseBasicParsing).Content

$m = [regex]::Match($html, "(R-[0-9.]+-win\.exe)")
if (-not $m.Success) {
    throw "Could not parse R installer filename from $urlBase"
}

$exeName = $m.Groups[1].Value
$installer = Join-Path $pre $exeName

Write-Host "[R] Installer: $exeName"
Write-Host "[R] Saving to: $installer"

Invoke-WebRequest -Uri ($urlBase + $exeName) -OutFile $installer -UseBasicParsing

Write-Host "[R] Installing R silently. If this requires admin rights, run Git Bash as Administrator and retry."
Start-Process -FilePath $installer -ArgumentList "/VERYSILENT","/SUPPRESSMSGBOXES","/NORESTART","/SP-" -Wait

$installed = Find-GoodR
if ($installed) {
    Write-Host "[R] Success. Working Rscript: $installed"
    exit 0
}

throw "R installer finished but no working Rscript.exe was found."
