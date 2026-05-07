#!/bin/bash
set -e

echo "Building Cython extensions..."
cd "$(dirname "$0")/.."

python setup.py build_ext --inplace 2>/dev/null || \
    python -c "from Cython.Build import cythonize; from setuptools import setup, Extension; setup(ext_modules=cythonize(['sonic_gate/cython_modules/*.pyx'], compiler_directives={'language_level': '3'}), script_args=['build_ext', '--inplace'])"

echo "Cython build complete."
