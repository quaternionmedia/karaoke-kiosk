#!/usr/bin/env python3
"""Quick syntax check - compile all .py files."""

import py_compile
import sys
from pathlib import Path

errors = []
for py_file in Path("src").rglob("*.py"):
    try:
        py_compile.compile(str(py_file), doraise=True)
        print(f"✓ {py_file}")
    except py_compile.PyCompileError as e:
        print(f"✗ {py_file}: {e}")
        errors.append(str(py_file))

if errors:
    print(f"\n{len(errors)} file(s) with syntax errors")
    sys.exit(1)
else:
    print("\nAll files compiled successfully!")
    sys.exit(0)
