# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
<#
.SYNOPSIS
  Create the conda env `rmcprofile` for rmcprofile-skill, register its Jupyter kernel,
  and check whether an RMCProfile package is reachable through RMCPROFILE_HOME.
.PARAMETER DryRun
  Print every command without executing it.
.PARAMETER Conda
  Path to conda.exe (default: %USERPROFILE%\miniconda3\Scripts\conda.exe).
.NOTES
  RMCProfile itself is not installed by this script: download the Windows package from
  https://rmcprofile.ornl.gov/download/ (SourceForge), unzip it, and set RMCPROFILE_HOME to
  the RMCProfile_package folder (the one that contains exe\ and tutorial\).
#>
param(
  [switch]$DryRun,
  [string]$Conda = "$env:USERPROFILE\miniconda3\Scripts\conda.exe"
)
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$yml  = Join-Path (Split-Path -Parent $here) "environment-rmcprofile.yml"
$py   = "$env:USERPROFILE\miniconda3\envs\rmcprofile\python.exe"
$steps = @()
function Step($name, $cmd) {
  Write-Host "== $name"
  Write-Host "   $cmd"
  if ($DryRun) { $script:steps += "$name : DRY-RUN"; return }
  Invoke-Expression $cmd
  if ($LASTEXITCODE -ne 0) { $script:steps += "$name : FAIL ($LASTEXITCODE)"; Write-Host ($script:steps -join "`n"); exit 1 }
  $script:steps += "$name : OK"
}
if (-not (Test-Path $Conda)) { Write-Host "FAIL: conda not found at $Conda (pass -Conda)"; exit 1 }
if (-not (Test-Path $yml))   { Write-Host "FAIL: $yml missing"; exit 1 }
Step "create-env"       "& `"$Conda`" env create -f `"$yml`" -y"
Step "register-kernel"  "& `"$py`" -m ipykernel install --user --name rmcprofile-mc --display-name `"Python 3.12 (rmcprofile)`""
Step "verify-imports"   "& `"$py`" -c `"import numpy, scipy, matplotlib, pytest; print('imports ok')`""
if ($env:RMCPROFILE_HOME -and (Test-Path (Join-Path $env:RMCPROFILE_HOME "exe\rmcprofile.exe"))) {
  $steps += "rmcprofile-package : FOUND at $env:RMCPROFILE_HOME"
} else {
  $steps += "rmcprofile-package : NOT FOUND (set RMCPROFILE_HOME to the RMCProfile_package folder; the skill works without it, package-bound checks are skipped)"
}
Write-Host ($steps -join "`n")
exit 0
