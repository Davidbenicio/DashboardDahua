#!/bin/sh
set -e

# Upgrade packaging tools first to prefer wheels over source builds
python -m pip install --upgrade pip setuptools wheel

# Install requirements preferring binary wheels when available
python -m pip install --prefer-binary -r project/requirements.txt
