#!/bin/bash

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="${PROJECT_DIR}/venv"

if [ ! -d "${VENV_DIR}" ]; then
    python3 -m venv "${VENV_DIR}"
    "${VENV_DIR}/bin/pip" install --upgrade pip
    "${VENV_DIR}/bin/pip" install -r "${PROJECT_DIR}/requirements.txt" --break-system-packages
fi

source "${VENV_DIR}/bin/activate"
cd "${PROJECT_DIR}" || exit 1
python renovation_status.py

