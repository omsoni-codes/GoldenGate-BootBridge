#!/bin/bash
# ==============================================================================
# GoldenGate-BootBridge: Universal x86_64 UEFI Bootloader Bridge Shell Interface
# Author: Om Soni (omsoni-codes)
# License: MIT License (c) 2026 Om Soni
# ==============================================================================
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
python3 "$DIR/bootbridge.py" "$@"
