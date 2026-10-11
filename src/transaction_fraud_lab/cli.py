"""Offline JSON command-line interface."""

import argparse
import json
import sys
from pathlib import Path

from . import core
from .common import ContractError, read_json


def main(argv=None):
    parser = argparse.ArgumentParser(prog="fraud-lab")
    parser.add_argument("command", choices=["validate", "features"])
    parser.add_argument("input", type=Path)
    args = parser.parse_args(argv)
    try:
        value = read_json(args.input)
        if args.command == "validate":
            core.inspect(value)
            result = {"status": "valid_input", "scope": "initial_offline_component"}
        else:
            result = core.inspect(value)
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
        return 0
    except (ContractError, ValueError, OSError) as exc:
        message = str(exc) if isinstance(exc, ContractError) else "unreadable or invalid input"
        print(
            json.dumps({"status": "error", "code": "invalid_input", "message": message}),
            file=sys.stderr,
        )
        return 2
