#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

make etl
make features
make bundle
