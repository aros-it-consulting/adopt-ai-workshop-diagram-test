"""Runs the binaries of the build, all installed by mise (see mise.toml at the project root)."""

import os
import shutil
import subprocess
import sys


def find_tool(name):
    tool = shutil.which(name)
    if tool:
        return tool
    sys.exit(f"{name} is not on PATH. Run `mise install` at the project root.")


def run_tool(name, *arguments, **environment):
    """Runs one tool, the keyword arguments added to its environment, and stops the build if it fails."""
    command = [find_tool(name), *[str(argument) for argument in arguments]]
    child_environment = {**os.environ, **environment}
    result = subprocess.run(command, capture_output=True, text=True, env=child_environment)
    if result.returncode != 0:
        sys.exit(f"{name} failed.\n{result.stderr}")
