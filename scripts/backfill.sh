#!/bin/bash
set -e

# Backfill historical YC content
# Usage: bash scripts/backfill.sh [start-date]
# Example: bash scripts/backfill.sh 2020-01-01

START_DATE=${1:-"2020-01-01"}

echo "OpenYC Skills - Historical Backfill"
echo "Start date: $START_DATE"
echo ""

# Activate venv if not active
if [ -z "$VIRTUAL_ENV" ]; then
  source .venv/bin/activate
fi

python -m src.cli backfill --start-date "$START_DATE"
