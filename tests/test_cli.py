import json
from pathlib import Path

import pytest

from transaction_fraud_lab.cli import main
from transaction_fraud_lab.common import ContractError, read_json

ROOT = Path(__file__).resolve().parents[1]


def test_documented_command_emits_json(capsys):
    assert main(["features", str(ROOT / "examples/ordinary-history.case.json")]) == 0
    assert json.loads(capsys.readouterr().out)["schema_version"] == "0.1"


def test_invalid_file_exits_without_claiming_success(tmp_path, capsys):
    path = tmp_path / "invalid.json"
    path.write_text("{}")
    assert main(["features", str(path)]) == 2
    output = capsys.readouterr()
    assert not output.out
    assert json.loads(output.err)["status"] == "error"


def test_duplicate_json_keys_rejected(tmp_path):
    path = tmp_path / "duplicate.json"
    path.write_text('{"currency":"USD","currency":"INR"}')
    with pytest.raises(ContractError, match="duplicate JSON"):
        read_json(path)


def test_nonfinite_json_rejected(tmp_path):
    path = tmp_path / "invalid.json"
    path.write_text('{"amount_minor":NaN}')
    with pytest.raises(ContractError):
        read_json(path)
