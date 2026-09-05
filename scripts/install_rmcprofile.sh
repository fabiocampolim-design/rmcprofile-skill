#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
# Create the conda env `rmcprofile` and register its Jupyter kernel (Linux/macOS/WSL).
# RMCProfile itself is not installed here: unpack the Linux tarball from
# https://rmcprofile.ornl.gov/download/ and export RMCPROFILE_HOME=<.../RMCProfile_package>.
# Usage: install_rmcprofile.sh [--dry-run] [--conda /path/to/conda]
DRY=0; CONDA="${CONDA:-conda}"
while [ $# -gt 0 ]; do case "$1" in --dry-run) DRY=1;; --conda) CONDA="$2"; shift;; *) echo "unknown arg $1"; exit 2;; esac; shift; done
HERE="$(cd "$(dirname "$0")" && pwd)"; YML="$HERE/../environment-rmcprofile.yml"
status=()
step() { echo "== $1"; echo "   $2"; if [ $DRY = 1 ]; then status+=("$1 : DRY-RUN"); return; fi
         if bash -c "$2"; then status+=("$1 : OK"); else status+=("$1 : FAIL"); printf '%s\n' "${status[@]}"; exit 1; fi; }
command -v "$CONDA" >/dev/null 2>&1 || { echo "FAIL: conda not found ($CONDA)"; exit 1; }
[ -f "$YML" ] || { echo "FAIL: $YML missing"; exit 1; }
step create-env      "$CONDA env create -f '$YML' -y"
step register-kernel "$CONDA run -n rmcprofile python -m ipykernel install --user --name rmcprofile-mc --display-name 'Python 3.12 (rmcprofile)'"
step verify-imports  "$CONDA run -n rmcprofile python -c 'import numpy, scipy, matplotlib, pytest; print(\"imports ok\")'"
if [ -n "$RMCPROFILE_HOME" ] && [ -x "$RMCPROFILE_HOME/exe/rmcprofile" ]; then status+=("rmcprofile-package : FOUND at $RMCPROFILE_HOME");
else status+=("rmcprofile-package : NOT FOUND (export RMCPROFILE_HOME; package-bound checks are skipped without it)"); fi
printf '%s\n' "${status[@]}"
