#!/usr/bin/env python3
# flake8: noqa: E501
"""
Script to regenerate requirements.txt from pyproject.toml

Usage:
    python scripts/update_requirements.py
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Regenerate requirements.txt from pyproject.toml."""
    project_root = Path(__file__).parent.parent
    pyproject_file = project_root / "pyproject.toml"
    requirements_file = project_root / "deployment" / "requirements.txt"

    if not pyproject_file.exists():
        print("❌ pyproject.toml not found!")
        sys.exit(1)

    print("🔄 Regenerating requirements.txt from pyproject.toml...")

    try:
        # Run pip-compile
        subprocess.run(
            [
                "pip-compile",
                str(pyproject_file),
                "--output-file",
                str(requirements_file),
                "--upgrade",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        print("✅ requirements.txt generated successfully!")
        print(f"📁 Location: {requirements_file}")

        # Show what was generated
        with open(requirements_file, "r") as f:
            lines = f.readlines()
            dependency_count = len(
                [line for line in lines if line.strip() and not line.startswith("#")]
            )
            print(f"📦 Total dependencies: {dependency_count}")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating requirements.txt: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ pip-compile not found. Install with: " "pip install pip-tools")
        sys.exit(1)


if __name__ == "__main__":
    main()
