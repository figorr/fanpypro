#!/usr/bin/env bash
set -euo pipefail

version="$1"

# pyproject.toml
sed -i "s/^version = \".*\"/version = \"$version\"/" pyproject.toml

# manifest.json
jq --arg ver "$version" '.version = $ver' custom_components/fanpypro/manifest.json > tmp.json && mv tmp.json custom_components/fanpypro/manifest.json

# version.py
echo "__version__ = \"$version\"" > custom_components/fanpypro/version.py

rm -f tmp.json
